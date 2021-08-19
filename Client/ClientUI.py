from ClientPI import ClientPI
from cmd import Cmd

class ClientUI(Cmd):
	def initilise_client(self, client):
		self.client = client
		self.client.server_os()
		self.client.stream_mode()
		self.client.file_structure()
		self.client.binary_type()
		self.client.present_working_directory()
		self.client.update_remote_directory_list()
		self.__print_directory_list()
		print("Type \'help\' to see the list of available functions and \'quit\' to exit\r\n")

	# Connection related functions
###################################################################################
	def do_check_control(self, inp):
		self.client.check_control()

	def do_data_mode(self, inp):
		self.client.data_mode(inp)

	def do_quit(self, inp):
		self.client.close_connections()
		return True

	# Documentation for connection related functions
###################################################################################
	def help_check_control(self):
		print("Confirm that the control connection is still active.\r\n")

	def help_data_mode(self):
		print("data_mode <mode>\r\n")
		print("Select whether data transfers are either active or passive.")
		print("Arguments: \'active\' or \'passive\' (case sensetive).\r\n")
	
	def help_quit(self):
		print("Close all connections and logout the user.\r\n")

	# Directory related functions
###################################################################################
	def do_directory_change(self, inp):
		self.client.change_working_directory(inp)
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	def do_directory_create(self, inp):
		self.client.make_directory(inp)
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	def do_directory_current(self, inp):
		self.client.present_working_directory()

	def do_directory_delete(self, inp):
		self.client.remove_directory(inp)
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	def do_directory_list(self, inp):
		self.__print_directory_list()

	def do_directory_parent(self, inp):
		self.client.change_to_parent_directory()
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	# Documentation for directory related functions
###################################################################################
	def help_directory_change(self):
		print("directory_change <path>\r\n")
		print("Change the current directory.")
		print("The path of the new directory can either be relative")
		print("to the root or relative to the current working directory.\r\n")

	def help_directory_create(self):
		print("directory_create <path>\r\n")
		print("Make a new directory within the current working directory.\r\n")

	def help_directory_current(self):
		print("Show the path of the current directory (PWD).\r\n")

	def help_directory_delete(self):
		print("directory_delete <path>\r\n")
		print("Delete a specified directory.\r\n")

	def help_directory_list(self):
		print("Show the contents of the current directory.\r\n")

	def help_directory_parent(self):
		print("Change the current directory to that of its parent.\r\n")

	# File related functions
###################################################################################
	def do_file_delete(self, inp):
		self.client.delete_file(inp)
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	def do_file_download(self, inp):
		self.client.download(inp)
		self.__print_directory_list()

	def do_file_upload(self, inp):
		self.client.upload(inp)
		self.client.update_remote_directory_list()
		self.__print_directory_list()

	# Documentation for file related functions
###################################################################################
	def help_file_delete(self):
		print("file_delete <path>\r\n")
		print("Delete a specified file.\r\n")

	def help_file_download(self):
		print("file_download <filename.extention>\r\n")
		print("Enter the name and file extention of the required file.")
		print("This only works for files in the current directory (PWD).")
		print("Files will be stored in the \"FromServer\" directory.\r\n")

	def help_file_upload(self):
		print("file_upload <filename.extention>\r\n")
		print("Enter the name and file extention of the required file.")
		print("This only works for files in the \"ToServer\" directory.")
		print("Files are uploaded to the server's current directory (PWD).\r\n")

	# Private functions
###################################################################################
	def __print_directory_list(self):
		data = self.client.get_remote_directory_list()
		dash = "-" * 80
		print(dash)
		print("{:<20s}{:<20s}{:<20s}{:<20s}".format("Name", "Size", "Date Modified", "Type"))
		print(dash)
		for i in range(len(data)):
			if data[i][3][0] == "d":
				data[i][3] = "directory"
			else:
				data[i][3] = "file"
			print("{:<20s}{:<20s}{:<20s}{:<20s}".format(data[i][0],data[i][1],data[i][2],data[i][3]))
		print("\r\n")