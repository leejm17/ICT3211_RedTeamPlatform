#!/bin/sh

# Description: This file/script would stop the Mod Bus Interrupt  
# Tag: Stop Mod Bus Interrupt  
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 11 7"
