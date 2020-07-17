import os
import base64
import sys
import json
import spotipy
import webbrowser
import requests
import bs4
from googlesearch import *
import spotipy.util as util
from json.decoder import JSONDecodeError
from PyQt5.QtWidgets import *
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Spotify Playlist Creator V0.0')
        self.initUI()
        scope  = 'user-read-playback-state streaming ugc-image-upload playlist-modify-public'
        self.username = 'tamati-us'
        token = SpotifyOAuth(scope=scope,username=self.username)
        spotify = spotipy.Spotify(auth_manager=token)
        self.spotifyObject = spotify
        self.device =''
        self.currentSong = ['']

    def generatePlaylist(self):
        try:
            searchQuery = self.artistField.text()
            results = self.spotifyObject.search(searchQuery,1,0,"artist")
            artist = results['artists']['items'][0]
            artist_uri = artist['uri']

            #Genereate JSON of 10 recommended Tracks
            recommendations = self.spotifyObject.recommendations(seed_artists=[artist_uri], limit=int(self.amountOfSongs.currentText()))
            #print the content in an easy to read format(derived from JSON)
            track_list = recommendations['tracks']
            list_of_songs = []
            self.songs.clear()
            for tracks in track_list:
                self.songs.addItem(tracks['name'])
                # print(tracks['name'])
                list_of_songs.append(tracks['uri'])

            #create playlist
            playlist_name = 'Similar to ' + artist['name']
            playlist_description = 'Songs similar to ' + artist['name']
            self.spotifyObject.user_playlist_create(user=self.username,name=playlist_name,public=True,description=playlist_description)

            #identify id of newest playlist
            prePlaylists = self.spotifyObject.user_playlists(user=self.username)
            playlist = prePlaylists['items'][0]['id']

            #add 20 songs
            self.spotifyObject.user_playlist_add_tracks(user=self.username, playlist_id=playlist, tracks=list_of_songs)
            newtag = 'A playlist with songs similar to '  + artist['name'] + ' has been added!'
            self.label2.setText(newtag)
            self.label2.show()
            self.button2.setEnabled(True)
            self.button3.setEnabled(True)
        # print(json.dumps(newResults,sort_keys=True, indent=4))
        except:
            self.label2.setText('Bad Artist Name!')
    def getLyrics(self,preSong,artist):
        song = preSong + ' ' + artist + ' Lyrics'
        website = ''
        for j in search(song, tld="co.in", num=1, stop=1, pause=2):
            website = j
        result = requests.get(website)
        soup = bs4.BeautifulSoup(result.text,'lxml')
        lyrics = soup.select('p')
        return lyrics[0].getText()
    def startPlaying(self):
        # try:
        newResults = self.spotifyObject.search(self.songs.currentText(), limit=10, offset=0, type='track', market=None)
        bruh = newResults['tracks']
        # print(json.dumps(bruh,sort_keys=True, indent=4))
        artistPre = bruh['items'][0]['artists']
        artist = artistPre[0]['name']
        songURI = bruh['items'][0]['uri']
        devices1 = self.spotifyObject.devices()
        devices1['devices'][1]['is_active'] = True
        self.device = devices1['devices'][1]['id']
        self.lyrics.setPlainText(self.getLyrics(self.songs.currentText(), artist))
        self.lyrics.show()
        # print(json.dumps(self.device,sort_keys=True, indent=4)
        if self.currentSong[0]!=self.songs.currentText():
            self.spotifyObject.start_playback(device_id = self.device,uris=[songURI])
        else:
            self.spotifyObject.start_playback(device_id = self.device,uris=[songURI],position_ms=self.currentSong[1])
        # except:
        #     print('Spotify is not open!')
    def pause(self):
        self.spotifyObject.pause_playback(device_id=self.device)
        playBackInfoTemp = self.spotifyObject.current_playback()
        playBackInfo = playBackInfoTemp['progress_ms']
        self.currentSong = [self.songs.currentText(),playBackInfo]
    def initUI(self):
        layout = QGridLayout()
        self.image1 = QPixmap('/Users/kalyan/PythonPrograms/file-spotify-logo-png-4.png')
        self.image1 = self.image1.scaledToWidth(100)
        self.labelPic = QLabel(self)
        self.labelPic.setPixmap(self.image1)
        self.labelPic.setAlignment(Qt.AlignCenter)
        self.label1 = QLabel('Enter artist:',self)
        self.artistField  = QLineEdit()
        self.button1 = QPushButton('Genereate Playlist', self)
        self.button2 = QPushButton()
        self.button2.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        # self.button2.setStyleSheet("background-color:#44eb4a""QPushButton:pressed { background-color: red }")
        self.button2.setStyleSheet("QPushButton { background-color: #44eb4a}"
                      "QPushButton:pressed { background-color: red }" )
        self.button1.setStyleSheet("QPushButton { color: black;background-color: #44eb4a }"
                                    "QPushButton:pressed { background-color: red }" )
        self.button3 = QPushButton()
        self.button3.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.button3.setStyleSheet("QPushButton { background-color: #44eb4a }"
                      "QPushButton:pressed { background-color: red }" )
        # self.button3.setIcon(QIcon('/Users/kalyan/PythonPrograms/pngtree-pause-vector-icon-png-image_470715.jpg'))
        # self.button3.setGeometry(200, 1000, 100, 40)
        self.label2 = QLabel('',self)
        self.label2.setAlignment(Qt.AlignCenter)
        self.label2.hide()
        self.amountOfSongs = QComboBox()
        self.amountOfSongs.addItems(['10', '25', '50'])
        self.songs =  QComboBox()
        self.lyrics = QPlainTextEdit()
        self.lyrics.setReadOnly(True)
        layout.addWidget(self.lyrics,4,1)
        layout.addWidget(self.labelPic,0,1)
        layout.addWidget(self.label1,1,0)
        layout.addWidget(self.artistField,1,1)
        layout.addWidget(self.button1, 1, 2)
        layout.addWidget(self.label2, 2,1)
        layout.addWidget(self.amountOfSongs,2,0)
        layout.addWidget(self.songs,3,0)
        layout.addWidget(self.button2,3,1)
        layout.addWidget(self.button3,3,2)
        self.button2.setEnabled(False)
        self.button3.setEnabled(False)
        self.label2.hide()
        self.lyrics.hide()
        self.setLayout(layout)
        self.setStyleSheet("color: #44eb4a; background-color: black;")
        self.artistField.setStyleSheet("color: black; background-color: white;")
        self.amountOfSongs.setStyleSheet("color: white; background-color: black; selection-background-color:#44eb4a;")
        self.songs.setStyleSheet("color: white; background-color: black; selection-background-color:#44eb4a;")
        # QAbstractItemView.setStyleSheet('color:white;')
        self.show()

        self.button1.clicked.connect(self.generatePlaylist)
        self.button2.clicked.connect(self.startPlaying)
        self.button3.clicked.connect(self.pause)
