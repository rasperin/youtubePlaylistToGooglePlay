import os
import csv
import math
import re
from gmusicapi import Mobileclient
import pickle

#REMOVE BEFORE SHARING
email='youremail@gmail.com'
#https://myaccount.google.com/apppasswords
appPassword = 'yourHexAppPassword' #This can be created in your google account settings->signin and security->App Passwords->Generate
#/REMOVE BEFORE SHARING

#Playlist info
playlistName = 'Space Dreams'
playlistId = 'PLX9sl--YXuc8oKJwO571or9WobW5ZVK7Z'
writeToPlaylist = False
#/Playlist info

missingSongs = []

def addItems(title):
    result = api.search(title)
    try:
        res = result["song_hits"][0]["track"]["storeId"]
    except NameError:
        res = False
    except IndexError:
        res = False

    if res:
        if (writeToPlaylist):
            pres = api.add_songs_to_playlist(playlist, res)
    else:
        print("Couldn't find song " + title)
        missingSongs.append(title)

def filterBadCharactersAndAddItems(items):
    for title in items:
        title = re.sub('\[(.*?)\]', '', title)
        title = re.sub('\((.*?)\)', '',  title)
        title = re.sub('【(.*?)】', '', title)
        print('Adding title: ' + title)
        if(title == 'Deleted video' or title == 'Private video'):
            print("Skipping deleted/private")
            continue
        addItems(title)


api = Mobileclient(False)
api.login(email, appPassword, Mobileclient.FROM_MAC_ADDRESS)
if (writeToPlaylist):
    playlist = api.create_playlist(playlistName, 'Building with app')

items = []
with open("space-dreams.csv") as f:
    reader = csv.DictReader(f, fieldnames=['artist', 'song'])
    for data in reader:
        items.append(data['artist']+' - '+data['song'])

filterBadCharactersAndAddItems(items)

api.logout()
print("Process completed!")
print("Missing songs are: ", len(missingSongs))
print(missingSongs)