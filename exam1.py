from datetime import datetime
from multiprocessing import Process
import requests
import json
import os
import cv2

def writeVideo(data_list, current_time, num):   # 비디오저장
    # RTSP를 불러오는 곳
    video_capture = cv2.VideoCapture(data_list[num][2]) #스트리밍 프로토콜(RTSP)주소

    # 영상 설정
    video_capture.set(3, 800)  # 영상 가로길이 설정
    video_capture.set(4, 600)  # 영상 세로길이 설정
    fps = 20    # 초당 frame
    streaming_window_width = int(video_capture.get(3))   # 가로 길이 가져오기
    streaming_window_height = int(video_capture.get(4))  # 세로 길이 가져오기

    #현재 년,월,일,시간,장소 및 cctv채널
    fileName = str(current_time.strftime('%Y-%m-%d_%H시_')+data_list[num][1]+('_')+data_list[num][0])   #data_list[num][0]:CCTV관리번호 [num][1]:설치위치명

    # 디렉토리 확인 및 생성
    createDirectory(f'D:/cctv')
    # 파일 저장하기 위한 변수 선언
    path = f'D:/cctv/{fileName}.avi'

    # DIVX 코덱 적용 # 코덱 종류 # DIVX, XVID, MJPG, X264, WMV1, WMV2
    # 무료 라이선스의 이점이 있는 XVID를 사용
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')

    # 비디오 저장
    # cv2.VideoWriter(저장 위치, 코덱, 프레임, (가로, 세로))
    out = cv2.VideoWriter(path, fourcc, fps, (streaming_window_width, streaming_window_height))

    time = 3*60     #3분57초~4분30초??
    start_time = datetime.now()

    while (datetime.now() - start_time).total_seconds() < time:
        ret, frame = video_capture.read()
        # 영상을 저장한다.
        out.write(frame)

    video_capture.release()  # cap 객체 해제
    out.release()  # out 객체 해제
    cv2.destroyAllWindows()

def createDirectory(directory): #디렉토리생성
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create the directory.")

# main
if __name__ == "__main__":
    # url
    url = 'https://api.odcloud.kr/api/15063717/v1/uddi:fd7b941f-734e-4c1d-9155-975be33fc19c?page=1&perPage=10&serviceKey=V0%2Bkt4XQZArkyunVv1CZ%2FzWwd%2Fe%2BBnuXHot%2BD2YTebvfS3ikOIM8EWuxK2k1eeCq8VG7WVTWyoZGpO1bODWwSg%3D%3D'

    response = requests.get(url)  # GET 방식: requests.get(), HTTP호출
    response.status_code  # 응답확인코드

    # 데이터 값 출력해보기
    contents = response.text

    # 문자열을 json으로 변경
    json_ob = json.loads(contents)

    # data정리
    data_list = [(i['CCTV관리번호'], i['설치위치명'], i['스트리밍 프로토콜(RTSP)주소']) for i in json_ob['data']]

    # 일자 및 시간
    current_time = datetime.now()

    # 스레드 생성 및 시작
    for num in enumerate(data_list):
        p = Process(target=writeVideo, args=(data_list, current_time, num[0]))
        p.start()

    for _ in range(num[0]):
        p.join()