#!/usr/bin/python

from distutils.core import setup

desc = """ Morse-tutor for Linux using the Koch-method. """

long_desc = """ This morse-tutor/trainer uses the Koch-method which is known to
be the fastest way to learn morse-code. 

KochMorse has a modern, easy to use Gtk2 user-interface. It also uses 
alsaaudio for sound-output."""

setup ( name = 'KochMorse',
        version = '0.99.7',
        description = desc,
        long_description = long_desc,
        author = 'Hannes Matuschek',
        author_email = 'hmatuschek@gmail.com',
        url = 'http://kochmorse.googlecode.com',

        classifiers = ['Development Status :: 5 - Production/Stable',
                       'Environment :: X11 Applications :: GTK',
                       'Intended Audience :: Education',
                       'Intended Audience :: End Users/Desktop',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Operating System :: POSIX :: Linux',
                       'Programming Language :: Python',
                       'Topic :: Communications :: Ham Radio'], 

        packages = ['KochMorse','KochMorse.alsamorse'],
        requires = ['alsaaudio'],
        scripts = ['kochmorse'],
        package_data = {'KochMorse' : ['*.glade']},
        
        data_files = [('/usr/share/applications',['kochmorse.desktop']),
                      ('/usr/share/KochMorse',   ['icon.svg']),
                      ('/usr/share/KochMorse/i18n', ['i18n/KochMorse.pot', 'i18n/de_DE.po']),
                      ('/usr/share/KochMorse/i18n/de/LC_MESSAGES', ['i18n/de/LC_MESSAGES/KochMorse.mo']) ] )                
