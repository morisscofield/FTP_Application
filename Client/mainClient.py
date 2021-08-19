import getpass
from ClientPI import ClientPI
from ClientUI import ClientUI

print("Welcome to FTP!! Please enter connection details.")
print("Leaving fields blank will enter values shown in brackets.\r\n")
serverAddress = input("Server Address (127.0.0.1): ")

if serverAddress == "":
	serverAddress = "127.0.0.1"
serverPort = input("Port (12000): ")
if serverPort == "":
	serverPort = "12000"
client = ClientPI(serverAddress, int(serverPort))

if client.is_CMD_active():
	userName = input("User Name (Moris): ")
	if userName == "":
		userName = "Moris"
	password = getpass.getpass(prompt = "Password: ")
	if password == "":
		password = "NerdAlliance"
	client.login(userName, password)

if client.is_user_valid():
	ui = ClientUI()
	ui.initilise_client(client)
	ui.cmdloop()