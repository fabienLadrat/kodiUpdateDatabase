#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import os

class movie:

    def __init__(self, idFile, played):
        self.idFile = idFile
        self.played = played

class bookmark:

    def __init__(self, idFile, timeInSeconds, totalTimeInSeconds, thumbNailImage, player, playerState, type):
        self.idFile = idFile
        self.timeInSeconds = timeInSeconds
		self.totalTimeInSeconds = totalTimeInSeconds
		self.thumbNailImage = thumbNailImage
		self.player = player
		self.playerState = playerState
		self.type = type
		
databaseChambre = "/tmp/remote_database_dir/Database/MyVideos90.db"
databaseSalon = '/storage/.kodi/userdata/Database/MyVideos90.db'
#new /storage/.kodi/userdata/Database/MyVideos90.db
#old (gotham) /storage/.xbmc/userdata/Database/MyVideos78.db
path = "/tmp/remote_database_dir"

if os.path.exists(path) == False:
	os.popen("mkdir -p /tmp/remote_database_dir")
	os.popen("mount -t cifs //192.168.0.15/userdata -o user=root -o pass=openelec /tmp/remote_database_dir")

con = None
conC = None

# connexion rpi Chambre
conC = lite.connect(databaseChambre)
#print "Opened database successfully";
curC = conC.cursor()    

# connexion rpi Salon
con = lite.connect(databaseSalon)
#print "Opened database successfully";
cur = con.cursor()  

# get movie seen
curC.execute("SELECT f.idFile as nbVue FROM files f where f.playCount <> 0")
data = curC.fetchall()

for row in data:
	#print row[0].encode('utf8');
	movieFile = movie(row[0],1)
	cur.execute("UPDATE files SET playCount=? where idFile=?" , (movieFile.played, movieFile.idFile))		
#print "Total number of rows updated :", con.total_changes

# get bookmark for files
curC.execute("SELECT * FROM bookmark b")
data = curC.fetchall()

for row in data:
	#print row[0].encode('utf8');
	bookmarkItem = bookmark(row[1],row[2],row[3],row[4],row[5],row[6],row[7])
	cur.execute("SELECT * FROM bookmark b where b.idFile=?",(bookmarkItem.idFile,))
	dataSalon = cur.fetchone()
	if dataSalon is None:
		# row not exist => insert
		cur.execute("INSERT INTO bookmark (idFile, timeInSeconds, totalTimeInSeconds, thumbNailImage, player, playerState, type) VALUES (?,?,?,?,?,?,?)" , (bookmarkItem.idFile, bookmarkItem.timeInSeconds, bookmarkItem.totalTimeInSeconds, bookmarkItem.thumbNailImage, bookmarkItem.player, bookmarkItem.playerState, bookmarkItem.type))		
	else:
		# row already exist => update with max of timeInSeconds
		bookmarkOne = bookmark(dataSalon[1],dataSalon[2],dataSalon[3],dataSalon[4],dataSalon[5],dataSalon[6],dataSalon[7])
		if bookmarkItem.timeInSeconds > bookmarkOne.timeInSeconds:
			cur.execute("UPDATE bookmark SET timeInSeconds=? where idFile=?" , (bookmarkItem.timeInSeconds, bookmarkItem.idFile))	
		
#print "Total number of rows updated :", con.total_changes

con.commit()
	
con.close()
conC.close()

#re copie base de donnée chambre
if os.path.exists(path) == True:
	os.popen("cp -r -f /storage/.kodi/userdata/Database/MyVideos90.db /tmp/remote_database_dir/Database/")
	
#print "Operation done successfully";
