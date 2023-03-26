#!/bin/sh

# Description: This file/script demostrates the disabling of the COMPORT on the remote Windows Host System
# Tag: Disable COM Port   
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 7"
