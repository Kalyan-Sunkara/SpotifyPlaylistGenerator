
import os
from flask import Flask, session, request, redirect, render_template
from flask_session import Session
import spotipy
import json
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'


Session(app)
spotify = ''
auth_manager=''
caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)
# username = 'tamati-us'
# username = 'woahunicorn'
scope = 'user-top-read user-read-playback-state streaming ugc-image-upload playlist-modify-public'
# username = '26wbcozjp146flaztqwhirmqx'
# auth_manager = spotipy.oauth2.SpotifyOAuth(username=username, scope=scope)
# spotify = spotipy.Spotify(auth_manager=auth_manager)

@app.route('/', methods=['GET','POST'])
# @app.route('/login' methods=['POST'])
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
        # return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    # spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect('/home')
    # global spotify
    # if request.method == 'POST':
    #     user = request.form['user']
    #     auth_manager = spotipy.oauth2.SpotifyOAuth(username=user, scope=scope)
    #     spotify = spotipy.Spotify(auth_manager=auth_manager)
    #     session['token_info'] = auth_manager.get_access_token()
    #     return redirect('/home')
    # return render_template('login.html')


# @app.route('/')
@app.route('/home')
def index():
    global spotify
    global auth_manager
    # if request.args.get("code"):
        # print('hello')
        # session['token_info'] = auth_manager.get_access_token(request.args["code"])
        # return redirect('/home')

    if not auth_manager.get_cached_token():
        return redirect('/')
        # auth_url = auth_manager.get_authorize_url()
        # return f'<h2><a href="{auth_url}">Sign in</a></h2>'
        # return render_template('signIn.html',auth_url=auth_url)
        # return redirect('/')

    # print(json.dumps(spotify.me(),sort_keys=True,indent=4))
    name = spotify.me()["display_name"]
    return render_template('home.html',name=name)
    # part2 = f'<small><a href="/sign_out">[sign out]<a/></small></h2>'
    # part3 = f'<a href="/playlists">my playlists</a>'
    # greeting = part1 + part2 + part3
    # return render_template('home.html',name=name)


@app.route('/sign_out')
def sign_out():
    os.remove(session_cache_path())
    session.clear()
    return redirect('/')


@app.route('/playlists')
def playlists():
    global spotify
    global auth_manager
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        playlists1 = spotify.current_user_playlists()
        playlists = []
        # iterator=0
        # while x < len(playlist)
        for x in playlists1['items']:
            playlists.append(x['name'])
            # names = x['name']
            # playlists = playlists + names
        style = 'background: transparent;'
        # playlists = playlists1['items'][0]['name']
        # print(json.dumps(spotify.current_user_playlists(),sort_keys=True,indent=4))
        return render_template('playlists.html',style=style,playlists=playlists)
               # f'<a href="/">Go Back</a>'
        # playlists['items'][0]['name']
@app.route('/topArtists')
def topArtists():
    global spotify
    global auth_manager
    # if not session.get('token_info'):
    #     return redirect('/')
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        topArtists1 = spotify.current_user_top_artists(limit=50,time_range="long_term")
        topArtists = []
        for x in topArtists1['items']:
            topArtists.append(x['name'])
        # print(json.dumps(topArtists,sort_keys=True,indent=4))
        return render_template('topArtists.html',topArtists=topArtists)

@app.route('/generatePlaylist')
def makePlaylist():
    global spotify
    global auth_manager
    # if not session.get('token_info'):
    #     return redirect('/')
    if not auth_manager.get_cached_token():
        return redirect('/')
    else:
        data = 'We do not judge who you listen to'
        return render_template('generatePlaylist.html',data=data)

@app.route('/generatePlaylist', methods=['POST'])
def my_form_post():
    global spotify
    # global auth_manager
    #find the artist
    text = request.form['artist']
    results = spotify.search(text,1,0,"artist")
    artist = results['artists']['items'][0]
    artist_uri = artist['uri']

    recommendations = spotify.recommendations(seed_artists=[artist_uri], limit=25)
    #print the content in an easy to read format(derived from JSON)
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
