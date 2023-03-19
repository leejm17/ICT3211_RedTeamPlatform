#!/bin/sh

# Description: This file/script demostrates the execution of SSH to a Windows Machine   

# sshpass -p 'toor' ssh toor@192.168.56.104 "ls; ls -la"
# sshpass -p 'Student12345@' ssh student@172.16.2.223 "whoami"
echo "Start"
sshpass -p 'Student12345@' ssh student@192.168.62.3 "C:\Users\Student\Desktop\SharedFolder\dashboardtest.exe"
echo "end"
# sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\dashboardtest.exe"