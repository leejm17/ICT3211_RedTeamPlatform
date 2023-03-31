from flask import Flask, render_template, request, url_for, redirect, flash
from flask import session, request
from forms import UploadForm

# For executing sh files
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

# For looking sh files
import os
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

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
    
    # if ssh in filename, run script that add ssh rules to stop ssh connection
    if "ssh" in command:
        process = subprocess.Popen(["\"" +command+ "\""],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         shell=True,
                         encoding='utf-8',
                         errors='replace')
        sleep(5)
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
                    queue_in.put(realtime_output) 
                    queue_in.put("Connection timed out. Access to Smart Meter PC on port 22 has been blocked") 
                    queue_in.put("Ok.") 
    else:
        process = subprocess.Popen([command],  stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                            shell=True,
                            encoding='utf-8',
                            errors='replace')
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                queue_in.put("Ok.")
                break
            if realtime_output:
                # If the output from stdout is not empty, insert it into the shared queue queue_in
                queue_in.put(realtime_output.strip())
                if "timed out" in realtime_output or "not recognized" in realtime_output or "permission denied" in realtime_output or "cannot find the path specified" in realtime_output:
                    queue_in.put("Fail.")
                    break
                if "Fail." in realtime_output:
                    break 
                """
                # As realtime_output lines contain the string "Ok." with additional junk bytes,
                # an additional "Ok." is added into the queue for client browser to catch it.
                """
                if "Ok." in realtime_output:
                    queue_in.put("Ok.")
                    break   
    sleep(2)

    event.set()

def emit_script(queue_in, event):

    # While loop to constantly check if: 
    while True:
        """
        # if the queue is empty and if its not empty,
        # consume data from the queue and emit the line to client browser 
        """
        if not queue_in.empty():
            line = queue_in.get()
            eventlet.sleep(0)
            # Emit to browser client where socket event listener is socket.on(scriptoutput)
            socketio.emit('scriptoutput', {'number': str(line)}, namespace='/test')
        """
        # if event flag has been set by run_script thread
        # break out of while loop 
        """ 
        if event.is_set():
            break

    return


@socketio.on('connect', namespace='/test')
def trigger_attack():

    fileName = request.args.get('file')

    if not fileName.endswith(".sh"):
        socketio.emit('scriptoutput', {'number': str("File selected is not an sh file. Please try again")}, namespace='/test')
        socketio.emit('scriptoutput', {'number': str("Fail.")}, namespace='/test')
        return

    # Create Queue for the 2 threads to produce into and consume from
    attackIOQueue = eventlet.Queue()
    # Create event for subprocess to set event flags
    event = Event()
    
    # Create one thread to run subprocess to execute sh files 
    t = socketio.start_background_task(run_script, attackIOQueue, fileName, event)

    # Create another thread to emit output of subprocess to client browser
    t2 = socketio.start_background_task(emit_script, attackIOQueue, event)

    # Stop the thread once sub-process in emit_script is completed and event.set()
    t.join()
    t2.join()

    return

#===============================================Get Various Statuses=================================================#
#Thread to run subprocess to get status of FW, Win Defender and Kepserver
def get_statuses(queue_in, event):

    fileName = "getallstatus.sh"

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
            queue_in.put("Fail.")
            break
         # Insert all non-empty output into realtime_output array
        if realtime_output:
            realtime_output = realtime_output.replace('-', '')
            realtime_output = realtime_output.replace(':', '')
            output_stringlist.append(realtime_output.strip())
    
    if output_stringlist:
        """
        # If output_stringlist is not empty, invoke firewall_status function
        # to normalize data on the various statuses gathered from remote host
        """
        output = firewall_status(output_stringlist)
        queue_in.put(output)
        queue_in.put("Ok.")

    sleep(3)
    event.set()

    return

def emit_statuses(queue_in, event):
    while True:
        if not queue_in.empty():
            line = queue_in.get()
            # Emit to browser client where socket event listener is socket.on(statusoutput)
            socketio.emit('statusoutput', {'number': line}, namespace='/statuses')
        if event.is_set():
            break

    return


def firewall_status(stringlist):
    # Remove empty string from list
    stringlist = list(filter(None, stringlist))
    # Remove "OK." from stringlist to make array have even values as stringlist array has odd number of values
    stringlist.remove("Ok.")
    """
    # Lower case all items in stringlist array
    # as well as unwanted values such as state and <spaces>
    """
    stringlist = [line.lower() for line in stringlist]
    stringlist = [line.replace('state', ' ') for line in stringlist]
    stringlist = [line.replace(' ', '') for line in stringlist]

    # Convert values in stringlist array to dictionary with key-value pairs
    it = iter(stringlist)
    res_dct = dict(zip(it, it))  

    return res_dct

#Namespace to get status of FW, Win Defender and Kepserver
@socketio.on('connect', namespace='/statuses')
def trigger_recon():

    # Create event for subprocess to set event flags
    event = Event()
    # Create Queue for threads to produce into and consume from
    statusIOQueue = eventlet.Queue()

    # Create one thread to run subprocess to run sshpass 
    # and get various statuses of remote host
    t3 = socketio.start_background_task(get_statuses, statusIOQueue, event)

    # Create another thread to emit output of subprocess to client browser
    t4 = socketio.start_background_task(emit_statuses, statusIOQueue, event)

    # Stop the thread once sub-process in emit_status is completed and event.set()
    t3.join()
    t4.join()

    return

# ==================Route to get .sh files for user to run in attack dashboard===============================================#
@app.route("/getshfiles", methods=["GET"])
def get_sh_files():
	listOfshFiles = get_list_of_sh_files()
	return listOfshFiles

