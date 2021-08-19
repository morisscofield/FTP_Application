import socket
import random
import os

class ClientDTP():
	def __init__(self):
		self.dataConn = None
		self.dataSocket = None
		self.dataPortUpper = None
		self.dataportLower = None
		self.dataPort = None
		self.isConnOpen = False
		self.isConnPassive = True
		self.bufferSize = 1024
		self.downloadsFolder = "Transfers/FromServer/"
		self.uploadsFolder = "Transfers/ToServer/"
		self.remoteList = []

	# Functions for establishing an active data connection
###################################################################################
	def __generate_data_port_active(self):
		self.dataPortUpper = str(random.randint(20,30))
		self.dataportLower = str(random.randint(0,255))
		self.dataPort = (int(self.dataPortUpper) * 256) + int(self.dataportLower)

	def client_address_active(self,address):
		address = address.split(".")
		address = ",".join(address)
		address = address + "," + self.dataPortUpper + "," + self.dataportLower
		return address

	def listen_active(self,ip):
		self.__generate_data_port_active()
		self.dataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.dataSocket.bind((ip,self.dataPort))
		self.dataSocket.listen(1)

	def accept_connection_active(self):
		self.dataConn,dataIP = self.dataSocket.accept()
		self.isConnOpen = True
		print("Successful active data connection\r\n")

	# Functions for establishing a passive data connection
###################################################################################
	def __extract_server_ip_passive(self,address):
		ip = address[0] + "." + address[1] + "." + address[2] + "." + address[3]
		return ip

	def __extract_server_port_passive(self,address):
		self.dataPortUpper = str(address[-2])
		self.dataportLower = str(address[-1])
		self.dataPort = (int(address[-2]) * 256) + int(address[-1])
		return self.dataPort

	def __extract_address(self,address):
		first = address.find("(") + 1
		second = address.find(")")
		address = address[first:second]
		address = address.split(",")
		return address

	def make_connection_passive(self,address):
		try:
			extracted_address = self.__extract_address(address)
			ip = self.__extract_server_ip_passive(extracted_address)
			port = self.__extract_server_port_passive(extracted_address)
			self.dataConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.dataConn.connect((ip,port))
			self.isConnOpen = True
			print("Successful passive data connection\r\n")
		except:
			print("Could not establish passive connection\r\n")
			self.close_data()

	# Functions for querying the data connection
###################################################################################
	def is_data_established(self):
		return self.isConnOpen

	def is_passive(self):
		return self.isConnPassive

	# Functions for managing the data connection
###################################################################################
	def data_mode(self,mode = True):
		if mode:
			self.isConnPassive = True
		else:
			self.isConnPassive = False

	def close_data(self):
		if self.isConnOpen and self.dataConn != None:
			self.dataConn.close()
			self.isConnOpen = False
			print("Terminating data connection\r\n")

	# Functions for querying the file system (get functions)
###################################################################################
	def does_file_exist(self,fileName):
		filePath = self.uploadsFolder + fileName
		if os.path.isfile(filePath):
			return True
		return False

	# Functions for data transfer to/from server
###################################################################################
	def from_server(self,fileName):
		file = open(self.downloadsFolder + fileName,"wb")
		data = self.dataConn.recv(self.bufferSize)
		while data:
			file.write(data)
			data = self.dataConn.recv(self.bufferSize)
		file.close()

	def to_server(self,fileName):
		file = open(self.uploadsFolder + fileName,"rb")
		data = file.read(self.bufferSize)
		while data:
			self.dataConn.send(data)
			data = file.read(self.bufferSize)
		file.close()

	def download_remote_list(self):
		listData = self.dataConn.recv(self.bufferSize).decode().rstrip()
		self.remoteList = []
		while listData:
			fileInfo = listData.split("\r")
			for item in fileInfo:
				item = item.strip().rstrip()
				self.__curate_list(item)
				listData = self.dataConn.recv(self.bufferSize).decode().rstrip()

	# Functions for managing the list of directory items
###################################################################################
	def __curate_list(self, item):
		temp = item.split()
		fileName = " ".join(temp[8:])
		fileSize = str(" ".join(temp[4:5])) + " Bytes"
		lastModified = " ".join(temp[5:8])
		permissions = " ".join(temp[0:1])
		tempList = [fileName, fileSize, lastModified, permissions]
		tempList = list(filter(None, tempList))
		self.remoteList.append(tempList)

	def get_remote_list(self):
		return self.remoteList
