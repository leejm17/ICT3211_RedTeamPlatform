# from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request, url_for, redirect, flash
from flask import session, request
from forms import UploadForm
from multiprocessing import Process

import subprocess
from subprocess import Popen, PIPE
import asyncio
import sys

import threading
from threading import Lock
from threading import Thread, Event
from flask_socketio import SocketIO, emit, disconnect, send
import eventlet


from time import sleep
# from queue import Queue
# queue = eventlet.queue()

# For looking sh files
import os
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# bootstrap = Bootstrap5(app)

socketio = SocketIO(app)

# App routes
@app.route("/", methods=["GET"], endpoint="home")
def home_page():
    return render_template("/home.html")

@app.route("/attackdashboard", methods = ['POST', 'GET'])
def attack_dashboard():
    return render_template('attackdashboard.html')

def run_script(queue_in, fileName, event):
    
    command  ='./scripts/' + fileName
    print('Run script started')
    print("command: " + command)
    
    # if ssh in filename, run script that add ssh rules to stop ssh connection
    if "ssh" in command:

        # print("SSH File requested")
        process = subprocess.Popen(["\"" +command+ "\""],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         shell=True,
                         encoding='utf-8',
                         errors='replace')
        # kill the process as the process would hang infinitely
        process.kill()

        sleep(5)

        # run below command to check if conncetion to remote host would timesout due to the SSH rule in previous command
        testSSHCommand = "sshpass -p 'Student12345@' ssh -o ConnectTimeout=5 student@172.16.2.223"
        testSSHProcess = subprocess.Popen([testSSHCommand],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         shell=True,
                         encoding='utf-8',
                         errors='replace')
        # Use a while loop to continuosly retrive output of the command/subprocess
        while True:
            realtime_output = testSSHProcess.stdout.readline()
            if realtime_output == '' and testSSHProcess.poll() is not None:
                break
            if realtime_output:
                """
                # If the subprocess outputs the phrase "Connection Timed Out",
                # it means that the SSH port has been succesfully blocked on the remote host
                """
                if "Connection timed out" in realtime_output:
                    queue_in.put("Ok.") 
    else:
        process = subprocess.Popen([command],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            shell=True,
                            encoding='utf-8',
                            errors='replace')
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                # print("run_script realtime_output: ",realtime_output.strip(), flush=True)
                # If the output from stdout is not empty, insert it into the shared queue
                queue_in.put(realtime_output.strip())
                if "Connection timed out" in realtime_output or "not recognized" in realtime_output:
                    queue_in.put("Fail.")
                """
                # As realtime_output lines contain the string "Ok." with additional junk bytes,
                # an additional "Ok." is added into the queue for client browser to catch it.
                """
                if "Ok." in realtime_output:
                    queue_in.put("Ok.")
                    break   

    sleep(2)

    print("subprocess is done")

    event.set()

# @socketio.on("message")
# def handle_send(line):
    
#     # eventlet.sleep(0)
#     # socketio.sleep(0)

def emit_script(queue_in, event):
    print('Emit script started')

    # While loop to constantly check if: 
    while True:
        """
        # if the queue is empty and if its not empty,
        # consume data from the queue and emit the line to client browser 
        """
        if not queue_in.empty():
            line = queue_in.get()
            eventlet.sleep(0)
            socketio.emit('scriptoutput', {'number': str(line)}, namespace='/test')
            # print("emit_script output: ",line, flush=True)
        """
        # if event flag has been set by run_script thread
        # break out of while loop if event flag has been set
        """ 
        if event.is_set():
            print('Event is_set')
            break
        
    print('Emit script ended')

    return


@socketio.on('connect', namespace='/test')
def trigger_recon():

    # eventlet.monkey_patch(thread = True)

    print('Client connected')
    fileName = request.args.get('file')
    print("Filename is: ", fileName)

    # Create Queue for the 2 threads to produce into and consume from
    queue1 = eventlet.Queue()
    # Create event for subprocess to set event flags
    event = Event()
    
    # Create one thread to run subprocess to execute sh files 
    t = socketio.start_background_task(run_script, queue1, fileName, event)
    # t = threading.Thread(target=run_script, args=(queue1, fileName, event))
    # t.start()

    # Create another thread to emit output of subprocess to client browser
    t2 = socketio.start_background_task(emit_script, queue1, event)
    # t2 = threading.Thread(target=emit_script, args=(queue1, event))
    # t2.start()

    # Stop the thread once sub-process in emit_script is completed and event.set()
    t.join()
    t2.join()

    print("Thread Joined")

    return

