import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
import os
import logging

# 환경 변수 로드
load_dotenv()

# 환경 변수에서 토큰 및 채널 ID 가져오기
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
DEPLOY_CHANNEL_ID = os.getenv('DEPLOY_CHANNEL_ID')

# SSL 설정
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Slack 클라이언트 초기화
slack_client = WebClient(token=SLACK_BOT_TOKEN, ssl=ssl_context)

def create_slack_message():
    header_text = "배포 완료 알림"
    text = "성공적으로 테스트 서버 배포가 완료되었습니다."

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

def send_slack_notification():
    header_text, blocks = create_slack_message()

    try:
        result = slack_client.chat_postMessage(
            channel=DEPLOY_CHANNEL_ID,
            text=header_text,
            blocks=blocks
        )
        logging.info(result)
    except SlackApiError as e:
        logging.error(f"Error posting message: {e}")

if __name__ == "__main__":
    send_slack_notification()