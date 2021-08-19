import socket
import threading
from ServerDTP import ServerDTP

class ServerPI(threading.Thread):
	def __init__(self, name, serverIP, serverPort, cmdConn, addr):
		threading.Thread.__init__(self)
		self.name = name
		self.serverIP = serverIP
		self.cmdPort = serverPort
		self.cmdConn = cmdConn
		self.addr = addr
		self.serverDTP = ServerDTP()
		self.user = ""
		self.validUser = False
		self.isCmdActive = True
		self.possibleCommands = ["USER","PASS","PASV","PORT","SYST","RETR","STOR","QUIT",
		"NOOP","TYPE","STRU","MODE","PWD","CWD","CDUP","MKD","RMD","DELE","LIST"]
		self.noUserCommands = ["USER","NOOP","QUIT","PASS"]
		self.possibleUsers = ["Moris","Scofield","Mellan","Rey"]
		self.current_mode = "S"
		self.current_type = "I"

	# Functions for sending and receiving commands
###################################################################################
	def __send(self, message):
		print(message)
		self.cmdConn.send(message.encode())

	def __execute_command(self, command, argument):
		ftpFunction = getattr(self, command)
		if argument == "":
			ftpFunction()
		else:
			ftpFunction(argument)

	def __command_length(self, clientMessage):
		space_pos = clientMessage.find(" ")
		messageSize = 0
		if space_pos == -1:
			messageSize = len(clientMessage) - 2
		else:
			messageSize = space_pos

		return messageSize

	# Functions for the main server loop
###################################################################################
	def run(self):
		print(self.name + " connected to " + str(self.addr) + "\r\n")
		self.__send("220 Successful control connection\r\n")
		try:
			while self.isCmdActive:
				clientMessage = self.cmdConn.recv(1024).decode()
				print(clientMessage)
				cmdLen = self.__command_length(clientMessage)
				command = clientMessage[:cmdLen].strip().upper()
				argument = clientMessage[cmdLen:].strip()
				if not self.validUser and command not in self.noUserCommands:
					self.__send("530 Please log in\r\n")
					continue
				if command in self.possibleCommands:
					self.__execute_command(command, argument)
				else:
					self.__send("502 Command not implemented\r\n")
		except socket.error:
			print("Terminating control connection\r\n")
			self.isCmdActive = False
			self.cmdConn.close()
			self.serverDTP.close_data()

	# Functions for handling FTP commands