# scope  = 'ugc-image-upload playlist-modify-public'
# username = input('input username: ')
# token = SpotifyOAuth(scope=scope,username=username)
# spotifyObject = spotipy.Spotify(auth_manager=token)
# print(token.get_authorize_url())


# os.system(token.get_authorize_url())
app = QApplication([])
app.setStyle('Fusion')
window = Window()
app.exec_()
#Get the Username from terminal
# username = sys.argv[1]
# username = input('What is your username: ')
#
# #using scope to modify Playlists
# scope  = 'ugc-image-upload playlist-modify-public'
# #user ID: tamati-us
#
# #Erase cache and prompt for user permission
# try:
#     token = util.prompt_for_user_token(username, scope)
# except:
#     os.remove(f".cache-{username}")
#     token = util.prompt_for_user_token(username, scope)
#
# #Create spotify Object
#
# spotifyObject = spotipy.Spotify(auth=token)
#
# user = spotifyObject.current_user()
# # print(json.dumps(user,sort_keys=True, indent=4))
# # displayName = user['display_name']
# # follower = user['followers']['total']
# # print(f'Display Name:{displayName}')
# # print(f'Followers:{follower}')
# def playlistCreation():
#     #import global variables
#     global username
#     global spotifyObject
# #
#     #create the spotify playlist!
#     playlist_name = input('Playlist name: ')
#     playlist_description = input('Playlist Desctiption: ')
#     spotifyObject.user_playlist_create(user=username,name=playlist_name,public=True,description=playlist_description)
#
#     #identify id of newest playlist
#     prePlaylists = spotifyObject.user_playlists(user=username)
#     playlist = prePlaylists['items'][0]['id']
#
#     #finds the tracks to add to the playlist!
#     list_of_songs  = []
#     while True:
#         try:
#             searchQuery = input("Track Name(Enter 'q' to exit): ")
#             if(searchQuery == 'q'):
#                 break
#             results = spotifyObject.search(searchQuery,1,0,"track")
#             song_uri = results['tracks']['items']
#             song_uri = song_uri[0]['uri']
#             list_of_songs.append(song_uri)
#         except:
#             print('Incorrect Song')
#
#     #adds the songs to the playlist
#     spotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist, tracks=list_of_songs)
#
#
# def searchArtist():
#     global spotifyObject
#     searchQuery = input('Artist Name: ')
#     results = spotifyObject.search(searchQuery,1,0,"artist")
#     artist = results['artists']['items'][0]
#     artist_uri = artist['uri']
#     print()
#     print(artist['name'])
#     print(str(artist['followers']['total']) + " followers")
#     print()
#     # print(artist['genres'][0])
#     genreList = artist['genres']
#     genreString = "Genre: "
#     for x in genreList:
#         genreString  =  genreString + x + ", "
#
#     print(genreString)
#     print()
#     #print artist albums!
#     albumsJSON = spotifyObject.artist_albums(artist_uri, album_type='album')
#     albumsResults = albumsJSON['items'];
#     albums = 'Albums: '
#     for x in albumsResults:
#         if x['name'] not in albums:
#             albums  =  albums + x['name'] + ", "
#     print(albums)
#     print(json.dumps(results,sort_keys=True, indent=4))
# def recommend():
#     global username
#     global spotifyObject
#     #Find the Artist URI
#     try:
#         searchQuery = input('Artist Name: ')
#         results = spotifyObject.search(searchQuery,1,0,"artist")
#         artist = results['artists']['items'][0]
#         artist_uri = artist['uri']
#
#         #Genereate JSON of 10 recommended Tracks
#         recommendations = spotifyObject.recommendations(seed_artists=[artist_uri])
#         #print the content in an easy to read format(derived from JSON)
#         track_list = recommendations['tracks']
#         list_of_songs = []
#         for tracks in track_list:
#             print(tracks['name'])
#             list_of_songs.append(tracks['uri'])
#
#         #create playlist
#         playlist_name = 'Similar to ' + artist['name']
#         playlist_description = 'Songs similar to ' + artist['name']
#         spotifyObject.user_playlist_create(user=username,name=playlist_name,public=True,description=playlist_description)
#
#         #identify id of newest playlist
#         prePlaylists = spotifyObject.user_playlists(user=username)
#         playlist = prePlaylists['items'][0]['id']
#
#         #add 20 songs
#         spotifyObject.user_playlist_add_tracks(user=username, playlist_id=playlist, tracks=list_of_songs)
#     except:
#         print('Unexpected Error!')
#     # spotifyObject.playlist_upload_cover_image(playlist_id=playlist,image_b64='')
#
#
#
# while(True):
#     print('0 - Search For Artist')
#     print('1 - Create Recommendations Playlist')
#     print('2 - Create Custom Playlist')
#     print('3  - Quit')
#     print()
#     choice = input('Choose option: ')
#     if choice == '0':
#         searchArtist()
#     elif choice == '1':
#         recommend()
#     elif choice == '2':
#         playlistCreation()
#     elif choice == '3':
#         break
#     else:
#         print("Choose Valid Option")
# print(json.dumps(results,sort_keys=True, indent=4))

#print(json.dumps(VARIABLE,sort_keys=True, indent=4))
