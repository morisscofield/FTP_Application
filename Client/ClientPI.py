import socket
from ClientDTP import ClientDTP

class ClientPI():
	def __init__(self,serverIP,cmdPort):
		self.clientDTP = ClientDTP()
		self.username = None
		self.serverIP = serverIP
		self.clientIP = "127.0.0.1"
		self.cmdSocket = None
		self.cmdPort = cmdPort
		self.cmdIsActive = False
		self.userIsValid = False
		self.working_directory = None
		self.__open_connection()

	# Functions for managing connections
###################################################################################
	def __open_connection(self):
		try:
			self.cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.cmdSocket.connect((self.serverIP,self.cmdPort))
			response = self.__receive_command()
			if response[:3] == "220":
				self.cmdIsActive = True
			else:
				self.cmdIsActive = False
		except:
			self.cmdIsActive = False
			self.cmdSocket.close()
			print("Unable to establish control connection\r\n")

	def __receive_command(self):
		response = self.cmdSocket.recv(1024).decode()
		print(response)
		return response

	def __send_command(self,command,partial = True):
		if self.is_CMD_active():
			# print(command)
			self.cmdSocket.send(command.encode())
			response = self.__receive_command() 
			if partial:
				response = response[:3].strip()
			return response
		else:
			print("No control connection\r\n")
			return "000"

	def __data_connection(self):
		if self.clientDTP.is_passive():
			self.__passive_mode()
		else:
			self.__active_mode()

	def data_mode(self, mode):
		if mode == "active":
			self.clientDTP.data_mode(False)
			print("Now transferring in active mode\r\n")
		elif mode == "passive":
			self.clientDTP.data_mode(True)
			print("Now transfering in passive mode\r\n")
		else:
			print("Invalid mode")

	def is_CMD_active(self):
		return self.cmdIsActive

	def is_user_valid(self):
		return self.userIsValid

	# Functions for handling FTP commands
###################################################################################
	def login(self,username,password):
		if not self.userIsValid:
			response = self.__send_command("USER " + username + "\r\n")
			if response == "331":
				self.username = username
				response = self.__send_command("PASS " + password + "\r\n")
				if response == "230":
					self.userIsValid = True
			else:
				self.username = None
				self.userIsValid = False
		else:
			print("User is already logged in\r\n")

	def __passive_mode(self):
		if not self.clientDTP.is_data_established():
			response = self.__send_command("PASV\r\n", False)
			if response[:3] == "227":
				self.clientDTP.make_connection_passive(response)

	def __active_mode(self):
		if not self.clientDTP.is_data_established():
			self.clientDTP.listen_active(self.clientIP)
			response = self.__send_command("PORT " + 
			self.clientDTP.client_address_active(self.clientIP) + "\r\n")
			if response == "225":
				self.clientDTP.accept_connection_active()

	def server_os(self):
		self.__send_command("SYST\r\n")

	def download(self,fileName):
		self.__data_connection()
		if self.clientDTP.is_data_established():
			response = self.__send_command("RETR " + fileName + "\r\n")
			if response == "125":
				self.clientDTP.from_server(fileName)
				self.__receive_command()
		self.clientDTP.close_data()

	def upload(self,fileName):
		if not self.clientDTP.does_file_exist(fileName):
			print("Invalid file name\r\n")
			return
		self.__data_connection()
		if self.clientDTP.is_data_established():
			response = self.__send_command("STOR " + fileName + "\r\n")
			if response == "125":
				self.clientDTP.to_server(fileName)
				self.clientDTP.close_data()
				self.__receive_command()
		self.clientDTP.close_data()

	def close_connections(self):
		self.__send_command("QUIT\r\n")
		self.cmdSocket.close()
		self.clientDTP.close_data()
		self.cmdIsActive = False
		self.userIsValid = False

	def check_control(self):
		self.__send_command("NOOP\r\n")

	def binary_type(self):
		self.__send_command("TYPE I\r\n")

	def file_structure(self):
		self.__send_command("STRU F\r\n")

	def stream_mode(self):
		self.__send_command("MODE S\r\n")

	def present_working_directory(self):
		response = self.__send_command("PWD\r\n", False)
		index_start = response.find("/")
		index_end = len(response) - 3
		self.working_directory = response[index_start: index_end]

	def change_working_directory(self, dirPath):
		self.__send_command("CWD " + dirPath + "\r\n")

	def change_to_parent_directory(self):
		self.__send_command("CDUP\r\n")

	def make_directory(self, dirPath):
		self.__send_command("MKD " + dirPath + "\r\n")

	def remove_directory(self, dirPath):
		self.__send_command("RMD " + dirPath + "\r\n")

	def delete_file(self, filePath):
		self.__send_command("DELE " + filePath + "\r\n")

	def update_remote_directory_list(self):
		self.__data_connection()
		if self.clientDTP.is_data_established():
			response = self.__send_command("LIST\r\n")
			if response == "125":
				self.clientDTP.download_remote_list()
				self.__receive_command()
		self.clientDTP.close_data()

	def get_remote_directory_list(self):
		return self.clientDTP.get_remote_list()
