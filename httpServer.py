import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket, test
from tornado import gen
import threading
from random import randint
import bitalino
import json
import connectionClass
import numpy
import os


#Bitalino configuration variables
macAddress = ""
acqChannels = []
samplingRate = 0
nSamples = 0
digitalOutput = []
labels = []
nStop = 0
port = 0
'''
This is a simple Websocket server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
''' 
threads = [] #Array with threads
contador = 0
device = ""
toStop = False
connections = [] #Clients that are connected

class WSHandler(tornado.websocket.WebSocketHandler):
	
	

	def check_origin(self, origin):
		return True

	def open(self):
		
		
		connections.append(connectionClass.Connection(self))
		print connections
		print 'New connection was opened'
		
		#self.write_message("Conn!")


	
	def on_message(self, message):
		if type(message) == unicode:
			print type(message)
			print message
			for val in connections:
				
				val.set_sizeScreen(message)
				
		self.write_message(message)
		
			


	def on_close(self):
		for val in connections:
			if val.get_connection():

				connections.remove(val)
		print 'Conn closed...'
		
		if len(connections) == 0:
			
			global toStop 
			toStop = True

		
def getJsonInfo():

	global macAddress
	global acqChannels
	global samplingRate
	global nSamples
	global digitalOutput
	global labels
	global nStop
	global port

	with open(os.path.dirname(os.path.realpath(__file__)) + '\\variables.json') as data_file:    
		data = json.load(data_file)
		for a in data :
			macAddress = a
			break
		for i in data[macAddress]["acqChannels"] :
			acqChannels.append(i-1)

		samplingRate =data[macAddress]["samplingRate"]
		nSamples = data[macAddress]["nSamples"]
		for i in data[macAddress]["digitalOutput"] :
			digitalOutput.append(int(i))
		for i in data[macAddress]["labels"] :
			labels.append(i)
		nStop = data[macAddress]["nStop"]
		port = data[macAddress]["port"]

def stopDevice():
	global device 
	if device.started :
		try:
			device.stop()
			device.close()
			device = ""
		except Exception as e:
			print e
	else:	
		device.close()
		device = ""

def read_function():
	global toStop
	global device
	global labels
	global contador
	global nStop
	
	while True:
		
		if toStop :
			if type(device) == bitalino.BITalino :
				stopDevice()
			toStop = False

		elif len(connections) >= 1:

			if not type(device) == bitalino.BITalino :
				
				try :
					
					device = bitalino.BITalino(macAddress)
					
					
				except Exception as e:
					print e
					[client.get_connection().write_message("Could not connect to Bitalino !") for client in connections]
					contador +=1
					if contador == nStop :
						stopDevice()
						tornado.ioloop.IOLoop.instance().stop()
						return;
				
			else :
				try:
					if not device.started :

						device.start(samplingRate,acqChannels)

						
					data = device.read(nSamples)
					
				
					for client in connections :
						
						if client.get_divider() != -1:
							data = data[::client.get_divider()]
							
						

						msg="{"
						
						for c in range(data[0].size):
							
							msg+="'"+labels[c]+"':"+str(data[:,c])+","
							
						msg=msg[:-1]+"}"
						msg = msg.replace("\n","")
						data = json.dumps(msg)
						
						client.get_connection().write_message(data)


				except Exception as e:
					
					print e
					[client.get_connection().write_message("Erro de coneccao") for client in connections]
					toStop = True
					contador +=1
					if contador == nStop :
						stopDevice()
						tornado.ioloop.IOLoop.instance().stop()
						return;


application = tornado.web.Application([
	(r'/ws', WSHandler),
])
 
#Starts the script
if __name__ == "__main__":
	getJsonInfo()
	
	http_server = tornado.httpserver.HTTPServer(application)
	http_server.listen(port)
	t = threading.Thread(target=read_function)
	threads.append(t)
	t.start()
	print "Server On"
	tornado.ioloop.IOLoop.instance().start()