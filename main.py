#!/usr/bin/python
# -*- coding: utf-8 -*-

from playsound import playsound
from datetime import datetime
from subprocess import call
import json
import time

from util import USB, MP3FileManager, MicroSonicSencer, Trigger



#**************************************
# 공용 상수 초기화
#**************************************
MP3_PWD = '/home/pi/Desktop/auto_mp3/mp3/'
TTS_PWD = '/home/pi/Desktop/auto_mp3/tts/'
ROOT_PWD = '/home/pi/Desktop/auto_mp3/'



#**************************************
# setting.txt에서 설정을 가져와 초기화를 한다.
#**************************************
setting = None
with open(ROOT_PWD+'setting.txt', 'r') as json_file:
    setting = json.load(json_file)
print(setting)

# 라즈베리파이 초기화를 기다리기 위해서 지연을 준다.
time.sleep(setting['init_delay'])

# mp3 실행 거리 설정 (단위: cm)
TRIG_DISTANCE = setting['distance']



#**************************************
# 공용 변수 초기화
#**************************************
usb = USB()
manager = MP3FileManager(MP3_PWD)
sensor = MicroSonicSencer(13, 19)
trigger = Trigger(TRIG_DISTANCE, 4)



#**************************************
# USB가 연결되어 있는지 확인하고, mp3와 setting을 복사한다.
# USB가 연결되어 있으면 무조건 라즈베리파이 종료가 발생한다.
#**************************************
if usb.has_usb:
    playsound(TTS_PWD+"유에스비 감지하였습니다.mp3")

    # setting.txt이 있는지 확인하고 복사한다.
    if usb.has_setting():
        usb.copy_setting(ROOT_PWD)

    # mp3 파일이 있는지 확인하고 복사한다.
    mp3_list = usb.get_mp3_list()
    if len(mp3_list) == 0:
        playsound(TTS_PWD+"유에스비에 엠피쓰리 파일이 없습니다.mp3")
    else:
        playsound(TTS_PWD+"엠피쓰리복사를 시작합니다.mp3")
        manager.all_delete()
        manager.copy(usb.usb_pwd, mp3_list)
        playsound(TTS_PWD+"엠피쓰리복사가 끝났습니다.mp3")
    playsound(TTS_PWD+"라즈베리파이를 종료합니다 종료가 완료되면 유에스비를 제거해주세요.mp3")
    # 종료 명령
    call("sudo nohup shutdown -h now", shell=True)
    exit()



#**************************************
# 무한반복을 시작하고, 초음파 센서에 물체의 거리를 측정한다.
# 측정된 거리의 평균이 TRIG_DISTANCE보다 작으면 mp3를 실행한다.
#**************************************
playsound(TTS_PWD+"초기화를 끝냈습니다.mp3")

while True:
    dis = sensor.get_distance_per_cm()
    print(f'{datetime.now()} - {dis}')
    if trigger.push(dis):
        trigger.clear()
        for mp3 in manager.get_mp3_list():
            playsound(MP3_PWD+mp3)
