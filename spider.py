import json
import logging
import os
from urllib.parse import quote

import requests
import whisper


def spider_video_list():
    file_path = 'spider_video_list.json'
    json_map = None
    #test
    if os.path.exists(file_path):
        # 文件存在，执行读取操作
        with open(file_path, 'r') as f:
            json_map = json.load(f)
    else:
        #qq
        # 文件不存在，执行其他操作
        response = requests.get(
            'https://www.khanacademy.org/api/internal/graphql/ContentForPath?fastly_cacheable=persist_until_publish&pcv'
            '=bf3117ee863f58e87e44fffa0230422fe9517473&hash=909363320&variables=%7B%22path%22%3A%22math%2Fcc-eighth-grade'
            '-math%2Fcc-8th-numbers-operations%22%2C%22countryCode%22%3A%22SG%22%2C%22kaLocale%22%3A%22en%22%2C'
            '%22clientPublishedContentVersion%22%3A%22bf3117ee863f58e87e44fffa0230422fe9517473%22%7D&lang=en')
        json_map = json.loads(response.text)
        with open('spider_video_list.json', 'w') as f:
            json.dump(json_map, f)

    result_list = []
    for unit in json_map['data']['contentRoute']['listedPathData']['course']['unitChildren']:
        video_list = []
        for child in unit['allOrderedChildren']:
            if child['__typename'] == 'Lesson':
                for lesson in child['curatedChildren']:
                    if lesson['__typename'] == 'Video':
                        video_list.append({
                            'title': lesson['translatedTitle'],
                            'description': lesson['translatedDescription'],
                            'url': 'https://www.khanacademy.org'+lesson['canonicalUrl'],
                        })
        result_list.append({'title': unit['translatedTitle'],
                            'description': unit['translatedDescription'],
                            'videos': video_list})
    logging.info(result_list)
    return result_list


def spider_video_subtitles(url):
    encoded_url = quote(url, safe='')

    file_path = 'cache/spider_video_subtitles_' + encoded_url + '.json'
    json_map = None
    if os.path.exists(file_path):
        # 文件存在，执行读取操作
        with open(file_path, 'r') as f:
            json_map = json.load(f)
    else:
        # 文件不存在，执行其他操作
        response = requests.get(
            'https://www.khanacademy.org/api/internal/graphql/ContentForPath?fastly_cacheable=persist_until_publish&pcv'
            '=bf3117ee863f58e87e44fffa0230422fe9517473&hash=909363320&variables=%7B%22path%22%3A%22'
            + encoded_url +
            '%22%2C%22countryCode%22%3A%22SG%22%2C%22kaLocale%22%3A%22en%22%2C%22clientPublishedContentVersion%22%3A'
            '%22bf3117ee863f58e87e44fffa0230422fe9517473%22%7D&lang=en')
        json_map = json.loads(response.text)
        with open(file_path,'w') as f:
            json.dump(json_map, f)

    content_json = json_map['data']['contentRoute']['listedPathData']['content']
    json_list = content_json['subtitles']
    result_list = []
    for element in json_list:
        result_list.append({'startTime': element['startTime'], 'endTime': element['endTime'], 'text': element['text']})
    logging.info(result_list)
    return result_list


def video_processor():
    model = whisper.load_model("medium.en")
    result = model.transcribe("source.mp4")
    print(result["text"])


if __name__ == '__main__':
    # videos = spider_video_list()
    # spider_video_subtitles('/math/cc-eighth-grade-math/cc-8th-data/two-way-tables/v/interpreting-two-way-tables')
    video_processor()
