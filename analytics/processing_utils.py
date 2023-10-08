"""
File to house data processing utils for analytics-type metrics
"""
import logging
import math

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)

TIME_BETWEEN_FRAMES_S = 1 / 5


def _logarithmic_scale(x: float, max_value: float = 10) -> float:
    """
    Util function to fit an input value into a logarithmic scale. Used in calculating pressure value.

    :param x: The distance value (m) of a player to the ball/player in possession
    :param max_value: Maximum distance value (m) that exerts pressure on a ball-carrier
    :return: Value on a log scale between 0 and the `max_value`
    """

    # Ensure x is within the desired range
    x = max(0.0, min(max_value, x))
    # Calculate the logarithm, base 10, and normalize it to be between 0 and 1
    result = 1 - (math.log10(x + 1) / math.log10(max_value + 1))

    return result


def add_carry_event_pressure_metrics(
    event_data_df: pd.DataFrame,
    tracking_data_df: pd.DataFrame,
    pressure_future_time_s: float = 0.5,
) -> pd.DataFrame:
    """
    Function to add pressure metrics to carry events in a Metrica pressure dataframe. Although it takes both the event
    data and tracking data as inputs, the new event data dataframe is the sole output.

    :param event_data_df: Processed dataframe of event data
    :param tracking_data_df: Processed dataframe of tracking data
    :return: Returns new version of the events dataframe
    """
    logger.info("Starting task to add pressure metrics to carry events")

    carries_info_df = event_data_df[event_data_df["type_id"] == 10][
        ["index", "start_frame", "end_frame"]
    ]
    carries_metrics_records = []
    for _, row in carries_info_df.iterrows():
        carry_tracking_df = tracking_data_df[
            (tracking_data_df["frame_id"] > row["start_frame"])
            & (tracking_data_df["frame_id"] <= row["end_frame"])
        ]

        carry_tracking_df["future_x"] = carry_tracking_df["x_metres"] + (
            carry_tracking_df["vx"] * (pressure_future_time_s / TIME_BETWEEN_FRAMES_S)
        )
        carry_tracking_df["future_y"] = carry_tracking_df["y_metres"] + (
            carry_tracking_df["vy"] * (pressure_future_time_s / TIME_BETWEEN_FRAMES_S)
        )

        carry_tracking_df["future_ball_x"] = carry_tracking_df["ball_x_metres"] + (
            carry_tracking_df["ball_vx"]
            * (pressure_future_time_s / TIME_BETWEEN_FRAMES_S)
        )
        carry_tracking_df["future_ball_y"] = carry_tracking_df["ball_y_metres"] + (
            carry_tracking_df["ball_vy"]
            * (pressure_future_time_s / TIME_BETWEEN_FRAMES_S)
        )

        carry_tracking_df["future_distance_to_ball"] = carry_tracking_df.apply(
            lambda row: math.dist(
                (row["future_x"], row["future_y"]),
                (row["future_ball_x"], row["future_ball_y"]),
            ),
            axis=1,
        )

        carry_tracking_df["pressure_value"] = carry_tracking_df.apply(
            lambda row: _logarithmic_scale(row["future_distance_to_ball"])
            if row["team_id"] != row["ball_owning_team_id"]
            else None,
            axis=1,
        )

        frame_pressure_df = (
            carry_tracking_df.groupby("frame_id")["pressure_value"].sum().reset_index()
        )
        if len(frame_pressure_df) == 0:
            print(row)
            continue
        carry_avg_pressure = frame_pressure_df["pressure_value"].mean()
        carry_start_pressure = frame_pressure_df["pressure_value"][0]

        carries_metrics_records.append(
            {
                "event_idx": row["index"],
                "carry_avg_pressure": carry_avg_pressure,
                "carry_start_pressure": carry_start_pressure,
            }
        )

    carry_metrics_df = pd.DataFrame.from_records(carries_metrics_records)

    # TODO: Make sure that `event_idx` column gets dropped
    new_events_df = event_data_df.merge(
        carry_metrics_df, left_on="index", right_on="event_idx", how="left"
    )

    return new_events_df
