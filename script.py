import feedparser
import requests
import os
import csv
import ffmpeg
from bs4 import BeautifulSoup

# URL of the RSS feed
rss_url = "https://anchor.fm/s/8a0924fc/podcast/rss"

# Directory where you want to save the media files
save_dir = "podcast_media_files"

# CSV file to save metadata
metadata_csv = "podcast_metadata.csv"

# Make sure the save directory exists
os.makedirs(save_dir, exist_ok=True)

# Function to download media file
def download_media(file_url, title, extension):
    file_name = f"{title}.{extension}"
    file_path = os.path.join(save_dir, file_name)

    if not os.path.exists(file_path):
        print(f"Downloading: {file_name}")
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            with open(file_path, 'wb') as media_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        media_file.write(chunk)
            print(f"Downloaded: {file_name}")
        else:
            print(f"Failed to download: {file_name}")
    else:
        print(f"File {file_name} already exists!")

# Function to convert M4A to MP3 using ffmpeg
def convert_m4a_to_mp3(m4a_file, mp3_file):
    print(f"Converting {m4a_file} to {mp3_file}")
    try:
        ffmpeg.input(m4a_file).output(mp3_file).run()
        print(f"Conversion successful: {mp3_file}")
    except ffmpeg.Error as e:
        print(f"Error converting {m4a_file}: {e}")

# Function to clean HTML tags using BeautifulSoup
def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

# Function to fetch and parse RSS feed
def fetch_rss_metadata():
    feed = feedparser.parse(rss_url)

    with open(metadata_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Description", "Published", "Creator", "Duration", "Media URL", "File Type"])

        for entry in feed.entries:
            title = entry.title.replace("/", "-")
            description = clean_html(entry.summary)
            published = entry.published if 'published' in entry else "Unknown"
            creator = clean_html(entry.get("dc:creator", "Unknown"))  # Extracting creator
            duration = entry.get("itunes_duration", "Unknown")
            media_url = None
            file_type = None

            unsupported_files = []  # List to store unsupported file types

            if 'enclosures' in entry:
                for enclosure in entry.enclosures:
                    media_type = enclosure['type']
                    media_url = enclosure['url']

                    # Check for supported file types including .m4a
                    if 'audio/mpeg' in media_type:
                        file_type = 'mp3'
                    elif 'audio/x-m4a' in media_type or 'audio/m4a' in media_type:
                        file_type = 'm4a'
                    elif 'video/mp4' in media_type:
                        file_type = 'mp4'
                    elif 'video/x-matroska' in media_type:
                        file_type = 'mkv'
                    else:
                        unsupported_files.append(media_type)

                    if media_url and file_type:
                        download_media(media_url, title, file_type)

                        # Convert .m4a to .mp3 if necessary
                        if file_type == 'm4a':
                            m4a_file = os.path.join(save_dir, f"{title}.m4a")
                            mp3_file = os.path.join(save_dir, f"{title}.mp3")
                            convert_m4a_to_mp3(m4a_file, mp3_file)
                            os.remove(m4a_file)  # Remove the original M4A file after conversion
                            file_type = 'mp3'  # Update the file type

                        writer.writerow([title, description, published, creator, duration, media_url, file_type])
                        break

            if not media_url:
                print(f"No media downloaded for: {title}")

            if unsupported_files:
                print(f"Unsupported file types for '{title}': {', '.join(unsupported_files)}")

# Call the function to fetch, download media, and save metadata
fetch_rss_metadata()
