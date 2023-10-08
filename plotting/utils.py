"""
File for plotting functions
"""
import datetime
import glob
import os
from typing import Optional, List

import mplsoccer as mplsoccer
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt


def plot_image(
    frame_data: pd.DataFrame,
    pitch_length: int = 105,
    pitch_width: int = 68,
    save_image: bool = True,
    save_filepath: Optional[str] = None,
):
    """
    Util to produce an image of a frame of Skillcorner tracking data. The input should be a single frame, no more.

    :param frame_data:
    :param pitch_length:
    :param pitch_width:
    :param save_image:
    :param save_filepath:
    :param highlight_ball_frame: Note - requires highlight column to be in dataframe
    :return:
    """

    assert (
        len(frame_data["frame_id"].unique()) == 1
    ), "Input data must contain one frame, no more and no fewer."
    if save_image:
        assert (
            save_filepath
        ), "If you want to save the image you need to provide a filepath."

    df_home = frame_data[frame_data["team_id"] == "FIFATMA"]
    df_away = frame_data[frame_data["team_id"] == "FIFATMB"]
    df_ball = frame_data.copy()

    pitch = mplsoccer.Pitch(
        pitch_type="metricasports",
        pitch_length=pitch_length,
        pitch_width=pitch_width,
        axis=True,
        label=True,
        positional=True,
    )  # showing axis labels is optional
    fig, ax = pitch.draw()
    ax.set_title(
        f"Frame: {frame_data['frame_id'].unique()[0]}, {frame_data['timestamp'].unique()[0]}"
    )

    # away_scatter
    if len(df_away) > 0:
        pitch.scatter(df_away.x, df_away.y, ax=ax, edgecolor="black", facecolor="red")
    # home_scatter
    if len(df_home) > 0:
        pitch.scatter(
            df_home.x, df_home.y, ax=ax, edgecolor="black", facecolor="cornflowerblue"
        )
    # ball_scatter
    if len(df_ball) > 0:
        pitch.scatter(
            df_ball.ball_x.iloc[0],
            df_ball.ball_y.iloc[0],
            ax=ax,
            edgecolor="black",
            facecolor="yellow",
            s=[75],
        )

    if save_image:
        plt.savefig(save_filepath)
        print("Saved image successfully.")

        plt.close()


def plot_blank_pitch(
    pitch_length: int = 105,
    pitch_width: int = 68,
    save_image: bool = True,
    save_filepath: Optional[str] = None,
):
    """
    Util to plot a blank pitch for when a frame is missing data, so that data doesn't simply skip several seconds from
    one play to the next
    """

    pitch = mplsoccer.Pitch(
        pitch_type="metricasports",
        pitch_length=pitch_length,
        pitch_width=pitch_width,
        axis=True,
        label=True,
    )  # showing axis labels is optional
    fig, ax = pitch.draw()
    ax.set_title(f"Frame: ")

    if save_image:
        plt.savefig(save_filepath)
        print("Saved image successfully.")

        plt.close()


def plot_animation(
    frame_idx_list: List[int],
    data_df: pd.DataFrame,
    save_folder: str,
    pitch_length: int = 105,
    pitch_width: int = 68,
):
    """
    Function to produce an animation from a set of Metrica frame data

    :param frame_idx_list:
    :param pitch_length:
    :param pitch_width:
    :param save_folder:
    :return:
    """

    try:
        os.mkdir(save_folder)
    except FileExistsError:
        print("Folders already created")
    except FileNotFoundError:
        print("Invalid file path somewhere along the way with initial folder")
        return

    frames_path = os.path.join(save_folder, "frames")
    gif_path = os.path.join(save_folder, "gif")

    try:
        os.mkdir(frames_path)
        os.mkdir(gif_path)
    except FileExistsError:
        print("Folders already created")
    except FileNotFoundError:
        print("Invalid file path somewhere along the way with sub-folders")
        return

    print(f"Starting to produce frame images: {datetime.datetime.now()}")
    for idx, frame_idx in enumerate(frame_idx_list):
        plt.ioff()
        try:
            plot_image(
                frame_data=data_df[data_df["frame_id"] == frame_idx],
                pitch_length=pitch_length,
                pitch_width=pitch_width,
                save_image=True,
                save_filepath=f"{save_folder}/frames/{frame_idx}.png",
            )
        except AssertionError:
            print(f"Assertion Error - Drawing blank pitch for frame {idx+1}")
            plot_blank_pitch(
                pitch_length=pitch_length,
                pitch_width=pitch_width,
                save_image=True,
                save_filepath=f"{save_folder}/frames/{frame_idx}.png",
            )
        else:
            print(f"Done {idx+1} of {len(frame_idx_list)}")

    images = []

    for filename in sorted(glob.glob(f"{save_folder}/frames/*.png")):
        im = Image.open(filename)
        images.append(im)

    for x in range(0, 9):
        im = images[-1]
        images.append(im)

    print(f"Saving gif: {datetime.datetime.now()}")

    images[0].save(
        f"{save_folder}/gif/{frame_idx_list[0]}_{frame_idx_list[-1]}.gif",
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=len(frame_idx_list),
        loop=0,
    )

    print(f"Saved gif: {datetime.datetime.now()}")
