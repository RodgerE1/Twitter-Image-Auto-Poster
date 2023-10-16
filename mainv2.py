import tweepy
from dotenv import load_dotenv
import os
import time
import shutil
import glob
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta

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
        print(
            f"tweepy.TweepError occurred while sending tweet for {filename}: {e.response.text}"
        )
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


class TweetThread(QThread):
    update_gui = pyqtSignal(str, str, str, str, str, str)

    def run(self):
        api, client = authenticate()
        create_sent_directory()

        while True:
            self.refresh_image_count_and_update_gui()
            image_files = get_image_files()
            if not image_files:
                print("No more images to process. Exiting.")
                break

            for filename in image_files:
                response = send_tweet(api, client, filename)
                if response:
                    print_success_message(filename)
                    move_file_to_sent(filename)

                    tweet_time = datetime.now().strftime("%I:%M %p")
                    next_tweet_time = (
                        datetime.now() + timedelta(seconds=WAIT_TIME_SECONDS)
                    ).strftime("%I:%M %p")

                    image_files = get_image_files()  # refresh image list
                    next_image = image_files[0] if image_files else "None"
                    remaining_images_count = str(len(image_files))

                    self.update_gui.emit(
                        filename,
                        next_image,
                        tweet_time,
                        next_tweet_time,
                        remaining_images_count,
                        f"{WAIT_TIME_SECONDS // 60} minute(s)",
                    )

                    time.sleep(WAIT_TIME_SECONDS)

    def refresh_image_count_and_update_gui(self):
        image_files = get_image_files()
        remaining_images_count = str(len(image_files))
        self.update_gui.emit("", "", "", "", remaining_images_count, "")


def main():
    app = QApplication([])

    window = QWidget()
    layout = QVBoxLayout()

    time_label = QLabel("Time: ")
    thumbnail_label = QLabel("Thumbnail: ")
    next_thumbnail_label = QLabel("Next Thumbnail: ")
    tweet_time_label = QLabel("Tweet Sent At: ")
    next_tweet_time_label = QLabel("Next Tweet At: ")
    remaining_images_label = QLabel("Remaining Images: ")
    countdown_label = QLabel("Next Tweet in: ")

    layout.addWidget(time_label)
    layout.addWidget(thumbnail_label)
    layout.addWidget(next_thumbnail_label)
    layout.addWidget(tweet_time_label)
    layout.addWidget(next_tweet_time_label)
    layout.addWidget(remaining_images_label)
    layout.addWidget(countdown_label)

    window.setLayout(layout)
    window.show()

    timer = QTimer()
    timer.timeout.connect(
        lambda: time_label.setText(f"Time: {datetime.now().strftime('%I:%M %p')}")
    )
    timer.start(1000)  # Update every second

    tweet_thread = TweetThread()
    tweet_thread.update_gui.connect(
        lambda filename, next_image, tweet_time, next_tweet_time, remaining_images_count, countdown: update_gui(
            filename,
            next_image,
            tweet_time,
            next_tweet_time,
            remaining_images_count,
            countdown,
            thumbnail_label,
            next_thumbnail_label,
            tweet_time_label,
            next_tweet_time_label,
            remaining_images_label,
            countdown_label,
        )
    )
    tweet_thread.start()

    app.exec_()


def update_gui(
    filename,
    next_image,
    tweet_time,
    next_tweet_time,
    remaining_images_count,
    countdown,
    thumbnail_label,
    next_thumbnail_label,
    tweet_time_label,
    next_tweet_time_label,
    remaining_images_label,
    countdown_label,
):
    # Display the thumbnail of the image that was just sent
    if filename:
        pixmap = QPixmap(f"SENT/{filename}")
        thumbnail_label.setPixmap(pixmap.scaled(512, 512))

    # Display the thumbnail of the next image to be sent
    if next_image != "None":
        next_pixmap = QPixmap(next_image)
        next_thumbnail_label.setPixmap(next_pixmap.scaled(512, 512))
    else:
        next_thumbnail_label.clear()

    # Update the time labels
    tweet_time_label.setText(f"Tweet Sent At: {tweet_time}")
    next_tweet_time_label.setText(f"Next Tweet At: {next_tweet_time}")

    # Update remaining images count
    remaining_images_label.setText(f"Remaining Images: {remaining_images_count}")

    # Update countdown
    countdown_label.setText(countdown)


if __name__ == "__main__":
    main()
