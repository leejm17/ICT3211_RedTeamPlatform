#!/bin/sh

# Description: This file/script demostrates the disabling SSH (port 22) on the remote Windows Host System through the Windows Firewall
# Tag: Block/Disrupt SSH port on Host Computer  
sshpass -p 'Student12345@' ssh student@172.16.2.223 -o ConnectTimeout=5 "C:\Windows\Temp\SmartMetertest\AttackScript.exe 4"
