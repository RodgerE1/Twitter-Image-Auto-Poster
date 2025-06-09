import tweepy
import configparser  # Import the configparser library
from datetime import datetime
import random

# from dotenv import load_dotenv
import os
import time
import shutil
import glob
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QHBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon

# Load environment variables from .env file
# load_dotenv()
# Instead of a fixed wait time, use a function to get a random wait time
def get_random_wait_time():
    return random.randint(600, 1200)

# Use this function to set WAIT_TIME_SECONDS before each send operation
WAIT_TIME_SECONDS = get_random_wait_time()


def initialize_config():
    config = configparser.ConfigParser()
    try:
        if not os.path.exists("Main.cfg"):
            config["TweetCount"] = {"Remaining": "1500", "ResetFlag": "False"}
            with open("Main.cfg", "w") as configfile:
                config.write(configfile)
        else:
            config.read("Main.cfg")
    except Exception as e:
        print(f"An error occurred while initializing the config file: {e}")
    return config


# Update the remaining tweet count in the config file
def update_remaining_tweet_count(config, remaining_count):
    try:
        config["TweetCount"]["Remaining"] = str(remaining_count)
        with open("Main.cfg", "w") as configfile:
            config.write(configfile)
    except Exception as e:
        print(f"An error occurred while updating the remaining tweet count: {e}")


# Reset the tweet count at the beginning of the month
def reset_tweet_count_if_needed(config):
    current_day = datetime.now().day
    reset_flag = (
        config.getboolean("TweetCount", "ResetFlag")
        if config.has_option("TweetCount", "ResetFlag")
        else False
    )

    if current_day == 1 and not reset_flag:
        update_remaining_tweet_count(config, 1500)
        try:
            config["TweetCount"]["ResetFlag"] = "True"
            with open("Main.cfg", "w") as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"An error occurred while resetting the tweet count: {e}")
    elif current_day != 1:
        try:
            config["TweetCount"]["ResetFlag"] = "False"
            with open("Main.cfg", "w") as configfile:
                config.write(configfile)
        except Exception as e:
            print(f"An error occurred while updating the reset flag: {e}")


def authenticate():
    # Get API tokens from environment variables
    bearer_token = "AAAAAAAAAAAAAAAAAAAAACBNqQEAAAAAAvpeIlap3NFbyIS79nC3k9urHbE%3DgQ89Z2RA5L6GQe9MTtdeRXMCevdSF95IVP2GhR2IIomtVjM2dN"
    consumer_key = "OUpCgrIwhfj8wEAu5tZaXcsUC"
    consumer_secret = "1npz1fpvGucQaLRYy78uQ10WXase5f8uhpgUcvajjjqkxOqIQW"
    access_token = "1225923114262986752-ptQOzWCrVUUE4F8zkHEd1iLRymgJRl"
    access_token_secret = "M91Cwf0q02KgJ4tEMcgcoxqsCdhXFWqyhR4E9rpfpHScA"
    # bearer_token = os.getenv("BEARER_TOKEN")
    # consumer_key = os.getenv("CONSUMER_KEY")
    # consumer_secret = os.getenv("CONSUMER_SECRET")
    # access_token = os.getenv("ACCESS_TOKEN")
    # access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

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
    image_files = glob.glob("*.[jJ][pP][gG]*") + glob.glob("*.[pP][nN][gG]")

    # Sort the files based on creation time in ascending order
    # sorted_files = sorted(image_files, key=lambda x: os.path.getctime(x))                #newest first
    sorted_files = sorted(
        image_files, key=lambda x: os.path.getctime(x), reverse=True
    )  # oldest first

    return sorted_files


def send_tweet(api, client, filename):
    try:
        # Upload image to Twitter
        media_id = api.media_upload(filename=filename).media_id_string

        # Text to be Tweeted
        text = "#supportsmallcreators #StableDiffusion #AIImage #SDXL #GenerativeAI #AIArtwork #aiartcommunity #AIArtGallery #AIART #AIArtistCommunity #sdxl #DALLE3 #digitalart #madewithai #artoftheday"

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
    update_gui = pyqtSignal(
        str, str, str, str, str, str, str
    )  # Add one more str for tweet count

    def __init__(self):
        super(TweetThread, self).__init__()
        self.config = initialize_config()  # Initialize the config here

    def run(self):
        api, client = authenticate()
        create_sent_directory()
        reset_tweet_count_if_needed(self.config)
        remaining_tweet_count = int(self.config["TweetCount"]["Remaining"])

        while True:
            self.refresh_image_count_and_update_gui()
            image_files = get_image_files()
            if not image_files:
                print("No more images to process. Exiting.")
                break

            for filename in image_files:
                if remaining_tweet_count <= 0:
                    print("Reached monthly tweet limit. Exiting.")
                    return

                response = send_tweet(api, client, filename)
                if response:
                    print_success_message(filename)
                    move_file_to_sent(filename)  # Move the file first

                    # Now update the GUI
                    tweet_time = datetime.now().strftime("%I:%M %p")
                    next_tweet_time = (
                        datetime.now() + timedelta(seconds=WAIT_TIME_SECONDS)
                    ).strftime("%I:%M %p")

                    image_files = get_image_files()  # refresh image list
                    next_image = image_files[0] if image_files else "None"
                    remaining_images_count = str(len(image_files))

                    remaining_tweet_count -= 1  # Decrease the tweet count
                    update_remaining_tweet_count(self.config, remaining_tweet_count)

                    self.update_gui.emit(
                        filename,
                        next_image,
                        tweet_time,
                        next_tweet_time,
                        remaining_images_count,
                        f"{WAIT_TIME_SECONDS // 60} minute(s)",
                        str(remaining_tweet_count),  # Add the remaining tweet count
                    )
                    for remaining_seconds in range(
                        WAIT_TIME_SECONDS, 0, -60
                    ):  # Decrease by 60 seconds in each iteration
                        self.update_gui.emit(
                            filename,
                            next_image,
                            tweet_time,
                            next_tweet_time,
                            remaining_images_count,
                            f"{remaining_seconds // 60} minute(s)",  # Convert seconds to minutes
                            str(remaining_tweet_count),  # Add the remaining tweet count
                        )
                        time.sleep(60)  # Sleep for 60 seconds (1 minute)
                        QApplication.processEvents()  # Refresh the GUI

    def refresh_image_count_and_update_gui(self):
        image_files = get_image_files()
        remaining_images_count = str(len(image_files))
        remaining_tweet_count = str(
            int(self.config["TweetCount"]["Remaining"])
        )  # Fetch the remaining tweet count from the config
        self.update_gui.emit(
            "", "", "", "", remaining_images_count, "", remaining_tweet_count
        )  # Add the remaining tweet count as the 7th argument


