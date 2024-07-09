#!/bin/bash

# 배포 시작 알림 스크립트 실행
python3 ~/notion_slack_api_bot/slack_notification/deploy/deploy_start.py

cd ~/gongziphap_api/

# 최신 코드 가져오기
git pull origin test

cd gongziphap_fe

# 최신 코드 가져오기
git pull

cd ../apiserver

# docker-compose down 명령어 실행
docker-compose -f docker-compose-test.yml down

# 이전 명령어가 성공했는지 확인하고, 성공하면 다음 명령어 실행
if [ $? -eq 0 ]; then
    echo "docker-compose down completed successfully"
    docker-compose -f docker-compose-test.yml up -d --build

    # docker-compose up 명령어가 성공했는지 확인하고, 성공하면 다음 명령어 실행
    if [ $? -eq 0 ]; then
        echo "docker-compose up completed successfully"

        # 배포 완료 알림 스크립트 실행
        python3 ~/notion_slack_api_bot/slack_notification/deploy/deploy_end.py

        # 배포 완료 알림 스크립트가 성공했는지 확인
        if [ $? -eq 0 ]; then
            echo "slack_alert.py executed successfully"
        else
            echo "slack_alert.py failed"
        fi
    else
        echo "docker-compose up failed"
    fi
else
    echo "docker-compose down failed"
fi