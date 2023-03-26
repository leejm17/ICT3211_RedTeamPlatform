#!/bin/sh

# Description: This file/script would revert all changes
# Tag: Revert all changes to system    
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "cd \"C:\Windows\Temp\SmartMetertest\" && Attackscript.exe 11 10"
