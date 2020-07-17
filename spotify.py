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

        #sets window title of the gui
        self.setWindowTitle('Spotify Playlist Creator V0.0')

        #adds the gui elements
        self.initUI()

        #defines what resources we are asking from the spotify user are
        scope  = 'user-read-playback-state streaming ugc-image-upload playlist-modify-public'
        self.username = USERNAME

        #authenticates the user, so the application can be used
        token = SpotifyOAuth(scope=scope,username=self.username)

        #intializes the spotify object
        spotify = spotipy.Spotify(auth_manager=token)
        self.spotifyObject = spotify

        #device playback will come from
        self.device =''

        #keeps track of current song in the playback
        self.currentSong = ['']

    #function to create random playlist and implement it into spoitfy
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

    #webscrape function that find the lyrics to any given song(working on speed)
    def getLyrics(self,preSong,artist):

        #assumes the songs lyrics will be found on Genius.com
        song = preSong + ' ' + artist + ' Lyrics'
        website = ''
        for j in search(song, tld="co.in", num=1, stop=1, pause=2):
            website = j
        result = requests.get(website)
        soup = bs4.BeautifulSoup(result.text,'lxml')

        #find the 'p' tag in the html file
        lyrics = soup.select('p')

        #returns the lyrics found within the 'p' tag of the website
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

app = QApplication([])
app.setStyle('Fusion')
window = Window()
app.exec_()
