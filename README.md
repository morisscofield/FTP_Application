## File Transfer Protocol Project

## Prerequisites
  * Python >= 3.8

1. To run the server, navigate to the `Server` directory in the terminal and run the following command: 
``` bash 
python3 mainServer.py
```
  * _**Note** start the server before starting the client_

2. To run the client, navigate to the `Client` directory in the terminal and run the following command:
``` bash
python3 mainClient.py
```
  * The server does not allow for the creation of new users. However the list of valid users can be found in the `Server/UserFiles` directory. 
  
  * The password for each user is located in the `Server/UserFiles/{User}/phrase.txt` file for each user.

  * The `Server/UserFiles/{User}/Files` directory contains all of a user's files and directories.

  * Files downloaded from the server are stored in the `Client/Transfers/FromServer` directory.

  * Files that are to be uploaded to the server must be placed in the `Client/Transfers/ToServer` directory first.
