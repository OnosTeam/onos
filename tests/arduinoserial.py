#!/usr/bin/env python
#
# Copyright 2007 John Wiseman <jjwiseman@yahoo.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
A port of Tod E. Kurt's arduino-serial.c.
<http://todbot.com/blog/2006/12/06/arduino-serial-c-code-to-talk-to-arduino/>
"""

import termios
import fcntl
import os
import sys
import time
import getopt


# Map from the numbers to the termios constants (which are pretty much
# the same numbers).

BPS_SYMS = {
  4800:   termios.B4800,
  9600:   termios.B9600,
  19200:  termios.B19200,
  38400:  termios.B38400,
  57600:  termios.B57600,
  115200: termios.B115200
  }


# Indices into the termios tuple.

IFLAG = 0
OFLAG = 1
CFLAG = 2
LFLAG = 3
ISPEED = 4
OSPEED = 5
CC = 6


def bps_to_termios_sym(bps):
  return BPS_SYMS[bps]

  
class SerialPort:

  def __init__(self, serialport, bps):
    """Takes the string name of the serial port
    (e.g. "/dev/tty.usbserial","COM1") and a baud rate (bps) and
    connects to that port at that speed and 8N1. Opens the port in
    fully raw mode so you can send binary data.
    """
    self.port=serialport
    self.fd = os.open(serialport, os.O_RDWR | os.O_NOCTTY | os.O_NDELAY)
    attrs = termios.tcgetattr(self.fd)
    bps_sym = bps_to_termios_sym(bps)
    # Set I/O speed.
    attrs[ISPEED] = bps_sym
    attrs[OSPEED] = bps_sym

    # 8N1
    attrs[CFLAG] &= ~termios.PARENB
    attrs[CFLAG] &= ~termios.CSTOPB
    attrs[CFLAG] &= ~termios.CSIZE
    attrs[CFLAG] |= termios.CS8
    # No flow control
    attrs[CFLAG] &= ~termios.CRTSCTS

    # Turn on READ & ignore contrll lines.
    attrs[CFLAG] |= termios.CREAD | termios.CLOCAL
    # Turn off software flow control.
    attrs[IFLAG] &= ~(termios.IXON | termios.IXOFF | termios.IXANY)

    # Make raw.
    attrs[LFLAG] &= ~(termios.ICANON | termios.ECHO | termios.ECHOE | termios.ISIG)
    attrs[OFLAG] &= ~termios.OPOST

    # It's complicated--See
    # http://unixwiz.net/techtips/termios-vmin-vtime.html
    attrs[CC][termios.VMIN] = 0;
    attrs[CC][termios.VTIME] = 20;
    termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
    os.system("cat "+self.port)
  def read_until(self, until):
    #print "called serial.read_until"
    buf = ""
    done = False
    while not done:
      n = os.read(self.fd, 1)
      if n == '':
        # FIXME: Maybe worth blocking instead of busy-looping?
        time.sleep(0.01)
        continue
      buf = buf + n
      if n == until:
        done = True
    os.close(n)
    return buf



  def read(self, size):
    #print "called serial.read"
    buf = ""

    #buf= os.read(self.fd, 1)
    buf=os.popen("cat < "+self.port).read()

    print "input buffer="+buf
    #os.close(n)
    return buf


  def read1(self, size):
    #print "called serial.read"
    buf = ""
    done = False
    while not done:
      n = os.read(self.fd, 1)
      if n == '':
        # FIXME: Maybe worth blocking instead of busy-looping?
        time.sleep(0.01)
        continue
      buf = buf + n
      if len(buf) == size:
        done = True
        return buf
    os.close(n)
    return buf


  def write(self, str):
     #os.write(self.fd, str)
     os.system("echo "+str+" >> "+self.port)

  def write_byte(self, byte):
    os.write(self.fd, chr(byte))

  def isOpen(self):
    print " called  isOpen"
    return(1)

  #def open():
  #  return(1)


 # def __del__(self):
 #   print "class arduinoserial destroyed"
 #   try:
 #     os.close(self.fd)
 #   except:
 #     print "tried to close serial port"
  def close(self):
    print "class arduinoserial destroyed"
    try:
      os.close(self.fd)
    except:
      print "tried to close serial port"


