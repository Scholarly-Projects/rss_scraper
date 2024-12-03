import yt_dlp
import requests
from bs4 import BeautifulSoup
import csv

# Function to scrape Spotify podcast metadata
def fetch_spotify_metadata(podcast_url, csv_writer):
    response = requests.get(podcast_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust this based on actual podcast page structure
    episode_divs = soup.find_all('div', class_='EpisodeGridItem')

    if not episode_divs:
        print("No episodes found on the page. The page structure may have changed.")
        return

    for episode in episode_divs:
        title = episode.find('h2', class_='EpisodeTitle').text.strip() if episode.find('h2', class_='EpisodeTitle') else 'N/A'
        description = episode.find('p', class_='EpisodeDescription').text.strip() if episode.find('p', class_='EpisodeDescription') else 'N/A'
        release_date = episode.find('time', class_='ReleaseDate').text.strip() if episode.find('time', class_='ReleaseDate') else 'N/A'
        
        # Write episode data to the CSV
        csv_writer.writerow([title, 'Spotify', release_date, 'N/A', description, 'N/A'])

# Function to download YouTube audio and video and extract metadata
def fetch_youtube_audio_and_video(playlist_url, csv_writer):
    # Specify the location of ffmpeg
    ffmpeg_location = "/opt/homebrew/bin/ffmpeg"  # Adjust this path if necessary

    # Path to your cookies.txt file
    cookies_path = '/Users/andrewweymouth/Documents/GitHub/media_scraper/cookies.txt'  # Replace with the path to your cookies.txt file

    # YouTube-DL options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_location,  # Specify the location of ffmpeg
        'extractaudio': True,  # Only download audio
        'quiet': False,  # Enable verbose output for debugging
        'cookies': cookies_path,  # Correct path to cookies.txt
    }

    # Download the YouTube playlist and extract metadata for each video
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        playlist_info = ydl.extract_info(playlist_url, download=False)  # Don't download initially, just extract info
        for video in playlist_info.get('entries', []):
            title = video.get('title', 'N/A')
            upload_date = video.get('upload_date', 'N/A')
            duration = f"{video.get('duration', 0) // 60} min"
            description = video.get('description', 'N/A')
            video_url = video.get('url', 'N/A')

            # Download MP4 and MP3 files for each video
            ydl_opts.update({
                'outtmpl': f"{title}.%(ext)s",  # Save video and audio files with the same title
                'format': 'bestvideo+bestaudio/best',  # Download video and audio
            })
            with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                ydl_download.download([video_url])
            
            # Write video metadata to the CSV
            csv_writer.writerow([title, 'YouTube', upload_date, duration, description, f"{title}.mp4"])

# Main execution
youtube_playlist_url = 'https://www.youtube.com/playlist?list=PLvdtbgGlG0vblk0_ynIZgDwEew4kxUoAI'
spotify_podcast_url = 'https://creators.spotify.com/pod/show/idahohumanities'

# Open CSV file to store collected metadata
with open('media_metadata.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Platform', 'Date', 'Duration', 'Description', 'File/Link'])

    # Fetch YouTube data
    print("Fetching YouTube data...")
    fetch_youtube_audio_and_video(youtube_playlist_url, writer)

    # Fetch Spotify metadata
    print("Fetching Spotify metadata...")
    fetch_spotify_metadata(spotify_podcast_url, writer)

print('Data collection completed.')
