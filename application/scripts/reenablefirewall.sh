#!/bin/sh

# Description: This file/script would revert the firewall status of the affected Windows Host System
# Tag: Re-enable Windows Firewall    
sshpass -p 'Student12345@' ssh student@172.16.2.223 "C:\Users\Student\Desktop\SharedFolder\Compiled-Script\AttackScript.exe 10 1"
