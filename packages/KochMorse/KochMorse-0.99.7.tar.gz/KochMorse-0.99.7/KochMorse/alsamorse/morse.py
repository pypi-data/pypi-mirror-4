import alsaaudio
import struct
from math import sin, pi, ceil, floor
from threading import Thread, Event, Lock
import time
import logging

from wavwriter import WaveWriter


class Morse(Thread):
    """ This class implements the morse-engine. Instancing this class will 
        create a thread that does all the sound-io. This thread will initial 
        sleep untill Morse.pause(False) is called. You can reset the engine 
        into pause by calling Morse.pause(True). 

        Note; Since this class starts a new thread, you have to call 
        Morse.stop() to stop and join this thread.

        Morse can use anything that is iterratable as a char-source. """

    __morse_table = {'a':'.-',     'b':'-...',   'c':'-.-.',   'd':'-..',
                     'e':'.',      'f':'..-.',   'g':'--.',    'h':'....',
                     'i':'..',     'j':'.---',   'k':'-.-',    'l':'.-..',
                     'm':'--',     'n':'-.',     'o':'---',    'p':'.--.',
                     'q':'--.-',   'r':'.-.',    's':'...',    't':'-',
                     'u':'..-',    'v':'...-',   'w':'.--',    'x':'-..-',
                     'y':'-.--',   'z':'--..',   '0':'-----',  '1':'.----',
                     '2':'..---',  '3':'...--',  '4':'....-',  '5':'.....',
                     '6':'-....',  '7':'--...',  '8':'---..',  '9':'----.',
                     '.':'.-.-.-', ',':'--..--', '?':'..--..', "'":'.----.',
                     '!':'-.-.--', '/':'-..-.',  '(':'-.--.',  ')':'-.--.-',
                     '&':'.-...',  ':':'---...', ';':'-.-.-.', '=':'-...-',
                     '+':'.-.-.',  '-':'-....-', '_':'..--.-', '"':'.-..-.',
                     '$':'...-..-','@':'.--.-.'}
                    

    def __init__(self, frequency=750.0, speed=25.0, eff_speed=15.0, volume=0):
        """ The constructor takes 4 arguments. freqeucny specifies the 
            tone-frequency, speed the coding-speed, eff_speed the effective 
            conding-speed and volume the volumen in dB.

            @param frequency: Tone-frequence used in Hz. By default 750.0 Hz.
            @param speed: Coding-speed in WPM (words per minute). This 
                parameter specifies how fast a charater is send. The 
                pause-length between chars and words are defined by the 
                eff_speed parameter. 
            @param eff_speed: Effecive code speed in WPM. This speed defines 
                the length of the pauses between chars and words. This makes 
                it possible to train at full speed and have enougth time to 
                write chars down. 
            @param volume: Specifies the volume in dB. By default 0, which 
                means maximum."""
            
        self.__logger = logging.getLogger("kochmorse")
        self.__logger.info("Init morse with speed %s(%s), volume %s and freq %s"%(speed, eff_speed, volume, frequency))
        assert volume <= 0
        
        # call constructor
        Thread.__init__(self)

        # store attr:
        self.__frequency = float(frequency)
        self.__speed     = float(speed)
        self.__eff_speed = float(eff_speed)
        self.__volume    = 10.0**(float(volume)/20.0) * 32767.0

        self.__dit_sample = str()
        self.__da_sample  = str()
        self.__char_pause = str()
        self.__word_pause = str()

        # open alsa-pcm device for output:        
        self.__pcm = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, alsaaudio.PCM_NONBLOCK)
        #self.__pcm = WaveWriter("test.wav")

        self.__sample_rate = 48000.0

        self.__pcm.setchannels(1)
        self.__pcm.setrate(int(self.__sample_rate))
        self.__pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
     
        self.__sample_lock = Lock()
        self.__generate_samples()
 
        # thread stuff
        self.__running = True
        self.__pause = Event()

        self.__char_source = None
        self.__char_source_lock = Lock()
 
        self.__char_notifier = None
 
        # start thread
        self.start()
 

    def __generate_samples(self): 
        self.__sample_lock.acquire()
        
        # pre-calculate some stuff:
        omega = 2.0*pi*self.__frequency/self.__sample_rate  # jupp it is Omega
        period_len = 2.0*self.__sample_rate/self.__frequency    # period in frames

        # calculate sample-lengths: 
        self.__dit_len        = (60.0 * self.__sample_rate) / (50.0 * float(self.__speed))
        self.__dit_len        = int(floor(round(self.__dit_len/period_len)*period_len))
        self.__da_len         = (180.0 * self.__sample_rate) / (50.0 * float(self.__speed))
        self.__da_len         = int(floor(round(self.__da_len/period_len)*period_len))
        self.__char_pause_len = int(round((180 * self.__sample_rate) / (50.0 * float(self.__eff_speed))))
        self.__word_pause_len = int(round((480* self.__sample_rate) / (50.0 * float(self.__eff_speed))))
        self.__buffer_len     = self.__dit_len*2

        # calculate dit-sample:
        self.__dit_sample = str()
        w = 2.0*pi * self.__frequency/self.__sample_rate
        for i in range(self.__dit_len):  # calc sine tone
            if i <= period_len:
                value = float(i)/period_len * self.__volume*sin(omega * float(i))
            elif i >= self.__dit_len-period_len:
                value = float(self.__dit_len-i)/period_len * self.__volume * sin(omega * float(i))
            else:
                value = self.__volume * sin(omega * float(i))
            self.__dit_sample += struct.pack("<h", value)
        self.__dit_sample += struct.pack("<h", 0.0)*self.__dit_len

        #calculate da-sample:
        self.__da_sample = str()
        for i in range( self.__da_len ):
            if i <= period_len:
                value = float(i)/period_len * self.__volume*sin(omega * float(i))
            elif i >= self.__da_len-period_len:
                value = float(self.__da_len-i)/period_len * self.__volume * sin(omega * float(i))
            else:
                value = self.__volume * sin(omega * float(i))
            self.__da_sample += struct.pack("<h", value)
        self.__da_sample += struct.pack("<h", 0.0)*self.__dit_len

        # "calculate" pause-sample:
        self.__cpause_sample = struct.pack("<h", 0.0)*self.__char_pause_len
        self.__wpause_sample = struct.pack("<h", 0.0)*self.__word_pause_len

        # set buffer size:
        self.__pcm.setperiodsize(self.__buffer_len)
        self.__sample_lock.release()


    def run(self):
        """ Internal used method! This method will be called in a new threead 
            by the constructor. """
        # main thread-loop
        while self.__running:        
            self.__pause.wait()
            if not self.__running: return
            
            # if there is no ChararcterSource -> pause; continue     
            if not (hasattr(self.__char_source, "__iter__") or isinstance(self.__char_source, basestring)):
                self.__pause.clear()
                continue
   
            # lock source and get char from source
            self.__char_source_lock.acquire()

            # set framecount = 0
            self.__frame_counter  = 0

            for char in self.__char_source:
                # if " " send a word-pause
                if char == " ":
                    self._send_word_pause()

                # if char is in table -> send each symbol
                elif char in self.__morse_table.keys():
                    for sym in self.__morse_table[char]:
                        if sym == ".": 
                            self._send_dit()
                        elif sym == "-": 
                            self._send_da()
                    self._send_char_pause()
               
                # if char is not known
                else: 
                    self.__logger.warning("Unknown char '%s'"%char);  
                
                # it is importent to exit before calling __char_notifier
                # otherwise there will be a deadlock-if the GUI waits for
                # this thread to exit and self.__cahr_notifier waits for
                # the gui to went into idle 
                if not self.__running:
                    break 
 
                if hasattr(self.__char_notifier, "__call__"):
                    self.__char_notifier(char)

                if not self.__pause.isSet():
                    break

            # done, unlock source
            self.__char_source_lock.release() 

            # finnaly go into pause
            if self.__pause.isSet():
                self.__pause.clear()  


    def set_char_source(self, src):
        """ Defines the char source. A char-source can be any iteratable over 
            chars. 

            Note; If this method gets called while the engine is running, this
            method will set the engine into pause-mode and restart it after 
            the char-source was seted. This may reset the internal 
            frame-counter."""
        # save old pause-state
        is_set = self.__pause.isSet()
        # set thread into pause:
        self.__pause.clear()

        # reset char source
        self.__char_source_lock.acquire()
        self.__char_source = src
        self.__char_source_lock.release()

        #reset state    
        if is_set: self.__pause.set()                          


    def stop(self):
        """ Stops the engine. This method signals the thread to exit and waits
            for join. """
        self.__running = False
        if not self.__pause.isSet():
            self.__pause.set()
        time.sleep(0.00001)
        self.join()


    def is_running(self):
        """ Returns True if the thread is sill alife. """
        return self.__running

    
    def is_paused(self):
        """ Returns True if the thread is paused. """
        return not self.__pause.isSet()


    def set_pause(self, paused=True):
        """ This method pauses the thread or wakes it up. """
        if paused:
            self.__pause.clear()
        else:
            self.__pause.set()
        time.sleep(0.00001)


    def set_notifier(self, notifier):
        """ This method can be used to specifiy a callable, that will get each
            char right after it was send. """
        self.__char_notifier = notifier


    def set_volume(self, volume):
        """ Resets the volume. """
        assert volume <= 0
        self.__volume = 10.0**(float(volume)/20.0) * 32767.0
        self.__generate_samples()

    def set_speed(self, speed):
        """ Resets the speed of coding. """
        self.__speed = speed
        self.__generate_samples()

    def set_eff_speed(self, speed):
        """ Resets the effective coding speed. """
        self.__eff_speed = speed
        self.__generate_samples()

    def set_frequency(self, freq):
        """ Specifies the tone-frequency. """
        self.__frequency = freq
        self.__generate_samples()

    
    def get_framecount(self):
        """ Returns the number of frames send since the last wakeup.
            Each time the thread wakesup from pause this counter will be set 
            to 0. """
        return self.__frame_counter

    def get_time(self):
        """ Returns the elapsed seconds since last wakeup from pause-mode. """
        return self.__frame_counter / self.__sample_rate


    def _send_data(self, data): 
        """ internal used method to play the precalculated samples. """
        # XXX Sorry this code looks ugly but alsaaudio does not work well with
        # GUI apps if the PCM is opened with PCM_NORMAL (blocking). So i need 
        # to handle playback in PCM_NONBLOCK mode. Unless data is written into
        # the buffer, the thread will sleep the half time it takes to playback
        # the written data. If the buffer was full (l == 0) we sleep the half 
        # time to playback the whole buffer. (buffersize is determed by 
        # dit-len)
        
        idx = 0
        # unless all data was written
        while idx < len(data):
            l = 0
            while l == 0:   # while no data send:
                # lock sample and write data
                self.__sample_lock.acquire()
                l = self.__pcm.write(data[idx:])
                self.__sample_lock.release()
            
                # on error
                if l < 0:
                    self.__logger.error("Error while write to pcm")
                    return
                
                # time to play written data
                t = float(l)/self.__sample_rate 
            
                if t > 0:       
                    # if data was written: sleep the half time to play these 
                    time.sleep(t/2)
                else:
                    # else sleep a half dit-length
                    time.sleep(float(self.__dit_len)/(2.0*self.__sample_rate))
            # update counters 
            idx += l*2
            self.__frame_counter += l


    def _send_dit(self):
        self._send_data(self.__dit_sample)

    def _send_da(self):
        self._send_data(self.__da_sample)
   
    def _send_char_pause(self):
        self._send_data(self.__cpause_sample)

    def _send_word_pause(self):
        self._send_data(self.__wpause_sample)
