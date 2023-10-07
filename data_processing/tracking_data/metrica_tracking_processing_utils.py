"""
File containing component/modular functions for processing the Kloppy-fetched tracking data.

The functions and uses are as follows:
- convert_tracking_df_format: Converts the tracking data format from wide to long
- add_pitch_unit_coordinates: Adds coordinates to the data in the units of the pitch dimension (in metres). Used for
    other functions.
- add_player_velocities: Adds player and ball velocities. Used in other functions.
- add_player_speed_m_s: Adds player and ball speed on each frame in metres per second.
- add_player_direction_degrees: Add player and ball direction (compared to the previous frame) in degrees.
- add_distance_to_ball: Add player distances to the ball for each frame, in metres.
"""
import logging
import math

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def convert_tracking_df_format(
    kloppy_metrica_tracking: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to convert the tracking data loaded from the raw files by Kloppy into a
    format suitable for the rest of the processing functions

    :param kloppy_metrica_tracking: Dataframe of tracking data straight from the Kloppy function
    :return: Dataframe in long format
    """
    logger.info("Beginning task to convert tracking data format from wide to long")

    transformed_tracking_df = kloppy_metrica_tracking.melt(
        id_vars=[
            "period_id",
            "timestamp",
            "frame_id",
            "ball_state",
            "ball_owning_team_id",
            "ball_x",
            "ball_y",
            "ball_z",
            "ball_speed",
        ],
        var_name="var",
        value_name="value",
    )

    transformed_tracking_df[["id", "metric"]] = transformed_tracking_df[
        "var"
    ].str.split("_", expand=True)
    transformed_tracking_df = transformed_tracking_df.drop("var", axis=1)

    transformed_tracking_df = transformed_tracking_df.pivot(
        index=[
            "period_id",
            "timestamp",
            "frame_id",
            "ball_state",
            "ball_owning_team_id",
            "ball_x",
            "ball_y",
            "ball_z",
            "ball_speed",
            "id",
        ],
        columns="metric",
        values="value",
    ).reset_index()

    # Columns included in the Kloppy processing which don't contain data from Metrica
    transformed_tracking_df = transformed_tracking_df.drop(["d", "s"], axis=1)

    return transformed_tracking_df


def add_pitch_unit_coordinates(
    tracking_data_df: pd.DataFrame, pitch_width_m: float, pitch_length_m: float
) -> pd.DataFrame:
    """
    Function to add X and Y columns to the tracking data for on-pitch in-metre units

    :param tracking_data_df: Partially processed tracking data dataframe
    :param pitch_width_m: Pitch width, taken from Metrica's metadata
    :param pitch_length_m: Pitch length, taken from Metrica's metadata
    :return: Further processed tracking data dataframe
    """
    logger.info("Beginning task to add pitch coordinates (m) to tracking data")

    tracking_data_df["x_metres"] = (tracking_data_df["x"]) * pitch_length_m
    tracking_data_df["y_metres"] = (tracking_data_df["y"]) * pitch_width_m

    # Because I've got the ball as separate fields I've got to do them separately too
    tracking_data_df["ball_x_metres"] = (tracking_data_df["ball_x"]) * pitch_length_m
    tracking_data_df["ball_y_metres"] = (tracking_data_df["ball_y"]) * pitch_width_m

    return tracking_data_df


def add_player_velocities(
    tracking_data_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Function to add velocities (based on distance from the previous frame) to players and the ball on both x and y axes.

    :param tracking_data_df: Partially processed tracking data dataframe
    :return: Further processed tracking data dataframe
    """
    logger.info("Beginning task to add player and ball velocities to tracking data")

    tracking_data_df = tracking_data_df.sort_values(
        ["period_id", "timestamp"], ascending=True
    )
    tracking_data_df["vx"] = tracking_data_df.groupby(["period_id", "id"])[
        "x_metres"
    ].transform(lambda x: np.diff(x, prepend=x.iloc[0]))
    tracking_data_df["vy"] = tracking_data_df.groupby(["period_id", "id"])[
        "y_metres"
    ].transform(lambda x: np.diff(x, prepend=x.iloc[0]))

    tracking_data_df["ball_vx"] = tracking_data_df.groupby(["period_id", "frame_id"])[
        "ball_x_metres"
    ].transform(lambda x: np.diff(x, prepend=x.iloc[0]))
    tracking_data_df["ball_vy"] = tracking_data_df.groupby(["period_id", "frame_id"])[
        "ball_y_metres"
    ].transform(lambda x: np.diff(x, prepend=x.iloc[0]))

    return tracking_data_df


def add_player_speed_m_s(tracking_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add player and ball speed to each frame of the tracking data, in metres per second.

    :param tracking_data_df: Partially processed tracking data dataframe
    :return: Further processed tracking data dataframe
    """
    logger.info("Beginning task to add player and ball speeds (m/s) to tracking data")

    tracking_data_df["speed_m_s"] = tracking_data_df.apply(
        lambda row: np.sqrt(row["vx"] ** 2 + row["vy"] ** 2) * 5
        if not np.isnan(row["vx"]) and not np.isnan(row["vy"])
        else None,
        axis=1,
    )

    tracking_data_df["ball_speed_m_s"] = tracking_data_df.apply(
        lambda row: np.sqrt(row["ball_vx"] ** 2 + row["ball_vy"] ** 2) * 5
        if not np.isnan(row["ball_vx"]) and not np.isnan(row["ball_vy"])
        else None,
        axis=1,
    )

    return tracking_data_df


def add_player_direction_degrees(tracking_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add player and ball movement direction to tracking data frames, in degrees.

    :param tracking_data_df: Partially processed tracking data dataframe
    :return: Further processed tracking data dataframe
    """
    logger.info("Beginning task to add player and ball velocities to tracking data")

    # TODO: Check where angle is actually relative to and add to docstring
    tracking_data_df["angle_deg"] = tracking_data_df.apply(
        lambda row: np.degrees(np.arctan2(row["vy"], row["vx"])) + 90
        if not np.isnan(row["vx"]) and not np.isnan(row["vy"])
        else None,
        axis=1,
    )

    return tracking_data_df


def add_player_distance_to_ball(tracking_data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add player distances to the ball to each frame of the tracking data, in metres

    :param tracking_data_df: Partially processed tracking data dataframe
    :return: Further processed tracking data dataframe
    """
    logger.info(
        "Beginning task to add player distances to the ball (m) in tracking data"
    )

    tracking_data_df["distance_to_ball"] = tracking_data_df.apply(
        lambda row: math.dist(
            (row["x_metres"], row["y_metres"]),
            (row["ball_x_metres"], row["ball_y_metres"]),
        )
        if row["x_metres"] is not None and row["ball_x_metres"] is not None
        else None,
        axis=1,
    )

    return tracking_data_df
