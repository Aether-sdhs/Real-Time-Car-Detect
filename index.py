import requests
import urllib.request
import numpy as np
from dotenv import load_dotenv
import os
import json
import questionary

def get_cctv_url(lat, lng):
    # .env 파일을 로드합니다.
    load_dotenv()

    # ITS_CCTV_KEY 환경 변수를 가져옵니다.
    ITS_CCTV_KEY = os.environ.get('ITS_CCTV_KEY')

    # CCTV 탐색 범위를 정의하기 위해 위경도 좌표 주변 1도 범위를 지정합니다.
    minX = str(lng - 1)
    maxX = str(lng + 1)
    minY = str(lat - 1)
    maxY = str(lat + 1)

    # API 호출 URL을 생성합니다.
    api_call = 'https://openapi.its.go.kr:9443/cctvInfo?' \
               'apiKey=' + ITS_CCTV_KEY + \
               '&type=ex&cctvType=2' \
               '&minX=' + minX + \
               '&maxX=' + maxX + \
               '&minY=' + minY + \
               '&maxY=' + maxY + \
               '&getType=json'

    # API를 호출하고 JSON 데이터를 가져옵니다.
    w_dataset = requests.get(api_call).json()
    cctv_data = w_dataset['response']['data']

    # CCTV의 좌표를 추출하여 리스트에 저장합니다.
    coordx_list = []
    for index, data in enumerate(cctv_data):
        xy_couple = (float(cctv_data[index]['coordy']), float(cctv_data[index]['coordx']))
        coordx_list.append(xy_couple)

    # 입력한 위경도 좌표에서 가장 가까운 CCTV 위치를 찾습니다.
    coordx_list = np.array(coordx_list)
    leftbottom = np.array((lat, lng))
    distances = np.linalg.norm(coordx_list - leftbottom, axis=1)
    min_index = np.argmin(distances)

    return cctv_data[min_index]

# 위치 정보가 포함된 JSON 파일을 불러옵니다.
with open('demo_cctv_list.json', 'r', encoding='utf-8') as file:
    cctv_locations = json.load(file)

# 선택된 CCTV 데이터를 저장할 리스트를 초기화합니다.
selected_cctv_data = []

# questionary를 사용하여 위치를 선택합니다.
title = '위치를 선택하세요:'
options = [loc['name'] for loc in cctv_locations]
selected_option = questionary.select(title, choices=options).ask()

# 선택한 위치를 JSON 데이터에서 찾습니다.
selected_location = cctv_locations[options.index(selected_option)]
selected_cctv_data.append(get_cctv_url(selected_location['latitude'], selected_location['longitude']))

# 필요한 경우 위의 코드를 반복하여 더 많은 위치의 데이터를 선택하고 가져올 수 있습니다.

# 선택한 위치의 CCTV 비디오를 다운로드합니다.
for cctv_data in selected_cctv_data:
    print('CCTV명:', cctv_data['cctvname'])
    print('CCTV 영상 URL:', cctv_data['cctvurl'])
    urllib.request.urlretrieve(cctv_data['cctvurl'], str(cctv_data['cctvname'] + ".mp4"))
    print("저장됨: ", str(cctv_data['cctvname'] + ".mp4"))