def main():
    app = QApplication([])

    window = QWidget()
    window.setWindowTitle("Twitter Image Auto-Poster")

    window.setWindowIcon(
        QIcon("D:\\Documents\\GitHub\\Twitter Image Auto-Poster\\x-Logo1.ico")
    )

    layout = QGridLayout()

    time_label = QLabel("Time: ")
    remaining_images_label = QLabel("Remaining Images: ")
    countdown_label = QLabel("Countdown to Next Tweet: ")
    remaining_tweet_count_label = QLabel("Remaining Tweets: 1500")

    tweet_sent_label = QLabel("Tweet Sent At:")
    tweet_sent_time_label = QLabel("")

    next_tweet_label = QLabel("Next Tweet At:")
    next_tweet_time_label = QLabel("")

    thumbnail_label = QLabel("Thumbnail of Last Tweet")
    next_thumbnail_label = QLabel("Thumbnail of Next Tweet")

    last_image_filename_label = QLabel("Last Image: None")
    last_image_filename_label.setWordWrap(True)
    last_image_filename_label.setMaximumWidth(512)

    next_image_filename_label = QLabel("Next Image: None")
    next_image_filename_label.setWordWrap(True)
    next_image_filename_label.setMaximumWidth(512)

    layout.addWidget(time_label, 0, 0, 1, 2)
    layout.addWidget(remaining_images_label, 0, 2, 1, 2)
    layout.addWidget(countdown_label, 0, 4)
    layout.addWidget(remaining_tweet_count_label, 0, 6, 1, 2)

    layout.addWidget(tweet_sent_time_label, 1, 0)
    layout.addWidget(thumbnail_label, 2, 0, 2, 2)
    layout.addWidget(last_image_filename_label, 4, 0, 1, 2)

    layout.addWidget(next_tweet_time_label, 1, 4, 1, 2)
    layout.addWidget(next_thumbnail_label, 2, 4, 2, 2)
    layout.addWidget(next_image_filename_label, 4, 4, 1, 2)

    window.setLayout(layout)
    window.show()

    timer = QTimer()
    timer.timeout.connect(
        lambda: time_label.setText(f"Time: {datetime.now().strftime('%I:%M %p')}")
    )
    timer.start(1000)

    tweet_thread = TweetThread()

    tweet_thread.update_gui.connect(
        lambda filename, next_image, tweet_time, next_tweet_time, remaining_images_count, countdown, remaining_tweet_count: update_gui(
            filename,
            next_image,
            tweet_time,
            next_tweet_time,
            remaining_images_count,
            countdown,
            remaining_tweet_count,
            thumbnail_label,
            next_thumbnail_label,
            tweet_sent_time_label,
            next_tweet_time_label,
            remaining_images_label,
            countdown_label,
            remaining_tweet_count_label,
            last_image_filename_label,
            next_image_filename_label,
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
    remaining_tweet_count,
    thumbnail_label,
    next_thumbnail_label,
    tweet_time_label,
    next_tweet_time_label,
    remaining_images_label,
    countdown_label,
    remaining_tweet_count_label,
    last_image_filename_label,
    next_image_filename_label,
):
    if filename:
        pixmap = QPixmap(f"SENT/{filename}")
        if pixmap.isNull():
            print(f"Failed to load image from SENT/{filename}")
        else:
            thumbnail_label.setPixmap(pixmap.scaled(512, 512))

    if next_image != "None":
        next_pixmap = QPixmap(next_image)
        if next_pixmap.isNull():
            print(f"Failed to load image from {next_image}")
        else:
            next_thumbnail_label.setPixmap(next_pixmap.scaled(512, 512))
    else:
        next_thumbnail_label.clear()

    tweet_time_label.setText(f"Tweet Sent At: {tweet_time}")
    next_tweet_time_label.setText(f"Next Tweet At: {next_tweet_time}")
    remaining_images_label.setText(f"Remaining Images: {remaining_images_count}")
    countdown_label.setText(countdown)
    remaining_tweet_count_label.setText(f"Remaining Tweets: {remaining_tweet_count}")

    last_image_filename_label.setText(f"Last Image: {filename if filename else 'None'}")
    next_image_filename_label.setText(
        f"Next Image: {next_image if next_image != 'None' else 'None'}"
    )


if __name__ == "__main__":
    main()
