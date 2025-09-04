import requests
from pytube import YouTube
from tqdm import tqdm

# Replace with your YouTube Data API key
API_KEY = 'AIzaSyDhr9ogsIdjtWTzUfHz2SzpPD-qsZl21J8'
CHANNEL_ID = 'UCsVz2qkd_oGXGC66fcH4SFA'
urls_file = 'video_urls.txt'

# Function to get the uploads playlist ID from the channel
def get_uploads_playlist_id(channel_id):
    url = f'https://www.googleapis.com/youtube/v3/channels?key={API_KEY}&id={channel_id}&part=contentDetails'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return uploads_playlist_id
    else:
        print(f'Error fetching uploads playlist ID: {response.status_code}')
        return None

# Function to get video links and dates from the uploads playlist
def get_video_links_from_playlist(playlist_id):
    video_data = []
    url = f'https://www.googleapis.com/youtube/v3/playlistItems?key={API_KEY}&playlistId={playlist_id}&part=snippet&maxResults=50'

    while True:
        # print("new page")
        print(len(video_data))
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                video_id = item["snippet"]["resourceId"]["videoId"]
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                video_date = item["snippet"]["publishedAt"]
                video_data.append((video_url, video_date))
            
            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break  # Exit loop if no more pages
            
            url = f'https://www.googleapis.com/youtube/v3/playlistItems?key={API_KEY}&playlistId={playlist_id}&part=snippet&maxResults=50&pageToken={next_page_token}'
        else:
            print(f'Error fetching video links: {response.status_code}')
            break

    return list(set(video_data))  # Remove duplicates

# Function to save URLs and dates to a file
def save_urls_to_file(video_data, filename):
    with open(filename, 'w') as file:
        for url, date in tqdm(video_data, desc="Saving URLs", unit="url"):
            file.write(f'{url}, {date}\n')

# Function to download videos containing "jungle" in the title
def download_videos(video_links):
    processed_links = []
    
    # Load already processed URLs from the file
    try:
        with open(urls_file, 'r') as file:
            processed_links = file.read().splitlines()
    except FileNotFoundError:
        pass  # File does not exist yet

    for video_link in video_links:
        if video_link in processed_links:
            print(f'Skipping already processed video: {video_link}')
            continue
        
        try:
            yt = YouTube(video_link)
            if "jungle" in yt.title.lower():
                print(f'Downloading: {yt.title}')
                yt.streams.filter(progressive=True, file_extension='mp4').first().download()
                print(f'Downloaded: {yt.title}')
                
                # Append the processed link to the file
                with open(urls_file, 'a') as file:
                    file.write(video_link + '\n')
        except Exception as e:
            print(f'Error downloading {video_link}: {e}')

# Main function
def main():
    uploads_playlist_id = get_uploads_playlist_id(CHANNEL_ID)
    if uploads_playlist_id:
        video_data = get_video_links_from_playlist(uploads_playlist_id)
        save_urls_to_file(video_data, urls_file)  # Save all URLs and dates to a file initially
        # Uncomment the following line to download videos
        # download_videos([url for url, _ in video_data])

if __name__ == "__main__":
    main()
