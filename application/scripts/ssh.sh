#!/bin/sh

# Description: This file/script demostrates the execution of SSH to a Windows Machine   

# sshpass -p 'toor' ssh toor@192.168.56.104 "ls; ls -la"

# sshpass -p 'Student12345@' ssh student@192.168.62.3 "dir C:\Users\student\Downloads"
sshpass -p 'Student12345@' ssh student@192.168.62.3 "C:\Users\student\Downloads\dashboardTest2.exe 1"
# sshpass -p 'Student12345@' ssh student@192.168.62.3 "C:\Users\student\Downloads\dashboordTestnonewline.exe"

# sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\dashboardtest.exe"
# sshpass -p 'Student12345@' ssh student@172.16.2.223 "whoami"