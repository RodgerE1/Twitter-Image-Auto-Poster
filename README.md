# Twitter Image Auto-Poster

A Python script to automatically post images to Twitter from a specified directory. The script will post one image at a time at specified intervals, and move the posted images to a "SENT" folder to avoid reposting.

## Features

- Automatically post images to Twitter at specified intervals.
- Move posted images to a "SENT" folder to avoid reposting.
- Configurable wait time between posts.
- Error handling to manage exceptions during the posting process.
- Console output for monitoring script activity and progress.
- Refreshes the image list to accommodate new images added while the script is running.

## Description

This script is designed to automate the process of posting images to Twitter. It scans a specified directory for images, posts one image at a time to Twitter, and moves the posted images to a "SENT" folder to avoid reposting. The script will wait for a specified interval between posts, and provides console output to monitor its activity and progress. It refreshes the image list at each interval to accommodate new images added while the script is running.

## Documentation

1. **Setup:**

   - Install the required packages listed in `requirements.txt`.
   - Create a `.env` file in the same directory as the script, and add your Twitter API credentials:
     ```
     BEARER_TOKEN=your_bearer_token
     CONSUMER_KEY=your_consumer_key
     CONSUMER_SECRET=your_consumer_secret
     ACCESS_TOKEN=your_access_token
     ACCESS_TOKEN_SECRET=your_access_token_secret
     ```

2. **Running the Script:**
   - Run the script using the command `python main.py`.
   - The script will post one image at a time from the specified directory to Twitter, and move the posted images to a "SENT" folder.
   - The script will output the progress to the console, including the remaining images count, successful posts, and countdown to the next post.

## License

MIT License

## Contributors

- Rodger Elliott
- ChatGPT
- [Jorge Zepeda](https://github.com/jorgez19/TweepyV2Images) (provided Twitter authentication code)
