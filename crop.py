import logging
import re
from datetime import datetime
import os

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
    # 動画情報の読み取り
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # VideoWriter設定
    fmt = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fmt, 30, (width, height))

    # mm:ssをframeに変換
    if chk_mmss(start_time):
        start_time_second = mmss_to_seconds(start_time)
        start_frame = int(start_time_second * 30)
    else:
        logging.warning("`start_time` is not set.")
        start_frame = 0

    if chk_mmss(end_time):
        end_time_second = mmss_to_seconds(end_time)
        end_frame = int(end_time_second * 30)
    else:
        logging.warning("`end_time` is not set.")
        end_frame = frame_count

    total_frames = end_frame - start_frame
    logging.info(f"clipping section: {start_time}-{end_time}.\
        Total frames: {total_frames}")

    # 動画の書き出し
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    for i in range(total_frames):
        print(f"\r{(i+1)/total_frames*100:.02f}% ({i+1:04}/{total_frames:04})",
              end="")

        ret, frame = cap.read()
        if not ret:
            break

        out.write(frame.astype('uint8'))

    cap.release()
    out.release()


def main():
    # logger
    logging.basicConfig(level=logging.INFO)

    # ===== WMs =====
    # CSVファイルから動画情報を読み取る
    video_info = pd.read_csv("data/wms_infant.csv")
    logging.info(f"number of videos: {len(video_info)}")

    # 保存先のフォルダ作成
    os.makedirs("output/wms", exist_ok=True)

    # 1行ごとに処理する
    for index, row in video_info.iterrows():
        input_path = row["path"]
        output_path = f"output/wms/{index:03}.mp4"
        start_time = row["start_time"]
        end_time = row["end_time"]
        logging.info(f"input path: {input_path}")
        logging.info(f"output path: {output_path}")
        extract_video(input_path, output_path, start_time, end_time)

    # ===== PR =====
    # CSVファイルから動画情報を読み取る
    video_info = pd.read_csv("data/pr_infant.csv")
    logging.info(f"number of videos: {len(video_info)}")

    # 保存先のフォルダ作成
    os.makedirs("output/pr", exist_ok=True)

    # 1行ごとに処理する
    for index, row in video_info.iterrows():
        input_path = row["path"]
        output_path = f"output/pr/{index:03}.mp4"
        start_time = row["start_time"]
        end_time = row["end_time"]
        logging.info(f"input path: {input_path}")
        logging.info(f"output path: {output_path}")
        extract_video(input_path, output_path, start_time, end_time)


if __name__ == "__main__":
    main()
