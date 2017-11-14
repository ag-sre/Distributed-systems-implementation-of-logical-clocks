*******************************************************************
CSE5306: Distributed Systems							 Fall 2017
Project 2 - N-Node Distributed Systems 
Team Members:
Divya Kathirvel 		1001434576
Ankita Gandhi
********************************************************************

PART 1:

Language : Python
Uses : Python compile v2.7

This part emulates the Berkeley's algorithm to synchronize clocks.
1 Master and 2 Client
Master is connected at port 8000
Clients are connected at port 7000 and 9000

Step 1:
	Master sends its logical clock to all clients
Step 2:
	Clients recieve the message and send their own local clock to master
Step 3:
	Master applies Berkeley's algorithm to calculate average and the time difference 
	to be subtracted/added from each client and itself
Step 4:
	Sends the value for adjustment to client and master itself
Step 5:
	Client as well as master adjusts the clocks and synchronizes with each other

********************************************************************

PART 2:

