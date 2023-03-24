# ICT3211_RedTeamPlatform
A Python-based Web application platform that integrates in-house exploits for a Smart Meter Network System.

# Pre-requisites
A Debian based Linux distro. Ubuntu is the recommended distro 
Python 3.8 is the recommended Python version.  

The below steps are pre-requisites to create a Python virtual environment with the Python version of 3.8:
```
apt install python3-virtualenv
sudo add-apt-repository ppa:deadsnakes/ppa
apt install python3.8
virtualenv --python="/usr/bin/python3.8" venv
```
Follwing that install the ssh pass utility which is required for the Python Flask Application to connect to the remote host without a password prompt
```
apt install sshpass
```

Follwing that run the below command to install the required libraries required to run the Python Flask libraries 
```
pip install -r requirements.txt 
```


