import os

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import math
import re
from gmusicapi import Mobileclient
import pickle

#Playlist info
playlistName = 'down tempo beat'
playlistId = 'PLX9sl--YXuc8oKJwO571or9WobW5ZVK7Z'
writeToPlaylist = False
#/Playlist info

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    fname='smth'
    pickleExists = os.path.isfile(fname)
    if pickleExists:
        fileObject = open(fname, 'rb')
        credentials = pickle.load(fileObject)
        fileObject.close()
    else:
        credentials = flow.run_console()
        fileObject = open(fname, 'wb')
        pickle.dump(credentials, fileObject)
        fileObject.close()
    return build(API_SERVICE_NAME, API_VERSION, developerKey=developerKey, credentials=credentials)


def print_response(response):
    print(response)


#Google craptastic generated code
def build_resource(properties):
    resource = {}
    for p in properties:
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]
            if key[-2:] == '[]':
                key = key[0:len(key) - 2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(',')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                ref[key] = {}
                ref = ref[key]
            else:
                ref = ref[key]
    return resource


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def playlist_items_list_by_playlist_id(client, **kwargs):
    response = client.playlistItems().list(
        **kwargs
    ).execute()

    return response

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

def printItems(items):
    try:
        nextPageToken=items['nextPageToken']
    except KeyError:
        nextPageToken=''
    print('nextPageToken: ' + nextPageToken)
    for item in items['items']:
        title = item['snippet']['title']
        title = re.sub('\[(.*?)\]', '', title)
        title = re.sub('\((.*?)\)', '',  title)
        title = re.sub('【(.*?)】', '', title)
        print('Adding title: ' + title)
        if(title == 'Deleted video' or title == 'Private video'):
            print("Skipping deleted/private")
            continue
        addItems(title)

    return nextPageToken

if __name__ == '__main__':
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    client = get_authenticated_service()

    api = Mobileclient(False)
    api.login(email, appPassword, Mobileclient.FROM_MAC_ADDRESS)
    if (writeToPlaylist):
        playlist = api.create_playlist(playlistName, 'Building with app')

    maxResults = 50
    items = playlist_items_list_by_playlist_id(client,
                                       part='snippet',
                                       maxResults=maxResults,
                                       playlistId=playlistId)

    itemsCount = int(items['pageInfo']['totalResults'])
    pages = math.ceil(itemsCount/maxResults)+1

    nextPage = printItems(items)

    if itemsCount > maxResults:
        for i in range(1, pages):
            items = playlist_items_list_by_playlist_id(client,
                                                       part='snippet',
                                                       maxResults=maxResults,
                                                       pageToken=nextPage,
                                                       playlistId=playlistId)
            nextPage = printItems(items)
            if nextPage == '':
                break

    api.logout()
    print("Process completed!")
    print("Total song count: ", itemsCount)
    print("Missing songs are: ", len(missingSongs))
    print(missingSongs)