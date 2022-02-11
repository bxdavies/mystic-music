from flask import render_template, session, request, redirect, g, current_app, url_for, flash
from . import account
import spotipy
import uuid
from functools import wraps
import os
from .. models import User
import datetime
import json

def session_cache_path():
    return current_app.config["SPOTIFY_CACHE_FOLDER"] + session.get("id")

def loginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            print('No session')
            return redirect('/auth/login')
         
        cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/auth/login')

        spotify = spotipy.Spotify(auth_manager=auth_manager)
        g.spotify = spotify
        return f(*args, **kwargs)
    return decorated_function

@account.route('/login')
def login():
    # Assign visitor a Random ID
    if not session.get("id"):
        session["id"] = str(uuid.uuid4())

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read',
                                                cache_handler=cache_handler, 
                                                show_dialog=True)

     # If user just logged in 
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"))
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        # Get ID and Display Name
        userID = spotify.me()["id"]
        displayName = spotify.me()["display_name"]

        # Check if user in DB
        user = User.objects(id=userID).first()
        if user is None:
            User(id=userID, display_name=displayName).save()
            syncAndAddToDB(spotify, userID)
            
        else:
            user.last_login = datetime.datetime.utcnow
            user.save()

        
        return redirect(url_for("account.dashboard"))

    #  Redirect to Authorization URL as user is not authenticated!
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    auth_url = auth_manager.get_authorize_url()
    return redirect(auth_url)
   
    
@account.route('/log-out')
def logOut():
    
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    flash('You have been logged out!', 'success')
    return redirect(url_for("main.index"))

@account.route('/dashboard')
@loginRequired
def dashboard():
    spotify = g.spotify
    displayName = spotify.me()["display_name"]
    return render_template("account/dashboard.html", displayName=displayName)

@account.route('/sync')
@loginRequired
def sync():
    spotify = g.spotify
    userID = spotify.me()["id"]
    syncAndAddToDB(spotify, userID)
    return redirect(url_for("account.dashboard"))

@account.route('/delete')
@loginRequired
def delete(): 
    spotify = g.spotify
    userID = spotify.me()["id"]
    user = User.objects(id=userID).first()
    user.delete()
    return redirect(url_for("main.index"))

def syncAndAddToDB(spotify, userID):
    user = User.objects(id=userID).first()

    # Clear existing Songs 
    user.songs = []
    user.save()
    
    # Get number of saved tracks
    numberOfTracks = spotify.current_user_saved_tracks(market="GB")["total"]
    
    # Loop through tracks in increments of 20
    for offset in range(0, numberOfTracks, 20):
        
        results = spotify.current_user_saved_tracks(market="GB", offset=offset)["items"]

        for track in results:

            user.songs.append(track["track"]["id"])
            user.save()
            
    
        
    