import httpServer


class Connection:
	
	def __init__(self, conection):
		self.sizeScreen = 2750
		self.connection = conection
		self.macAddress = 0
		self.nSamples = server.nSamples
		

	def get_sizeScreen(self):
		return self.sizeScreen

	def set_sizeScreen(self,sizeScreen):
		self.sizeScreen = int(sizeScreen)

	def get_connection(self):
		return self.connection

	def get_divider(self):
		if self.nSamples <= self.get_sizeScreen():
			return -1
		else:
			return self.nSamples // self.get_sizeScreen()
