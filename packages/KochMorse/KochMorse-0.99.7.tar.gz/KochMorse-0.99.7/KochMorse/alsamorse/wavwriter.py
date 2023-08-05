import wave

class WaveWriter:
    def __init__(self, filename):
        self.__wav = wave.open(filename, "wb")
        
    def __del__(self):   
        self.__wav.close()
 
    def setchannels(self, channels):
        self.__wav.setnchannels(channels)

    def setformat(self, format):
        self.__wav.setsampwidth(2)

    def setrate(self, rate):
        self.__wav.setframerate(rate)

    def setperiodsize(self, period): pass

    def write(self, data):
        self.__wav.writeframes(data)
