import os

import pandas as pd
import requests
from typing import Dict
import requests
import json
from dotenv import load_dotenv

load_dotenv()
URL = 'https://www.googleapis.com/youtube/v3/'

API_KEY = os.getenv('API_KEY')
PLAYLIST_ID = os.getenv('PLAYLIST_ID')

# 1つ目の動画のコメント情報を取得
# VIDEO_ID = '1vAUY1qNF1Q'
# CHANNEL_ID = 'UCjg5-lUiUzdmzzBRY9Xqrhw'


def print_video_list(no, play_list_id, next_page_token):
    params = {
        'key': API_KEY,
        'part': 'snippet',
        'playlistId': play_list_id,
        'maxResults': 50,
    }
    if next_page_token is not None:
        params['pageToken'] = next_page_token
    response = requests.get(URL + 'playlistItems', params=params)
    resource = response.json()

    for play_list_info in resource['items']:
        print(play_list_info['snippet']['resourceId']['videoId'])
        make_video_comment_csv(no, play_list_info['snippet']['resourceId']['videoId'], None)

    if 'nextPageToken' in resource:
        print_video_list(no, playlist_id, resource["nextPageToken"])



def make_video_comment_csv(no, video_id, next_page_token):

    text_data = []
    # 取得処理を実行
    print_video_comment(no, video_id, None, text_data)
    # データフレーム作成(高評価順にソート)
    df = pd.DataFrame(text_data, columns=['comment_id', 'type', 'comment_data', 'like_cnt', 'reply_cnt', 'user_name',
                                          'profile_page']).sort_values('like_cnt', ascending=False)
    # csv出力
    df.to_csv(str("./comment/") + str(video_id) + '.csv', index=False)
    # データフレームを一部出力して確認する
    df.head()


def print_video_reply(no, cno, video_id, next_page_token, id, text_data):
    params = {
        'key': API_KEY,
        'part': 'snippet',
        'videoId': video_id,
        'textFormat': 'plaintext',
        'maxResults': 50,
        'parentId': id,
    }

    if next_page_token is not None:
        params['pageToken'] = next_page_token
    response = requests.get(URL + 'comments', params=params)
    resource = response.json()

    for comment_info in resource['items']:
        # コメント
        text = comment_info['snippet']['textDisplay']
        # グッド数
        like_cnt = comment_info['snippet']['likeCount']
        # ユーザー名
        user_name = comment_info['snippet']['authorDisplayName']
        # ユーザープロフィール情報
        author_channel = comment_info["snippet"]['authorChannelUrl']
        # リストに取得した情報を追加
        text_data.append([id, 'child', text, like_cnt, 0, user_name, author_channel])
        #       print('{:0=4}-{:0=3}\t{}\t{}\t{}'.format(no, cno, text.replace('\n', ' '), like_cnt, user_name))
        cno = cno + 1

    if 'nextPageToken' in resource:
        print_video_reply(no, cno, video_id, resource["nextPageToken"], id, text_data)


def print_video_comment(no, video_id, next_page_token, text_data):
    params = {
        'key': API_KEY,
        'part': 'snippet',
        'videoId': video_id,
        'order': 'relevance',
        'textFormat': 'plaintext',
        'maxResults': 100,
    }
    if next_page_token is not None:
        params['pageToken'] = next_page_token
    response = requests.get(URL + 'commentThreads', params=params)
    resource = response.json()

    for comment_info in resource['items']:
        # コメント
        text = comment_info['snippet']['topLevelComment']['snippet']['textDisplay']
        # グッド数
        like_cnt = comment_info['snippet']['topLevelComment']['snippet']['likeCount']
        # 返信数
        reply_cnt = comment_info['snippet']['totalReplyCount']
        # ユーザー名
        user_name = comment_info['snippet']['topLevelComment']['snippet']['authorDisplayName']
        # Id
        parentId = comment_info['snippet']['topLevelComment']['id']
        # ユーザープロフィール情報
        author_channel = comment_info["snippet"]['topLevelComment']['snippet']['authorChannelUrl']
        # リストに取得した情報を追加
        text_data.append([parentId, 'parent', text, like_cnt, reply_cnt, user_name, author_channel])
        # 処理確認用
        if len(text_data) % 100 == 0:
            print(len(text_data))
        #     print('{:0=4}\t{}\t{}\t{}\t{}'.format(no, text.replace('\n', ' '), like_cnt, user_name, reply_cnt))
        if reply_cnt > 0:
            cno = 1
            print_video_reply(no, cno, video_id, next_page_token, parentId, text_data)
        no = no + 1

    if 'nextPageToken' in resource:
        print_video_comment(no, video_id, resource["nextPageToken"], text_data)


text_data = []
# コメントを全取得する
# video_id = VIDEO_ID
playlist_id = PLAYLIST_ID
# channel_id = CHANNEL_ID
no = 1
# 取得処理を実行
print_video_list(no, playlist_id, None)
