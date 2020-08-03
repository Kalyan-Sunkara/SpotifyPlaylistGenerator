"""
Prerequisites
    pip3 install spotipy Flask Flask-Session
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // added to your [app settings](https://developer.spotify.com/dashboard/applications)
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 -m flask run --port=8080
"""

import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import json
import uuid

application = Flask(__name__)
application.config['SECRET_KEY'] = os.urandom(64)
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = './.flask_session/'


Session(application)
spotify = ''
auth_manager=''
caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

scope = 'user-top-read user-read-playback-state streaming ugc-image-upload playlist-modify-public'


@application.route('/', methods=['GET','POST'])
def signIN():
    global spotify
    global auth_manager
    if not session.get('uuid'):
            # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path(), show_dialog=True, scope=scope)
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/home')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template('signIn.html',auth_url=auth_url)

    # Step 4. Signed in, display data
    
    return redirect('/home')


# @app.route('/')
@application.route('/home')
def index():
    global spotify
    global auth_manager

    if not auth_manager.get_cached_token():
        return redirect('/')
        
    name = spotify.me()["display_name"]
    return render_template('home.html',name=name)


@application.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')


@application.route('/playlists')
def playlists():
    global spotify
    global auth_manager
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        playlists1 = spotify.current_user_playlists()
        playlists = []
        
        for x in playlists1['items']:
            playlists.append(x['name'])
            
        style = 'background: transparent;'
        
        return render_template('playlists.html',style=style,playlists=playlists)
              
        
@application.route('/topArtists')
def topArtists():
    global spotify
    global auth_manager
    
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        topArtists1 = spotify.current_user_top_artists(limit=50,time_range="long_term")
        topArtists = []
        for x in topArtists1['items']:
            topArtists.append(x['name'])
       
        return render_template('topArtists.html',topArtists=topArtists)

@application.route('/generatePlaylist')
def makePlaylist():
    global spotify
    global auth_manager
    
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        data = 'We do not judge who you listen to'
        return render_template('generatePlaylist.html',data=data)

@application.route('/generatePlaylist', methods=['POST'])
def my_form_post():
    global spotify
    
    text = request.form['artist']
    results = spotify.search(text,1,0,"artist")
    artist = results['artists']['items'][0]
    artist_uri = artist['uri']

    recommendations = spotify.recommendations(seed_artists=[artist_uri], limit=25)
    
    track_list = recommendations['tracks']
    list_of_songs = []
    for tracks in track_list:
        # print(tracks['name'])
        list_of_songs.append(tracks['uri'])

    #create playlist
    playlist_name = 'Similar to ' + artist['name']
    playlist_description = 'Songs similar to ' + artist['name']
    spotify.user_playlist_create(user=spotify.me()["id"],name=playlist_name,public=True,description=playlist_description)

    #identify id of newest playlist
    prePlaylists = spotify.user_playlists(user=spotify.me()["id"])
    playlist = prePlaylists['items'][0]['id']

    #add 25 songs
    spotify.user_playlist_add_tracks(user=spotify.me()["id"], playlist_id=playlist, tracks=list_of_songs)
    data = 'Playlist similar to music by ' + artist['name'] + ' has been added'
    return render_template('generatePlaylist.html',data=data)

def session_cache_path():
    return caches_folder + session.get('uuid')

if __name__ =='__main__':
    application.run(host='0.0.0.0',port=8080, debug=True)
