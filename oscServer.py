import OSC, threading, json,bitalino, numpy, os

#Config of Bitalino device
macAddress = "" 
acqChannels = []  
samplingRate = 0 
nSamples = 0 
digitalOutput = []

nStop = 0 #Number of tries to run the script, if the script doesn't work after the last try it closes itself
send_address = "",8888 #IP and port of the address we are sending data to
threads = [] #Array with threads
counter =  0 #Helps to count the number of tries 
device = "" #Current type of the device being used

#Gets the information from the variable.json file
def getJsonInfo():

  global macAddress
  global acqChannels
  global samplingRate
  global nSamples
  global digitalOutput
  global nStop
  global send_address

  with open(os.path.dirname(os.path.realpath(__file__)) + '/variables.json') as data_file:    
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
    nStop = data[macAddress]["nStop"]
    send_address = data[macAddress]["sendAddress"],data[macAddress]["port"]
    
#Simple send function for multiple arguments
def send_osc(addr, *stuff):
    msg = OSC.OSCMessage()
    msg.setAddress(addr)
    for item in stuff:
        msg.append(item)
    c.send(msg)

#Stops the device if called
def stopDevice():
  global device 
  if type(device) == bitalino.BITalino :
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

#Starts the device, receives the information from the device and sends that information to the address in the variable.json file
def read_function():
  global device
  global counter
  global nStop
  zeros = [float(0.0)] * 21
  
  while True:
    
    if not type(device) == bitalino.BITalino :
        
      try :

        device = bitalino.BITalino(macAddress)
        print "Connected to a device with the macAddress : " + str(macAddress)
        
      except Exception as e:
        print "Try number "+ str(counter +1) + " : " + str(e)
        device = ""
        counter +=1
        if counter == nStop : 
          print "Number of tries reached, something went wrong!"
          stopDevice()
          return;
          
    else :
      try:
        if not device.started :
          device.start(samplingRate,acqChannels)
        data = device.read(nSamples)
        for i in range(0,nSamples,5):
          send_osc("/0/raw", zeros)
          send_osc("/0/bitalino",data[i,:].astype('float'))

      except Exception as e:

        print "Try number "+ str(counter +1) + " : " + str(e)
        device = ""
        counter +=1
        if counter == nStop : 
          stopDevice()
          print "Number of tries reached, something went wrong!"
          return;

#Starts the script
if __name__ == "__main__":
  getJsonInfo()
  # Initialize the OSC client.
  c = OSC.OSCClient()
  c.connect(send_address)
  t = threading.Thread(target=read_function)
  threads.append(t)
  t.start()
  print "Sending data to " + str(send_address)
