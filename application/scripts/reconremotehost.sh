#!/bin/sh

# Description: This file/script would Get Recon Info on the windows host
# Tag: Get Recon Info   
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\ReconScript.exe"