#===============================================Get Various Statuses==================================#
#Thread to run subprocess to get status of FW, Win Defender and Kepserver
def get_statuses(queue_in, event):

    # fileName = "getallstatus.sh"
    fileName = "homegetallstatus.sh"
    print('Get_statuses script started')

    command  ='./scripts/' + fileName
    process = subprocess.Popen([command],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         shell=True,
                         encoding='utf-8',
                         errors='replace')

    output_stringlist = []
    while True:
        realtime_output = process.stdout.readline()
        if realtime_output == '' and process.poll() is not None:
            break
        if "Connection timed out" in realtime_output:
            print("Fail to get statuses")
            queue_in.put("Fail.")
            break
        if realtime_output:
            # print(realtime_output.strip(), flush=True)
            realtime_output = realtime_output.replace('-', '')
            realtime_output = realtime_output.replace(':', '')
            # Append ALL non-empty lines into an arraylist
            output_stringlist.append(realtime_output.strip())
    
    if output_stringlist: 
        output = firewall_status(output_stringlist)
        queue_in.put(output)
        queue_in.put("Ok.")

    sleep(3)

    print("subprocess is done")

    event.set()

    return

def emit_statuses(queue_in, event):
    print('Emit statuses script started')
    while True:
        if not queue_in.empty():
            line = queue_in.get()
            socketio.emit('statusoutput', {'number': line}, namespace='/statuses')
        if event.is_set():
            print('Event is_set')
            break
    print('Emit script ended')

    return


def firewall_status(stringlist):
    # Remove empty string from list
    stringlist = list(filter(None, stringlist))
    # Remove OK. from stringlist to make array have even values
    stringlist.remove("Ok.")
    
    # Lower case all items in stringlist array
    # as well as unwanted values such as state and <spaces>
    stringlist = [line.lower() for line in stringlist]
    stringlist = [line.replace('state', ' ') for line in stringlist]
    stringlist = [line.replace(' ', '') for line in stringlist]

    # Convert values in stringlist array to dictionary with key-value pairs
    it = iter(stringlist)
    res_dct = dict(zip(it, it))
    
    print (res_dct)

    return res_dct

#Thread to get status of FW, Win Defender and Kepserver
@socketio.on('connect', namespace='/statuses')
def trigger_recon():

    print('Client for status connected')
    # Create event for subprocess to set event flags
    event = Event()
    # Create Queue for threads to produce into and consume from
    queue2 = eventlet.Queue()

    # Create one thread to run subprocess to run sshpass 
    # and get various statuses of remote host
    t3 = socketio.start_background_task(get_statuses, queue2, event)
    # t3.start()

    # Create another thread to emit output of subprocess to client browser
    t4 = socketio.start_background_task(emit_statuses, queue2, event)
    # t4.start()

    t3.join()
    t4.join()

    print('Thread Joined')

    return

# ==================Route to get .sh files for user to run in attack dashboard==============================#
@app.route("/getshfiles", methods=["GET"])
def get_sh_files():
	listOfshFiles = get_list_of_sh_files()
	return listOfshFiles

def get_list_of_sh_files():
    existing_dict = {}
    scriptDirectory = './scripts/'
    for file in  os.listdir(scriptDirectory):
        
        if file.endswith(".sh"):
            filePath = scriptDirectory + file
            f = open(filePath, "r")
            Lines = f.readlines()

            existing_dict[file] = []

            for line in Lines:
                line = line.strip()
                line = line.lstrip('#')
                if "Description:" in line:
                    existing_dict[file].append(line)
                elif "Tag:" in line:
                    line = line.strip("Tag:")
                    existing_dict[file].append(line)
    
    return existing_dict

# ===========================================================================================================================#

@app.route('/uploadfile', methods=['GET', 'POST'])
def file_upload():
    form = UploadForm()
    if form.validate_on_submit():        
        f = form.upload.data
        filename = secure_filename(f.filename)
        print (filename)

        if filename.endswith('.exe'):
            fullFileName = os.path.join('./executables/', filename)
            f.save(fullFileName)
            flash(u'.exe File has been uploaded', 'success')
        elif filename.endswith('.sh'):
            fullFileName = os.path.join('./scripts/', filename)
            f.save(fullFileName)
            flash(u'.sh File has been uploaded', 'success')
        else:
            print ("not exe or sh")
            flash(u'File submitted is not exe or sh file', 'danger')

        print ("File saved")

    print ("Done")

    return render_template('uploadfile.html', form = form)


