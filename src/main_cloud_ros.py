#!/usr/bin/env python

import roslib; roslib.load_manifest('cloud_ros')
import rospy
from cloud_ros.srv import *
from std_msgs.msg import String
from pySpacebrew.spacebrew import Spacebrew
import rosgraph.masterapi

import rostopic 
from rostopic import rostopicFunctions

import rosservice
from rosservice import rosserviceFunctions

import rosrun
from rosrun import rosrunFunctions

import roscommands
from roscommands import rosCommandsFunctions

import subprocess
import threading

import sys, tty, termios

import json
import time

def enviar(req):

	global start_time
	start_time = time.time()
	
	global brew

	comando = req.comando.split(" ")

	if(comando[0] == "rostopic"):
		rostopicFunctions(req.comando, brew)
	elif(comando[0] == "rosservice"):
		rosserviceFunctions(req.comando, brew)
	elif(comando[0] == "rosrun"):
		rosrunFunctions(req.comando, brew)
	elif(comando[0] == "roscommands"):
		rosCommandsFunctions(req.comando, brew)
	else:
		rospy.logwarn("Sintaxe do comando incorreta")

def recebido(data):
	global brew
	global start_time

	if data['acao']=="enviar" and data['comandoRos']=='rostopic':
		method = getattr(rostopic, data['funcao'])
		result = method(brew, data['topic'], data['freq'], data['ip'])
	elif data['acao']=="enviar" and data['comandoRos']=='rosservice':
		method = getattr(rosservice, data['funcao'])
		result = method(brew, data['service'], data['args'])
	elif data['acao']=="enviar" and data['comandoRos']=='rosrun':
		method = getattr(rosrun, data['funcao'])
		result = method(brew, data['package'], data['executable'], data['parameters'])
	elif data['acao']=="enviar" and data['comandoRos']=='roscommands':
		method = getattr(roscommands, data['funcao'])
		result = method(brew, data['commands'])
	else:
		rospy.logwarn("no else")
		rospy.logwarn(data['title']+"\n"+data['dados'])

	#print("--- %s seconds ---" % (time.time() - start_time))

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
	
	global brew

	while(True):
		orig_settings = termios.tcgetattr(sys.stdin)
		tty.setcbreak(sys.stdin)
		#tty.setraw(sys.stdin)
		ch=sys.stdin.read(1)[0]

		if(ch == 'A'):
			comm = "up"
		elif(ch == 'B'):
			comm = "down"
		elif(ch == 'C'):
			comm = "right"
		elif(ch == 'D'):
			comm = "left"
		else:
			comm = ""

		if(comm != ""):
			rosCommandsFunctions(comm, brew)

def cloud_ros():
	name = "rosPy Example"
	server = "sandbox.spacebrew.cc"
	#server = "200.131.135.146"
	
	global brew

	brew = Spacebrew(name=name, server=server)
	brew.addPublisher("Publisher")
	brew.addSubscriber("Subscriber")

	try:
		# start-up spacebrew
		brew.start()
		brew.subscribe("Subscriber", recebido)

		thread2 = myThread(1, "Thread-2", 1)
		thread2.start()
	finally: 
		rospy.init_node('cloud_ros_node')
		rospy.loginfo("cloud_ros node is up and running!!!")

	s = rospy.Service('send_data', Comando, enviar)
	s2 = rospy.Service('move_alone', Comando, move)

	rospy.spin()

if __name__ == '__main__':
	cloud_ros()

