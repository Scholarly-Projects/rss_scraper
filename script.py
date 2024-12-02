import yt_dlp
import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape Spotify podcast metadata
def fetch_spotify_metadata(podcast_url, csv_writer):
    response = requests.get(podcast_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all episode containers (depends on Spotify's structure)
    episode_divs = soup.find_all('div', class_='main-entityHeader-container')
    
    if not episode_divs:
        print("No episodes found on the page. The page structure may have changed.")
        return

    for episode in episode_divs:
        title = episode.find('span', class_='entity-title').text.strip() if episode.find('span', class_='entity-title') else 'N/A'
        description = episode.find('p', class_='main-description').text.strip() if episode.find('p', class_='main-description') else 'N/A'
        release_date = 'N/A'  # Spotify web scraping may not show release date directly.
        
        csv_writer.writerow([title, 'Spotify', release_date, 'N/A', description, 'N/A'])

# Function to download YouTube audio and extract metadata
def fetch_youtube_audio(playlist_url, csv_writer):
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=True)
        for video in playlist_info.get('entries', []):
            csv_writer.writerow([
                video.get('title', 'N/A'),
                video.get('upload_date', 'N/A'),
                f"{video.get('duration', 0) // 60} min",
                video.get('description', 'N/A'),
                f"{video.get('title', 'N/A')}.mp3"
            ])

# Main execution
youtube_playlist_url = 'https://www.youtube.com/playlist?list=PLvdtbgGlG0vblk0_ynIZgDwEew4kxUoAI'
spotify_podcast_url = 'https://creators.spotify.com/pod/show/idahohumanities'

with open('media_metadata.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Platform', 'Date', 'Duration', 'Description', 'File/Link'])

    print("Fetching YouTube data...")
    fetch_youtube_audio(youtube_playlist_url, writer)

    print("Fetching Spotify metadata...")
    fetch_spotify_metadata(spotify_podcast_url, writer)

print('Data collection completed.')
