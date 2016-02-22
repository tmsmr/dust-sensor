#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from flask import Flask
import subprocess as sp
import shlex
from string import Template
import datetime
from pprint import pprint
import ntplib
import RPi.GPIO as GPIO

DUSTSENSOR_CMD = 'sudo /home/pi/dustsensor/dustsensor'
MAX_TIME_DELTA = datetime.timedelta(seconds=5)
VALUES_LOG_FILE = '/home/pi/dustsensor/results.log'
VALUES = []
INDEX_TEMPL = '/home/pi/dustsensor/index.templ.html'

SERVO_PIN = 18
pwm = None

app = Flask(__name__)

@app.route('/')
def index():
        src = ''.join(open(INDEX_TEMPL).readlines())
        templ = Template(src)
        d = {'content': ''}
        d = fill_time(d)
        return templ.substitute(d)

@app.route('/measure')
def measure():
        servo(open=False)
        values = cmd_measure()
        servo(open=True)
        src = ''.join(open(INDEX_TEMPL).readlines())
        templ = Template(src)
        d = fill_time({})
        if values:
                VALUES.append((d['ntp'], values))
                logentry = '%s %sms %s%% %s' % (d['ntp'], values[0], values[1], values[2])
                with open(VALUES_LOG_FILE, 'a') as logfile:
                        logfile.write(logentry + '\n')
                d['content'] =logentry
        else:
                d['content'] = 'Invalid measurement'
        return templ.substitute(d)

@app.route('/list')
def list():
        src = ''.join(open(INDEX_TEMPL).readlines())
        templ = Template(src)
        d = fill_time({'content': ''})
        for measurement in VALUES:
                d['content'] += measurement[0]
                d['content'] += ' '
                d['content'] += '%sms %s%% %s' % (measurement[1][0], measurement[1][1], measurement[1][2])
                d['content'] += '<br />'
        return templ.substitute(d)


def fill_time(d):
        try:
                ntpclient = ntplib.NTPClient()
                response = ntpclient.request('pool.ntp.org')
                ntptime = datetime.datetime.fromtimestamp(response.tx_time)
                d['ntp'] = ntptime.strftime("%d.%m.%y %H:%M:%S")
                d['color'] = 'green'
        except:
                d['ntp'] = 'Invalid time'
                d['color'] = 'red'
        return d

def cmd_measure():
        try:
                cmd = shlex.split(DUSTSENSOR_CMD)
                p = sp.Popen(cmd, stdout=sp.PIPE)
                p.wait()
                stdout = p.stdout.read()
                if p.returncode != 0:
                        return None
                return stdout.strip().split(' ')
        except:
                return None

def servo(init=False, open=True):
        global pwm
        try:
                if init:
                        GPIO.setmode(GPIO.BCM)
                        GPIO.setup(SERVO_PIN, GPIO.OUT)
                        pwm = GPIO.PWM(SERVO_PIN, 50)
                        pwm.start(3)
                if open:
                        pwm.ChangeDutyCycle(10)
                else:
                        pwm.ChangeDutyCycle(3)
        except:
                pass


if __name__ == '__main__':
        servo(init=True, open=True)
        app.run(host='0.0.0.0', port='8080', threaded=True)
