# ICT3211_RedTeamPlatform
A Python-based Web application platform that integrates in-house exploits for a Smart Meter Network System.

# Pre-requisites
As this dashboard was developed on WSL Ubuntu 22.04, Ubuntu is the recommended distro to run the Flask Application.
An alternative would be a Debian based Linux distro.

Python 3.8 is the recommended Python version.  

## Set-up on Ubuntu 22.04

The below steps are for setting up and running the Flask Web Application on Ubuntu specifically version 22.04. 

Firstly run the the update command to update repository sources using:
```
apt update
```

First, install the ssh pass utility which is required for the Python Flask Application to connect to the remote host without a password prompt
```
apt install sshpass
```

The below steps are pre-requisites to create a Python virtual environment with the Python version of 3.8:
```
apt install python3-virtualenv
sudo add-apt-repository ppa:deadsnakes/ppa
apt install python3.8
virtualenv --python="/usr/bin/python3.8" venv
```

## Set-up on Kali Linux
Firstly run the the update command to update repository sources using:
```
apt update
```

For Kali-Linux, download the Python3.8 package as Kali's repository does not store Python packages more than 2 version older than current version which is Python 3.11
```
https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tgz
```

After downloading the Python3.8 package, install the following requirments first
```
sudo apt-get install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
```

Then unpackage / extract the Python3.8 package, run the configuration script and compile the Python3.8 program
```
tar -xzvf Python-3.8.0.tgz
cd Python-3.8.0
./config
make && sudo make install
```

After compiling and installing, run below commands to get the installation folder of Python3.8
```
root@DESKTOP-ABC123:~/itp# whereis python3.8
or
root@DESKTOP-ABC123:~/itp# find / -iname "*python*" -type f 2>/dev/null
```

Then, install Python3 virtialenv and proceed to create a Python3.8 virtual environment with the folder name of venv
```
apt install python3-virtualenv
virtualenv --python="<python3.8 location in above step>" venv
```

# Running the Flask Application
Change directory into the venv folder created by the previous command 
```
cd venv
```

Then run the below command to activate the virtual environment
```
source bin/activate
```

An exmaple below shows how to determine if you are inside the virtual ennviroment
```
root@DESKTOP-ABC123:~/itp/secondredteamcode/venv# source bin/activate
(venv) root@DESKTOP-ABC123:~/itp/secondredteamcode/venv#
```

Then place the contents within the application folder into the /venv folder. The structure should look like this 
```
venv
├── bin
├── lib
├── executables
│   ├── thisisnotarealexecutable.exe  
│   └── ....exe
├── scripts
│   ├── 1.sh 
│   └── ...
├── static
│   ├── css 
│   └── js
├── templates 
│   ├── attackdashboard.html        
│   ├── base.html         
│   └── ........             
├── forms.py
├── app.py
└── requirements.txt
```

Once inside the virtual environment run the below command to install the required libraries required to run the Python Flask libraries 
```
pip install flask
pip install -r requirements.txt 
```

After installing the pre-requisite libraries execute the below command to start the Python Flask Server 
```
python -m flask run
```