###################################################################################
	def USER(self, userName):
		if userName in self.possibleUsers:
			self.user = userName
			self.serverDTP.set_user(self.user)
			self.__send("331 Please enter password " + userName + "\r\n")
		else:
			self.validUser = False
			self.__send("332 Invalid user\r\n")

	def PASS(self, password = "phrase"):
		if self.user == "":
			self.__send("530 Please log in\r\n")
			return
		if self.serverDTP.is_password_valid(password):
			self.validUser = True
			self.__send("230 Welcome " + self.user + "\r\n")
		else:
			self.validUser = False
			self.__send("501 Invalid password\r\n")

	def PASV(self):
		try:
			self.serverDTP.listen_passive(self.serverIP)
			self.__send("227 Entering Passive connection mode " + 
			self.serverDTP.server_address_passive(self.serverIP) + "\r\n")
			self.serverDTP.accept_connection_passive()
		except:
			self.__send("425 Cannot open PASV data connection")
			self.serverDTP.close_data()

	def PORT(self, dataAddr):
		try:
			self.serverDTP.make_connection_active(dataAddr)
			self.__send("225 Active data connection established\r\n")
		except:
			self.__send("425 Unable to establish active data connection\r\n")
			self.serverDTP.close_data()

	def SYST(self):
		self.__send("215 UNIX\r\n")

	def RETR(self, fileName):
		if self.serverDTP.does_file_exist(fileName):
			try:
				self.__send("125 Sending " + fileName + " to client\r\n")
				self.serverDTP.begin_download(fileName)
				self.serverDTP.close_data()
				self.__send("226 Data transfer complete " + fileName + " sent to client\r\n")
			except:
				self.serverDTP.close_data()
				self.__send("426 Unable to send file to client\r\n")
		else:
			self.__send("450 Invalid file\r\n")
			self.serverDTP.close_data()

	def STOR(self, fileName):
		try:
			self.__send("125 Receiving " + fileName + " from client\r\n")
			self.serverDTP.begin_upload(fileName)
			self.serverDTP.close_data()
			self.__send("226 Data transfer complete " + fileName + " sent to server\r\n")
		except:
			self.serverDTP.close_data()
			self.__send("426 Unable to send file to server\r\n")

	def QUIT(self):
		self.__send("221 Terminating control connection\r\n")
		self.isCmdActive = False
		self.cmdConn.close()
		self.serverDTP.close_data()

	def NOOP(self):
		if self.isCmdActive:
			self.__send("200 Control connection OK\r\n")

	def TYPE(self, argument):
		argument = argument.upper()
		possibleArguments = ["A","I"]
		if argument in possibleArguments:
			if argument == "I":
				self.current_type = "I"
				self.__send("200 Binary (I) Type selected\r\n")
			else:
				self.current_type = "A"
				self.__send("200 ASCII (A) Type selected\r\n")
		else:
			self.__send("501 Invalid Type selected\r\n")

	def STRU(self, argument):
		argument = argument.upper()
		possibleArguments = ["F","R","P"]
		if argument in possibleArguments:
			if argument == "F":
				self.__send("200 File structure selected\r\n")
			else:
				self.__send("504 Only file structure supported\r\n")
		else:
			self.__send("501 Not a possible file structure\r\n")

	def MODE(self, argument):
		argument = argument.upper()
		possibleArguments = ["S","B","C"]
		if argument in possibleArguments:
			self.current_mode = "S"
			if argument == "S":
				self.__send("200 Stream mode selected\r\n")
			else:
				self.__send("504 Only stream mode supported\r\n")
		else:
			self.__send("501 Not a possible mode\r\n")

	def PWD(self):
		directory = "\"" + self.serverDTP.current_directory() + "\""
		self.__send("200 " + "Current working directory: " + directory + "\r\n")

	def CWD(self, dirPath = "/"):
		if dirPath == "..":
			self.CDUP()
			return
		if self.serverDTP.does_directory_exist(dirPath):
			self.serverDTP.change_directory(dirPath)
			directory = "\"" + self.serverDTP.current_directory() + "\""
			self.__send("250 Working directory changed to: " + directory + "\r\n")
		else:
			self.__send("501 directory does not exist\r\n")

	def CDUP(self):
		self.serverDTP.change_to_parent_directory()
		self.__send("200 " + "Working directory changed to: " + "\"" + self.serverDTP.current_directory() + "\"\r\n")

	def MKD(self, dirPath):
		if not self.serverDTP.does_directory_exist(dirPath):
			self.serverDTP.make_directory(dirPath)
			self.__send("257 Directory created" + "\r\n")
		else:
			self.__send("501 directory already exists\r\n")

	def RMD(self, dirPath):
		if self.serverDTP.does_directory_exist(dirPath):
			self.serverDTP.delete_directory(dirPath)
			self.__send("250 Directory deleted\r\n")
		else:
			self.__send("501 directory does not exist\r\n")

	def DELE(self, filePath):
		if self.serverDTP.does_file_exist(filePath):
			self.serverDTP.delete_file(filePath)
			self.__send("250 File deleted\r\n")
		else:
			self.__send("File does not exist\r\n")

	def LIST(self, dirPath = ""):
		if dirPath == "":
			dirPath = self.serverDTP.current_directory()
		if self.serverDTP.does_directory_exist(dirPath):
			try:
				self.__send("125 Sending file list\r\n")
				self.serverDTP.send_list(dirPath)
				self.serverDTP.close_data()
				self.__send("226 List successfully sent\r\n")
			except:
				self.serverDTP.close_data()
				self.__send("426 Unable to send list to client\r\n")
		else:
			self.serverDTP.close_data()
			self.__send("450 Invalid file path\r\n")

