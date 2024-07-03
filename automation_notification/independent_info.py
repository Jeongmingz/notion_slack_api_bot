import ssl
import certifi

ssl_context = ssl.create_default_context(cafile=certifi.where())

from notion_client import Client
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from dotenv import load_dotenv
import os
load_dotenv()
import logging

NOTION_INTEGRATION_ID = os.getenv('NOTION_INTEGRATION_ID')
NOTION_INTEGRATION_SECRET_KEY = os.getenv('NOTION_INTEGRATION_SECRET_KEY')
NOTION_INDEPENDENT_INFO_DB_ID = os.getenv('NOTION_INDEPENDENT_INFO_DB_ID')
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
# INDEPENDENT_INFO_CHANNEL_ID = os.getenv('TEST_CHANNEL_ID')
INDEPENDENT_INFO_CHANNEL_ID = os.getenv('INDEPENDENT_INFO_CHANNEL_ID')

notion_client = Client(auth=NOTION_INTEGRATION_SECRET_KEY)
slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)

def create_slack_message(properties):
    title = properties['공고 이름']['title'][0]['text']['content']
    location = properties['지역']['select']['name']
    apply_deadline_start = properties['신청 기한']['date']['start']
    apply_deadline_end = properties['신청 기한']['date']['end']
    apply_status = properties['신청 상태']['status']['name']
    url = properties['링크']['url']

    header_text = f"신청 가능! - {title}\n{apply_deadline_end} 까지"
    text = f"*공고 이름:* {title}\n*지역:* {location}\n*신청 기한:* {apply_deadline_start} ~ {apply_deadline_end}\n*신청 상태:* {apply_status}"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text,
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        },
        {
            "type": "divider"
        }
    ]

    if url:
        blocks.append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "신청하기"
                        },
                        "url": url
                    }
                ]
            }
        )

    return header_text, blocks

def create_no_applications_message():
    header_text = "현재 신청 가능한 공고가 없습니다."
    text = "현재 신청 가능한 공고가 없습니다. 새로운 공고가 올라오면 알려드리겠습니다."

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": header_text,
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]

    return header_text, blocks

pages = notion_client.search(filter={"property": "object", "value": "page"})

applications_found = False

for page in pages['results']:
    if page['properties']['신청 여부']['formula']['string'] == '신청 가능':
        applications_found = True
        properties = page['properties']
        text, blocks = create_slack_message(properties)

        try:
            result = slack_client.chat_postMessage(
                channel=INDEPENDENT_INFO_CHANNEL_ID,
                text=text,
                blocks=blocks
            )
            logging.info(result)
        except SlackApiError as e:
            logging.error(f"Error posting message: {e}")

if not applications_found:
    header_text, blocks = create_no_applications_message()
    try:
        result = slack_client.chat_postMessage(
            channel=INDEPENDENT_INFO_CHANNEL_ID,
            text=header_text,
            blocks=blocks
        )
        logging.info(result)
    except SlackApiError as e:
        logging.error(f"Error posting message: {e}")