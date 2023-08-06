#!/usr/bin/env python

"""\
Demo: handle incoming SMS messages by replying to them

Simple demo app that listens for incoming SMS messages, displays the sender's number
and the messages, then replies to the SMS by saying "thank you"
"""

from __future__ import print_function

import logging

PORT = '/dev/ttyUSB2'
BAUDRATE = 115200

from gsmmodem.modem import GsmModem

def handleSms(sms):
    print('== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n\n'.format(sms.number, sms.time, sms.text))
    print('Replying to SMS...')
    sms.reply('Thank you')
    print('SMS sent.\n')
    
def main():
    print('Initializing modem...')
    #logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(PORT, BAUDRATE, smsReceivedCallbackFunc=handleSms)
    modem.connect()
    print('Waiting for SMS message...')
    try:    
        modem.rxThread.join(2**31) # Specify a (huge) timeout so that it essentially blocks indefinitely, but still receives CTRL+C interrupt signal
    finally:
        modem.close();

if __name__ == '__main__':
    main()
