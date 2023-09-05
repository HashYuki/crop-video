import logging
import re
from datetime import datetime

import cv2
import pandas as pd


def mmss_to_seconds(mmss):
    try:
        time_obj = datetime.strptime(mmss, "%M:%S")
        total_seconds = time_obj.minute * 60 + time_obj.second
        return total_seconds
    except ValueError:
        logging.error("Invalid time format. Please use mm:ss format.")

def chk_mmss(x: str):
    """入力がmm:ssの形式でなければNoneを返す"""
    try:
        mmss_pattern = r'^(\d+):(\d+)$'
        return re.search(mmss_pattern, x)
    except TypeError:
        return None
        
    
# 動画を切り出す関数
def extract_video(input_path, output_path, start_time, end_time):
    cap = cv2.VideoCapture(input_path)
    fps = 30 # TODO:int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    
    if chk_mmss(start_time):
        start_time_second = mmss_to_seconds(start_time)
        start_frame = int(start_time_second * fps)
    else:
        logging.warning(f"`start_time` is not set.")
        start_frame = 0
        
    if chk_mmss(end_time):
        end_time_second = mmss_to_seconds(end_time)
        end_frame = int(end_time_second * fps)
    else:
        logging.warning(f"`end_time` is not set.")
        end_frame = float("inf")
        
    logging.info(f"clipping section: {start_time}-{end_time}. Total frame: {end_frame-start_frame}")


def main():
    # logger
    logging.basicConfig(level=logging.INFO)
    
    # CSVファイルから動画情報を読み取る
    video_info = pd.read_csv("data/wms_infant.csv")
    logging.info(f"number of videos: {len(video_info)}")
    
    # 1行ごとに処理する
    for index, row in video_info.iterrows():
        input_path = row["path"]
        output_path = f"{index:03}.avi"
        start_time = row["start_time"]
        end_time = row["end_time"]
        logging.info(f"input path: {input_path}")
        logging.info(f"output path: {output_path}")
        extract_video(input_path, output_path, start_time, end_time)

if __name__ == "__main__":
    main()
