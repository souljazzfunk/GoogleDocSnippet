# Google Docs to Twitter Thread Poster

## Overview

This Python script utilizes Google Docs API and Tweepy to create a Twitter thread from a Google Docs document. The script extracts content from a Google Docs document based on specific headings, segments the content, and posts it as a Twitter thread.

## Features

- Extracts content by heading level from a Google Docs document.
- Segments the content into chunks suitable for Twitter threads.
- Posts the segmented content as a Twitter thread.
- Adds a promotional tweet at the end of the thread.

## Installation

1. Clone the repository to your local machine.
2. Install the required packages.
3. Set up your API keys and credentials.

## Usage

1. **Set Environment Variable for API Keys**

    ```bash
    export API_KEYS=/path/to/api_keys/
    ```

2. **Run the Script**

    ```bash
    python googleDocSnippet.py
    ```

## Requirements

- Google Docs API
- Tweepy

## License

This project is licensed under the MIT License.