def get_list_of_sh_files():
    existing_dict = {}
    scriptDirectory = './scripts/'
    for file in os.listdir(scriptDirectory):
        
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
                    line = line.lstrip("Tag:")
                    existing_dict[file].append(line)
    
    return existing_dict

# ===========================================================================================================================#
# This route is responsible for handling .exe and .sh file uploads to the local filesystem
@app.route('/uploadfile', methods=['GET', 'POST'])
def file_upload():

    form = UploadForm()

    if form.validate_on_submit(): 
        # Get file upload data and its filename       
        f = form.upload.data
        filename = secure_filename(f.filename)

        if filename.endswith('.exe'):
            fullFileName = os.path.join('./executables/', filename)
            f.save(fullFileName)
            flash(u'.exe File has been uploaded', 'success')
        elif filename.endswith('.sh'):
            fullFileName = os.path.join('./scripts/', filename)
            f.save(fullFileName)
            flash(u'.sh File has been uploaded', 'success')
        else:
            flash(u'File submitted is not a .exe or .sh file', 'danger')

    return render_template('uploadfile.html', form = form)


# =====================================File Upload============================================================================ #
# Route is responsible for getting a list of .exe files uploaded to the local file system 
# and return it to uploadfile.html page on page load for Pen-tester to select
@app.route("/getexefiles", methods=["GET"])
def get_exe_files():
	listOfexeFiles = get_list_of_exe_files()
	return listOfexeFiles

def get_list_of_exe_files():
    existing_dict = {}
    executablesDirectory = './executables/'
    for file in  os.listdir(executablesDirectory):
        if file.endswith(".exe"):
            existing_dict[file] = []
    return existing_dict

# Route is responsible for uploadig .exe files selected to the Smart Meter PC remotely
@app.route('/remotefileupload', methods=['GET', 'POST'])
def remote_file_upload():
    if request.method == "POST":

        select = request.form.get('exe-select')
        fileDirectory = request.form.get('file-directory')
        fullFileName = os.path.join('./executables/', select)

        if not select.endswith(".exe"):
            flash(u'File selected does not end with exe', 'danger')
            return redirect(url_for('file_upload'))
        """
        # If user inputs a specific file directory for file upload to the Smart Meter PC,
        # append file directory to scp command
        """ 
        if fileDirectory != '':
            # strip any right trailing / or \ in directory name
            fileDirectory = fileDirectory.rstrip("\\")
            fileDirectory = fileDirectory.rstrip("/")

            # Append " and " to the directory name string for scp command
            fileDirectory = '"' +  fileDirectory.strip() + '"'

            command = 'sshpass -p "Student12345@" scp -o ConnectTimeout=5 ' + fullFileName + ' student@172.16.2.223:' + fileDirectory
        else:
            # If user does not input a specific a file directory for the Smart Meter PC,
            # default to using "C:\Users\student\Desktop\SharedFolder" directory in scp command
            command = 'sshpass -p "Student12345@" scp -o ConnectTimeout=5 ' + fullFileName + ' student@172.16.2.223:"C:\\Users\\student\\Desktop\\SharedFolder"'

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
                # if unable to upload the file to remote host, return error
                if "No such file or directory" in realtime_output:
                    flash(u'No such file or directory', 'danger')
                    break
                if "Connection timed out" in realtime_output:
                    flash(u'Unable to connect to remote host, connection timed out', 'danger')
                    break 

    return redirect(url_for('file_upload'))


#=========================================File Download===============================================#

@app.route('/remotefiledownload', methods=['GET', 'POST'])
def remote_file_download():

    if request.method == "POST":

        baseCommand = "sshpass -p \"Student12345@\" scp -o ConnectTimeout=5 -r student@172.16.2.223:"
        baseRemoteDirectory = '\"' +  "C:\\Users\\Student\\Documents\\AttackFolder" + '\"'
        baseLocalDirectory = '/root/testdownload'

        remoteFileDirectory = request.form.get('remote-file-directory')
        localFileDirectory = request.form.get('local-file-directory')
        # Strip submitted local and remote file directory of right trailing / and \
        remoteFileDirectory = remoteFileDirectory.rstrip("\\")
        remoteFileDirectory = remoteFileDirectory.rstrip("/")
        localFileDirectory = localFileDirectory.rstrip("\\")
        localFileDirectory = localFileDirectory.rstrip("/")

        # If user inputs a speific directory for both remote and local file directory
        if (remoteFileDirectory != '' and localFileDirectory != '') :
            remoteFileDirectory = '"' +  remoteFileDirectory.strip() + '"'
            command = baseCommand + remoteFileDirectory + ' ' + localFileDirectory            
        
        # If user only inputs a specific remote file directory
        elif (remoteFileDirectory != '' or localFileDirectory != '') :
            if remoteFileDirectory != '':
                remoteFileDirectory = '"' +  remoteFileDirectory.strip() + '"'
                command = baseCommand + remoteFileDirectory + ' ' + baseLocalDirectory

            # If user only inputs a specific local file directory
            if localFileDirectory != '':
                command = baseCommand + baseRemoteDirectory + ' ' + localFileDirectory

        # Default to default remote and local directory
        else:
            command =  baseCommand + baseRemoteDirectory + ' ' + baseLocalDirectory

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
                # If unable to connect to remote host or upload the file due to non-existent library, return error
                if "No such file or directory" in realtime_output:
                    flash(u'No such file or directory on remote host', 'danger')
                    break
                elif "Connection timed out" in realtime_output:
                    flash(u'Unable to connect to remote host, connection timed out', 'danger')
                    break

    return render_template('remotefiledownload.html')


if __name__ == '__main__':
    eventlet.monkey_patch()
    socketio.run(app)
