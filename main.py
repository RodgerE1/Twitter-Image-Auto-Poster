import tweepy
from dotenv import load_dotenv
import os
from datetime import datetime
import time
import shutil
import glob

# Load environment variables from .env file
load_dotenv()

# Configurable wait time
WAIT_TIME_SECONDS = 1800  # 30 minutes

def authenticate():
    # Get API tokens from environment variables
    bearer_token = os.getenv("BEARER_TOKEN")
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    # V1 Twitter API Authentication
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # V2 Twitter API Authentication
    client = tweepy.Client(
        bearer_token,
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret,
        wait_on_rate_limit=True,
    )

    return api, client

def create_sent_directory():
    # Create SENT directory if it doesn't exist
    if not os.path.exists("SENT"):
        os.makedirs("SENT")

def get_image_files():
    # Refresh the list of image files in the current directory
    return glob.glob("*.[jJ][pP][gG]*") + glob.glob("*.[pP][nN][gG]")

def send_tweet(api, client, filename):
    try:
        # Upload image to Twitter
        media_id = api.media_upload(filename=filename).media_id_string

        # Text to be Tweeted
        text = "#AIArtwork #aiartcommunity #AIArtGallery #AIART #AIArtistCommunity #aiartist #AIArtSociety #AIImage #sdxl #DALLE3"

        # Send Tweet with Text and media ID
        response = client.create_tweet(text=text, media_ids=[media_id])

        return response
    except tweepy.TweepError as e:
        print(f"tweepy.TweepError occurred while sending tweet for {filename}: {e.response.text}")
        return None
    except Exception as e:
        print(f"An unspecified error occurred while sending tweet for {filename}: {e}")
        return None

def print_success_message(filename):
    now = datetime.now()
    formatted_date = now.strftime("%B %d, %Y")
    formatted_time = now.strftime("%I:%M %p")
    print(f"'{filename}', successfully sent on {formatted_date}, {formatted_time}")

def move_file_to_sent(filename):
    shutil.move(filename, f"SENT/{filename}")

def countdown_to_next_tweet():
    for remaining_seconds in range(WAIT_TIME_SECONDS, 0, -60):
        print(f"Next tweet in {remaining_seconds // 60} minute(s)")
        time.sleep(60)

def main():
    api, client = authenticate()
    create_sent_directory()

    while True:
        image_files = get_image_files()
        remaining_images_count = len(image_files)
        if not image_files:
            print("No more images to process. Exiting.")
            break

        print(f"{remaining_images_count} image(s) left to tweet.")
        for filename in image_files:
            response = send_tweet(api, client, filename)
            if response:
                print_success_message(filename)
                move_file_to_sent(filename)
                countdown_to_next_tweet()
            remaining_images_count -= 1
            print(f"{remaining_images_count} image(s) left to tweet.")

if __name__ == "__main__":
    main()
