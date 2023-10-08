"""
File for Streamlit utils
"""
import os
from typing import List

import cv2

# TODO: I think there must be a better way of displaying these videos but this does the job currently
def create_temp_video_from_images(frame_id_list: List[int]):
    """
    Function to create an mp4 video of tracking data frames to display in the user metric creation.

    :param frame_id_list: List of tracking data frame IDs
    :return:
    """

    images = []
    for frame_id in frame_id_list:
        if os.path.isfile(f"./img/all_match_frames/frame{frame_id}.png"):
            img = cv2.imread(f"./img/all_match_frames/frame{frame_id}.png")
            images.append(img)

    height, width, layers = images[0].shape
    size = (width, height)

    out = cv2.VideoWriter(
        "./img/test_vid.mp4", cv2.VideoWriter_fourcc(*"H264"), 5, size
    )
    for i in range(len(images)):
        out.write(images[i])
    out.release()

    # TODO: It doesn't _really_ need to do this
    return "./img/test_vid.mp4"


def format_sequence_selectbox_label(sequence_df_row) -> str:
    """
    Format the label in the video selectbox to choose sequences to view

    :param sequence_df_row: Dataframe row for the sequence
    :return: Formatted label for that sequence/row of the selectbox
    """
    sequence_end_string = ""
    if sequence_df_row["reached_final_third"]:
        sequence_end_string = " (reached the final third)"
    if sequence_df_row["contained_shot"]:
        sequence_end_string = " (contained a shot)"

    return f"{sequence_df_row['sequence_team_id']}: {sequence_df_row['start_time']} - {sequence_df_row['end_time']}{sequence_end_string}"
