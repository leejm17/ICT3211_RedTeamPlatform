#!/bin/sh

# Description: This file/script would kill the keylogger initiated on the Smart Meter PC
# Tag: Kill Keylogger   
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 11 9"
