#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import shutil
import RPi.GPIO as gpio
import time
import json


class USB:
    def __init__(self):
        self._usb_root = '/media/pi/'
        usb_list = os.listdir(self._usb_root)

        self.has_usb = False
        self.usb_pwd = None
        if len(usb_list) > 0:
            self.has_usb = True
            self.usb_pwd = f'{self._usb_root}{usb_list[0]}/'
    
    def get_mp3_list(self):
        file_list = os.listdir(self.usb_pwd)
        mp3_list = [file for file in file_list if file.endswith('.mp3')]
        return mp3_list
    
    def get_setting(self):
        with open(self.usb_pwd+'setting.txt', 'r') as json_file:
            setting = json.load(json_file)
        return setting

    def copy_setting(self, pwd):
        setting = self.get_setting()
        print(setting)
        with open(pwd+'setting.txt', 'w') as json_file:
            json.dump(setting, json_file)

    def has_setting(self):
        file_list = os.listdir(self.usb_pwd)
        if "setting.txt" in file_list:
            return True
        return False


class MP3FileManager:
    def __init__(self, mp3_pwd):
        self.mp3_pwd = mp3_pwd
    
    def all_delete(self):
        file_list = os.listdir(self.mp3_pwd)
        for file in file_list:
            os.remove(self.mp3_pwd+file)
    
    def copy(self, copy_pwd, copy_list):
        for copy in copy_list:
            shutil.copy(copy_pwd+copy, self.mp3_pwd+copy)
    
    def get_mp3_list(self):
        file_list = os.listdir(self.mp3_pwd)
        mp3_list = [file for file in file_list if file.endswith('.mp3')]
        mp3_list.sort()
        return mp3_list


class MicroSonicSencer:
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)

        gpio.setup(trig, gpio.OUT)
        gpio.setup(echo, gpio.IN)
    
    def __del__(self):
        gpio.cleanup()
    
    def get_distance_per_cm(self):
        # trig 0.5초간 low로 유지
        gpio.output(self.trig, False)
        time.sleep(0.5)

        # trig 0.00001초간 high로 만들어서 초음파 보냄
        gpio.output(self.trig, True)
        time.sleep(0.0001)
        gpio.output(self.trig, False)

        # echo가 true가 된 시간
        while gpio.input(self.echo) == False:
            pulse_start = time.time()
        
        #echo가 false가 된 시간
        while gpio.input(self.echo) == True:
            pluse_end = time.time()
        
        # high로 유지한 시간(왕복 시간)
        pulse_duration = pluse_end - pulse_start

        # 17000을 곱하여 무체와의 거리로 변환
        distance = pulse_duration * 17000

        # 소수점 2자리로 변환
        distance = round(distance, 2)

        return distance


class Trigger:
    def __init__(self, trig_value, size=4):
        self.size = size
        self.trig_value = trig_value
        self.clear()
    
    def clear(self):
        self.list = [9999 for _ in range(self.size)]
    
    def push(self, value):
        self.list.pop(0)
        self.list.append(value)
        return self.is_trig()
    
    def is_trig(self):
        avg = sum(self.list) / self.size
        if avg <= self.trig_value:
            return True
        return False


if __name__ == '__main__':
    usb = USB()
    print(usb.has_usb)
    if usb.has_usb:
        print(usb.usb_pwd)
        print(usb.get_mp3_list())
    
    MP3_PWD = '/home/pi/Desktop/auto_mp3/mp3/'

    manager = MP3FileManager(MP3_PWD)
    print(manager.get_mp3_list())
