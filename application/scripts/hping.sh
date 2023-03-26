#!/bin/sh

# Description: This file/script demostrates reconnaisance of the network/Windows Machine
# Tag: Recon      
hping3 -S --flood -V -p 22 172.16.2.223
echo "Success"