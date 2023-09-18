from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import random
import time
import tweepy
import sys
sys.path.append('..')
from api_keys import GoogleDocKeys, TwitterApiKeys
# import os
# sys.path.append(os.environ.get('API_KEYS'))

# Initialize the API client
my = GoogleDocKeys()
scopes = ['https://www.googleapis.com/auth/documents.readonly']
credentials = Credentials.from_service_account_file(my.CREDENTIAL_FILE, scopes=scopes)
service = build('docs', 'v1', credentials=credentials)
document_id = my.DOCUMENT_ID
document = service.documents().get(documentId=document_id).execute()

# Parse the document content
headings = []
segment_content = []
current_segment = []
current_level = 0  # Store the current heading level; 0 means not within any heading section
desired_level = 2  # Set the desired heading level to collect

for element in document['body']['content']:
    if 'paragraph' in element:
        style = element['paragraph'].get('paragraphStyle', {})
        level = style.get('namedStyleType', "")
        
        # Check for any new heading level
        if level.startswith('HEADING_'):
            current_level = int(level.split('_')[-1])
            
            # If it's a desired level or higher, start a new segment
            if current_level <= desired_level:
                if current_segment:  # Save the previous segment if it exists
                    cleaned_segment = '_ '.join(current_segment).strip()
                    if cleaned_segment:  # Only store if it's not empty
                        segment_content.append(cleaned_segment)
                current_segment = []  # Reset the current segment
                
            # Store the heading
            heading_text = ""
            for part in element['paragraph']['elements']:
                if 'textRun' in part:
                    heading_text += part['textRun']['content']
            heading_text = heading_text.strip()
            if current_level == desired_level:
                headings.append(heading_text)
        
        if any(substring in heading_text for substring in ["参考文献", "使用例", "プロンプト例", "回答例", "生成例", "の例", "Source: "]):
            continue

        # Collect all text under the current heading
        if current_level >= desired_level:
            paragraph_text = ""
            for part in element['paragraph']['elements']:
                if 'textRun' in part:
                    paragraph_text += part['textRun']['content']
            paragraphs = paragraph_text.strip().split('_ ')
            current_segment.extend(paragraphs)

# Save the last segment if it exists
if current_segment:
    cleaned_segment = '_ '.join(current_segment).strip()
    if cleaned_segment:  # Only store if it's not empty
        segment_content.append(cleaned_segment)

chunks = 5  # Number of continuous paragraphs to extract
thread_content = ""

while True:
    num_segment = random.randint(1, len(segment_content) - 1)
    paragraphs = segment_content[num_segment].split('_ ')
    paragraphs = [s for s in paragraphs if s.strip()]

    if "ゲーム" in headings[num_segment]:
        continue

    if len(paragraphs) > chunks:  # Only proceed if the segment has enough paragraphs
        start_index = random.randint(1, len(paragraphs) - chunks)
        end_index = start_index + chunks
        extracted_paragraphs = paragraphs[start_index:end_index]
        thread_content = headings[num_segment] + "\n"
        thread_content += '\n\n'.join(extracted_paragraphs)
        break

def calculate_weighted_length(char):
    if char.isspace():  # Whitespace
        return 1
    elif char.isascii():  # ASCII characters
        return 1
    elif len(char.encode('utf-8')) > 1:  # Multi-byte characters (Assuming these are Japanese)
        return int((len(char.encode('utf-8')) / 3) * 2)
    else:
        print(f"Unhandled character: {char}")
        return 2  # Default handling

def slice_into_tweets(text):
    tweets = []
    tweet = ""
    tweet_length = 0
    continue_phrase = "（続く↓）"
    continue_length = calculate_weighted_length(continue_phrase)

    for char in text:
        char_length = calculate_weighted_length(char)

        if tweet_length + char_length + continue_length > 280:
            tweet += continue_phrase
            tweets.append(tweet)
            tweet = ""
            tweet_length = 0

        tweet += char
        tweet_length += char_length

    # if tweet:  # Add the last remaining tweet
    #     tweets.append(tweet)

    return tweets

promo_tweet = '''この続きはKindleで無料で読めます。
こちらの本です↓
https://amzn.to/3JkjuvZ
#ChatGPT #BingAI 
'''

tweets = slice_into_tweets(thread_content)
tweets.append(promo_tweet)

# for i, tweet in enumerate(tweets):
#     print(f"Tweet {i+1}: {tweet} (Weighted Length: {sum([calculate_weighted_length(c) for c in tweet])})")

def post_thread(tweets):
    my = TwitterApiKeys()
    tw = tweepy.Client(
        consumer_key=my.consumer_key,
        consumer_secret=my.consumer_secret,
        access_token=my.access_token,
        access_token_secret=my.access_token_secret
    )

    prev_tweet_id = None

    for tweet in tweets:
        if prev_tweet_id:
            response = tw.create_tweet(text=tweet, in_reply_to_tweet_id=prev_tweet_id)
        else:
            response = tw.create_tweet(text=tweet)
        prev_tweet_id = response[0]['id']
        print(tweet, "\n")
        time.sleep(1)

try:
    post_thread(tweets)
    # [print(t, "\n") for t in tweets]
except Exception as e:
    print(f"error: {e}")
    print(tweets)
