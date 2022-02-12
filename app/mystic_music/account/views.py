############
# Packages #
############
from flask import render_template, session, request, redirect, g, current_app, url_for, flash
import spotipy
import uuid
from functools import wraps
import os
import datetime

###########
# Modules #
###########
from . import account
from .. models import User

#############
# Functions #
#############

# Session Cache Path #
def sessionCachePath():
    return current_app.config["SPOTIFY_CACHE_FOLDER"] + session.get("id")


# Login Required 
def loginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # Check if ID is in session
        if session.get("id") is None:
            return redirect(url_for("account.login"))
        
        # Define Spotify Cache and Auth Handler Variables
        cacheHandler = spotipy.cache_handler.CacheFileHandler(cache_path=sessionCachePath())
        authManager = spotipy.oauth2.SpotifyOAuth(cache_handler=cacheHandler)

        # If Token is not valid or expired then redirect to Login
        if not authManager.validate_token(cacheHandler.get_cached_token()):
            return redirect(url_for("account.login"))

        # Define Spotify Variable 
        spotify = spotipy.Spotify(auth_manager=authManager)

        # Make Spotify variable global
        g.spotify = spotify
        
        return f(*args, **kwargs)
    return decorated_function


# Add Track List to DB #
def addTrackListToDB(spotify, userID):

    # Get user from the DB
    user = User.objects(id=userID).first()

    # Clear existing Songs 
    user.songs = []
    user.save()
    
    # Get number of saved tracks
    numberOfTracks = spotify.current_user_saved_tracks(market="GB")["total"]
    
    # Query the API in increments of 20
    for offset in range(0, numberOfTracks, 20):
        
        # Query the API and assign result to results
        results = spotify.current_user_saved_tracks(market="GB", offset=offset)["items"]

        # Loop through the Results
        for track in results:

            # Add song ID to the DB
            user.songs.append(track["track"]["id"])
            user.save()


#########
# Login #
#########           
@account.route('/login')
def login():

    # Assign visitor a Random ID
    if not session.get("id"):
        session["id"] = str(uuid.uuid4())

    # Define Spotify Cache and Auth Handler Variables
    cacheHandler = spotipy.cache_handler.CacheFileHandler(cache_path=sessionCachePath())
    authManager = spotipy.oauth2.SpotifyOAuth(scope='user-library-read',
                                                cache_handler=cacheHandler, 
                                                show_dialog=True)

    # If user just logged in 
    if request.args.get("code"):
        authManager.get_access_token(request.args.get("code"))
        spotify = spotipy.Spotify(auth_manager=authManager)

        # Get ID and Display Name
        userID = spotify.me()["id"]
        displayName = spotify.me()["display_name"]

        # Check if user in DB
        user = User.objects(id=userID).first()

        # If user is not in DB then add them and sync there Spotify account 
        if user is None:
            User(id=userID, display_name=displayName).save()
            addTrackListToDB(spotify, userID)
        
        # If the user is in the DB then update last login
        else:
            user.last_login = datetime.datetime.utcnow
            user.save()

        # Redirect to the Account Dashboard
        return redirect(url_for("account.dashboard"))

    #  Redirect to Authorization URL as user is not authenticated!
    if not authManager.validate_token(cacheHandler.get_cached_token()):
        authUrl = authManager.get_authorize_url()
        return redirect(authUrl)

    # If the token is not valid or not in URL redirect to the Authorization URL
    authUrl = authManager.get_authorize_url()
    return redirect(authUrl)


###########
# Log Out #
###########
@account.route('/log-out')
def logOut():
    
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(sessionCachePath())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    flash('You have been logged out!', 'success')
    return redirect(url_for("main.index"))


#############
# Dashboard #
#############
@account.route('/dashboard')
@loginRequired
def dashboard():

    # Spotify Variables 
    spotify = g.spotify
    displayName = spotify.me()["display_name"]

    # Return Dashboard Template with the variable displayName 
    return render_template("account/dashboard.html", displayName=displayName)


########
# Sync #
########
@account.route('/sync')
@loginRequired
def sync():

    # Spotify Variables 
    spotify = g.spotify
    userID = spotify.me()["id"]

    # Call the function for adding the track list to the DB
    addTrackListToDB((spotify, userID)

    # Flash success message and redirect to the account dashboard
    flash('You\'re Spotify account has been synced with Mystic Music!', 'success')
    return redirect(url_for("account.dashboard"))


##########
# Delete #
##########
@account.route('/delete')
@loginRequired
def delete(): 

    # Spotify Variables 
    spotify = g.spotify
    userID = spotify.me()["id"]

    # Get user from the DB and delete
    user = User.objects(id=userID).first()
    user.delete()

    # Flash success message and redirect to the homepage
    flash('You\'re Mystic Music account has been deleted!', 'success')
    return redirect(url_for("main.index"))
