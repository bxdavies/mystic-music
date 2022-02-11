import os
from dotenv import load_dotenv
from symsound import create_app, db
import sys

dotENVFile = os.path.join(os.path.dirname(__file__), ".env")
spotiPYCacheFolder = './.spotify-cache/'

# Check if ENV file exists
if os.path.exists(dotENVFile):
    load_dotenv(dotENVFile, verbose=True)
else:
    sys.exit("CRITICAL: Could not find .env file! ")

# Create Spotify Cache folder if not exists
if not os.path.exists(spotiPYCacheFolder):
    os.makedirs(spotiPYCacheFolder)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