@app.route('/remotefileupload', methods=['GET', 'POST'])
def remote_file_upload():

    if request.method == "POST":

        select = request.form.get('exe-select')
        fileDirectory = request.form.get('file-directory')
        fullFileName = os.path.join('./executables/', select)
        print(fullFileName)
        if not select.endswith(".exe"):
            flash(u'File selected does not end with exe', 'danger')
            return redirect(url_for('file_upload'))

        # If user inputs a specific file directory,
        # append file directory to scp command
        if fileDirectory != '':
            print("Initial fileDirectory is: ", fileDirectory)
            fileDirectory = fileDirectory.rstrip("\\")
            print("stripped fileDirectory is: ", fileDirectory)
            fileDirectory = '"' +  fileDirectory.strip() + '"'
            command = 'sshpass -p "Student12345@" scp ' + fullFileName + ' student@172.16.2.223:' + fileDirectory
        else:
            # If user does not input a specific file directory,
            # default to using "C:\\Users\\student\\Desktop\\SharedFolder" directory in scp command
            command = 'sshpass -p "Student12345@" scp ' + fullFileName + ' student@172.16.2.223:"C:\\Users\\student\\Desktop\\SharedFolder"'

        # run scp command using popen and upload the file to the remote system
        process = subprocess.Popen([command],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            shell=True,
                            encoding='utf-8',
                            errors='replace')
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                flash(u'File Succesfully Uploaded to remote host', 'Success') 
                break
            if realtime_output:
                # print(realtime_output.strip(), flush=True)
                # if unable to upload the file to remote host, return error
                if "No such file or directory" in realtime_output:
                    flash(u'No such file or directory', 'danger')
                if "Connection timed out" in realtime_output:
                    flash(u'Unable to connect to remote host, connection timeout', 'danger') 

    return redirect(url_for('file_upload'))


@app.route("/getexefiles", methods=["GET"])
def get_exe_files():
	listOfshFiles = get_list_of_exe_files()
	return listOfshFiles

def get_list_of_exe_files():
    existing_dict = {}
    executablesDirectory = './executables/'
    for file in  os.listdir(executablesDirectory):
        if file.endswith(".exe"):
            existing_dict[file] = []
    return existing_dict
#=========================================================================================================================================#

@app.route('/remotefiledownload', methods=['GET', 'POST'])
def remote_file_download():

    if request.method == "POST":
        remoteFileDirectory = request.form.get('remote-file-directory')
        localFileDirectory = request.form.get('local-file-directory')


        # If user inputs a specific file directory,
        # .........
        if (remoteFileDirectory != '' and localFileDirectory != '') :
            remoteFileDirectory = remoteFileDirectory.rstrip("\\")
            remoteFileDirectory = remoteFileDirectory.rstrip("/")
            remoteFileDirectory = '"' +  remoteFileDirectory.strip() + '"'

            localFileDirectory = localFileDirectory.rstrip("\\")
            localFileDirectory = localFileDirectory.rstrip("/")
            command = 'sshpass -p "Student12345@" scp -r student@172.16.2.223:' + remoteFileDirectory + ' ' + localFileDirectory
            print("local+remoteFileDirectory != '' command is: ", command)

        elif remoteFileDirectory != '' or localFileDirectory != '':
            if remoteFileDirectory != '':
                remoteFileDirectory = remoteFileDirectory.rstrip("\\")
                remoteFileDirectory = remoteFileDirectory.rstrip("/")
                remoteFileDirectory = '"' +  remoteFileDirectory.strip() + '"'
                command = 'sshpass -p "Student12345@" scp -r student@172.16.2.223:' + remoteFileDirectory + ' /root/testdownload'
                print(" remoteFileDirectory != '' command is: " ,command)
            if localFileDirectory != '':
                localFileDirectory = localFileDirectory.rstrip("\\")
                localFileDirectory = localFileDirectory.rstrip("/")
                command = 'sshpass -p "Student12345@" scp -r student@172.16.2.223:"C:\\Users\\Student\\Documents\\AttackFolder"' + ' ' + localFileDirectory
                print("localFileDirectory != '' command is: " ,command)
            
        else:
            command = 'sshpass -p "Student12345@" scp -r student@172.16.2.223:"C:\\Users\\Student\\Documents\\AttackFolder" /root/testdownload'
            print("default command is: ", command)
        # run scp command using popen and upload the file to the remote system
        process = subprocess.Popen([command],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            shell=True,
                            encoding='utf-8',
                            errors='replace')
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                flash(u'Files has been successfully copied to local folder: ', 'success')
                break
            if realtime_output:
                # print(realtime_output.strip(), flush=True)
                # If unable to connect to remote host or upload the fsile, return error
                print(realtime_output, flush = True)
                if "No such file or directory" in realtime_output:
                    flash(u'No such file or directory on remote host', 'danger')
                    break
                elif "Connection timed out" in realtime_output:
                    flash(u'Unable to connect to remote host, connection timeout', 'danger')
                    break
            

    return render_template('remotefiledownload.html')


if __name__ == '__main__':
    eventlet.monkey_patch()
    socketio.run(app)
