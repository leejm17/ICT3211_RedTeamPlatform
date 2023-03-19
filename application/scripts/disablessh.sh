#!/bin/sh

# Description: This file/script demostrates the disabling SSH (port 22) on the remote Windows Host System
# Tag: Block/Disrupt SSH port on Host Computer  
sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\Compiled-Script\AttackScript.exe 4"
