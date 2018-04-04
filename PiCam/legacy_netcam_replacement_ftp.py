#!/usr/bin/python

import time
import picamera
import socket
import datetime
import ftplib

camera = picamera.PiCamera()
camera.resolution = (1280, 1024)
camera.start_preview()
time.sleep(2)

tmpfile = '/tmp/picam.jpg'
hostname = socket.gethostname().split('.')[0]

while True:
    camera.capture(tmpfile)
    seconds = datetime.datetime.today().strftime("%s")
    print seconds
    file = open(tmpfile,'rb')                  # file to send
    dest_file = hostname + '_' + seconds + '.jpg'
    session = ftplib.FTP('ftp.example.com','ftpuser','passw0rd')
    session.storbinary('STOR ' + dest_file, file)     # send the file
    file.close()                                    # close file and FTP
    session.quit()

    time.sleep(0.25)
