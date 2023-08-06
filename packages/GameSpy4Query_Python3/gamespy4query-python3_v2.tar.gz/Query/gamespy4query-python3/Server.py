""" This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>."""

#&----------------------------------------------------&
#& Server.py
#&----------------------------------------------------&
#& Author     : sifter
#& Pub.  Date : 10/31/2012
#& Affiliation: C5 - C5 Gaming (ARMA2 PVP Server and Clan)
#& Website    : http://www.c5gaming.com
#& Python Vers: > 3
#& 
#&----------------------------------------------------&
#& Required Python Version: 3<
#&   Standard Class "Server" to create a module that 
#&    queries gamming servers using Gamespy's UT3 
#&  protocol.
#&
#&----------------------------------------------------&


#IMPORTS (ALL Standard Libraries, included Player Class)
import time
import socket
import binascii
import struct




class Server:
    """The Server Information is simply a request with a package of data from the server.
    To get this data we must send two packages"""
    def __init__(self, server, port):
        """Initialize Server Class"""
        self.server_adress = server     #server adress (string)
        self.port          = port       #port          (intger)
        self.info          = dict()
        self._final_string = ''         #Used Internally, Contains Final Unparsed Data Returned from Server
        self.players = []               #list of players in Player Objects

   #---
   #Sequential Construct Methods (must be called in order)
    def query(self, timeout_secs = 5):
        """Query the Server to Return Server ".info" and ".players"
         Supply Timeout for connection, default is 5 seconds"""
        self._connect(timeout_secs)
        self._get_first_package()
        self._get_second_package()
        #Parse Data
        self._parse_recieved_data(self._final_string)
        self._close()

    #-query()-Incapsulated Sequential Constructon Methods for Parent query Method-    
    def _connect(self, timeout = 5):
        """Initial Socket Connection To Server"""
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #Create Socket
        self._socket.connect((self.server_adress, self.port))                  #Create connection to server
        self._socket.settimeout(timeout)                                #Initialize timeout for socket 


    def _get_first_package(self):
        self._response_one = self._send_data('FEFD0900000000')             #Send the first package and recieve (Request = string representing hex)
        #Parse First Package to Send Back
        self._response_one = str(self._response_one[0]).split('x00')        #Process data on first package 
        self._response_one = self._response_one[4]                          #Parse to get integer from first response
        self._response_one = self._response_one[:-1]                        #--
        self._response_one = int(self._response_one)                        #--capture integer
        self._response_one = struct.pack('>i', self._response_one)          #Convert int to signed big-endian bytecode
        self._response_one = binascii.hexlify(self._response_one)           #Big-Endian bytecode --> HEX
        self._response_one = str(self._response_one)                        #HEX --> string to package variable
        self._response_one = self._response_one[2:10]                       #Strip HEX string for simple HEX for transport
        self._response_one = self._response_one.upper()
                                                    #NEED find difference with FF000000
    def _get_second_package(self):
        """Send the Second Package and
            Recieve the Server Info"""
        request_two = 'FEFD00' + '00000000' + self._response_one + 'FF000001' 
        self.info = self._send_data(request_two)
        self._strip()  #Strip Splitnum to final string
        self._more_than_one()  

    #-_get_second_package()- Incapsulated  Methods for Parent _get_second_package Method-  
    def _strip(self):
        """Strip Second Response Splitnum and collect the data.
          We need to keep Concatenating Responses into final string for parsing"""
        self._final_string = self._final_string + str(self.info[0])[38:] #strip splitnums and Concatenate
        
    def _more_than_one(self):
        """Check if There are More Packages"""
        more = False
        if str(self.info[0][14:15])[4:6] == '00':    #Check Splitnums
            more = True                              #More Packages
        elif str(self.info[0][14:15])[4:6] == '80':
            more = False                             #No More Packages

        #Keep Talking If there are More Packages else move on
        if more == True:
            self._get_second_package()
        elif more == False:
            pass

    #-/_get_second_package()-        


    def _close(self):
        """Close Socket Connection"""
        self._socket.close()
    #-/query()-

   #---        
   #Internal Methods
    def _send_data(self,package):
        """Internal Use... Sends ByteCode to Server after
          Socket Connection and Recieve Package"""
        self._socket.send(binascii.unhexlify(package.encode()))
        package = self._socket.recvfrom(1400)                 #Recieve Reply
        return package


    def _parse_recieved_data(self, data): #input raw list 1 with server info in bytes
        info, playr   = self._seperate_info_players(data)   #Seperate Server Info and Player List 
        self.info     = self._server_info_dict(info)        #Create The Server info Dictionary
        self.players  = self._server_player_list(playr)     #Create Player List (List of Objects)

    #-_parse_recieved_data()-Incapsulated Methods for Parent _parce_recieved_data Method-  
    def _seperate_info_players(self, data):
        #seperate players and server info
        data = data.split('\\x01',1) #More than one responses = multiple x01
        #print(self._final_string) #Parsing Testing Here. Print Complete Info That is Parsed

        #Strip Byte Explosion (seperators)
        info = data[0].split('\\x00')
        playr = data[1].split('\\x00')
        return info, playr

    def _server_info_dict(self, info):
        #Combine List to Dictionary for server detail info   X02 Ends Package
        info.pop(0)  #Remove 1st Null Value in list Comming from Somewhere
        info.pop()   #Remove last Null Values (there are two) in list
        info.pop()     #--
        info = iter(info)
        info = dict(zip(info,info))
        return info

    def _server_player_list(self, playr):
        """Create list of Player Objects"""
        #Now Parse the Player info
        #Consider Breaking this up by Game

        #--ARMA2 TESTING RESULT COMMENTS BELOW--
        #Empty value at start of players_ empty at end
        #Empty value at start of score_  empty at end
        #Empty value at start of team_  empty at end
        #Empty value at start of deaths_ x2 empty at end
        #X02 Ends Package followed by empty value
        #--/

        list_of_players = [] #This is the Player List that will be returned
        #Holding Lists to Create Player Objects
        playerz = []
        score   = []
        team    = []
        deaths  = []

        #Now Parse the Player info
        list_to_use = ''
        for each in playr:
            if each == 'player_':
                list_to_use = 'playerz'
                continue
            elif each == 'score_':
                list_to_use = 'score'
                continue
            elif each == 'team_':
                list_to_use = 'team'
                continue
            elif each == 'deaths_':
                list_to_use = 'deaths'
                continue
            elif each == '':  #Remove Empties
                continue
            elif each.startswith('\'\\x01'):  #Multiple Packages carry  additional x01
                continue
            else:
                pass

            #Creating Seqential Lists of Stats
            if list_to_use == 'playerz':
                playerz.append(each)
            elif list_to_use == 'score':
                score.append(each)
            elif list_to_use == 'team':
                team.append(each)
            elif list_to_use == 'deaths':
                deaths.append(each)
        #ARMA2 Tested - Need to Remove Empty Player Values (see comments at line 145 - 150)
        only_player_name = False  #Assume its not ARMA2 Server Initially 
        try:
            deaths.pop()
            deaths.pop()
        except IndexError:   #Not ARMA2 Server if it did not have score,team,deaths
            only_player_name = True  #Only going to return Player Name
            pass

        x = 0
        #Combine Sequential List of Stats and Create Objects Here
        for each in playerz:
            if only_player_name == True:  #Probably Not ARMA2 Server: Only Create with Player Name
                list_of_players.append(Player(each))

            #elif only_player_name == False: #Tested with ARMA2 Servers: Playe, Score, Team, Deaths  #HAVE NOT GOT WORKING YET
                #list_of_players.append(Player(each, score[x], deaths = deaths[x])) #Need Team

            elif only_player_name == False: #Tested with ARMA2 Servers: Playe, Score, Team, Deaths
                list_of_players.append(Player(each)) #Need Team
            x = x + 1

            
        return list_of_players  #return the list of player Objects to Server Object list
    #-/_parse_recieved_data()-

    
   #---
   #Reuseable Methods
    def reset_server(self, server, port):
        #Reset Server Adress
        self.__init__(server, port)

#---------------------------------------------------------
#---------------------------------------------------------

class Player:
    """Player class"""
    def __init__(self, name, score= None, team = None, deaths = None):
        self.name   = name
        self.score  = score
        self.team   = team
        self.deaths = deaths





    
