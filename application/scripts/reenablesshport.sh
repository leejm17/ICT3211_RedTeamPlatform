#!/bin/sh

# Description: This file/script would attempt to unblock the SSH port (22) on the Smart Meter Laptop 
# Tag: Re-enable SSH on Windows   
sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\Compiled-Script\AttackScript.exe 9 2"
