from flask_bootstrap import Bootstrap5
from flask import Flask, render_template, request

import subprocess
from subprocess import Popen, PIPE
import asyncio
import sys

from threading import Lock
from threading import Thread, Event
from flask import session, request
from flask_socketio import SocketIO, emit, disconnect

from random import random
from time import sleep
from queue import Queue
queue = Queue()
async_mode = None

# For looking sh files
import os
from os import listdir
from os.path import isfile, join


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
bootstrap = Bootstrap5(app)

socketio = SocketIO(app, async_handlers = False) # async_mode=async_mode)
thread = None
thread_lock = Lock()

#Random Number Generator Thread
thread = Thread()
thread_stop_event = Event()

event = Event()


# App routes
@app.route("/", methods=["GET"], endpoint="home")
def home_page():
    return render_template("/home.html")

@app.route("/attackdashboard", methods = ['POST', 'GET'])
def attack_dashboard():
    return render_template('attackdashboard.html')


def run_script(queue_in):
    p = subprocess.Popen(['./test.sh'], stdout=subprocess.PIPE, bufsize=1)
    for line in iter(p.stdout.readline, rb''):
        queue_in.put(str(line))
    p.stdout.close()
    p.wait()

    event.set()

def emit_script(queue_in):
    while True:
        if not queue_in.empty():
            line = queue_in.get()
            sleep(1)
            socketio.emit('newnumber', {'number': str(line)}, namespace='/test')
        if event.is_set():
            break
    print('Stop printing')


@socketio.on('connect', namespace='/test')
def trigger_recon():
    
    foo = request.args.get('foo')
    print(type(foo))
    
    # # need visibility of the global thread object
    # queue1 = Queue()
    # print('Client connected')

    # t = Thread(target=run_script, args=(queue1, ))
    # t.start()
    # t2 = Thread(target=emit_script, args=(queue1, ))
    # t2.start()

    # t.join()
    # t2.join()

    # print("jijiji")

    return

class RandomThread(Thread):
    def __init__(self):
        self.delay = 1
        super(RandomThread, self).__init__()
    def randomNumberGenerator(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print("Making random numbers")
        while not thread_stop_event.isSet():
            number = round(random()*10, 3)
            print (number)
            socketio.emit('newnumber', {'number': str(line)}, namespace='/test')
            sleep(self.delay)

    def run(self):
        self.randomNumberGenerator()


def ssh_script(queue_in):
    
    p = subprocess.Popen(['./ssh.sh'], stdout=subprocess.PIPE, bufsize=1)
    for line in iter(p.stdout.readline, rb''):
        queue_in.put(str(line))
    p.stdout.close()
    p.wait()

    sleep(5)
    event.set()

def emit_ssh(queue_in):
    while True:
        if not queue_in.empty():
            line = queue_in.get()
            print(line)
            socketio.emit('newnumber', {'number': str(line)}, namespace='/ssh')
        if event.is_set():
            break
    print('Stop printing')


@socketio.on('connect', namespace='/ssh')
def trigger_ssh():
    queue2 = Queue()
    print('Client connected for SSH')

    ssh_script_thread = Thread(target=ssh_script, args=(queue2, ))
    ssh_script_thread.start()
    ssh_emit_thread = Thread(target=emit_ssh, args=(queue2, ))
    ssh_emit_thread.start()

    ssh_script_thread.join()
    ssh_emit_thread.join()

    # print("jijiji")

    return

@app.route('/spyder', methods = ['POST', 'GET'])
def spyder():
    if request.method == "POST":
        print (request.form)
    
    return render_template('spyder.html') #, form=form)


@app.route("/getshfiles", methods=["GET"])
def get_sh_files():
	listOfshFiles = get_list_of_sh_files()
	return listOfshFiles

    # return "TESTING"

def get_list_of_sh_files():
    arr = []
    for file in  os.listdir():
         if file.endswith(".sh"):
             arr.append(file)
    print (arr)
    return arr



if __name__ == '__main__':
    socketio.run(app)

