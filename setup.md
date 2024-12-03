1. # Setting Up a Virtual Environment for media_scraper

## Step 1: Create a Virtual Environment

On Mac

python3 -m venv .venv

On Windows

python -m venv .venv

## Step 2: Activate the Virtual Environment

On Mac

source .venv/bin/activate

On Windows

.venv\Scripts\activate

## Step 3: Install Required Packages

pip install feedparser requests pydub ffmpeg-python audiosegment

pip install feedparser requests ffmpeg-python

## Step 4: Run the Script

python script.py



