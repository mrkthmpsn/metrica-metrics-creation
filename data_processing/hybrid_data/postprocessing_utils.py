"""
File for data-processing utils which require both tracking data and event data

The functions and uses are as follows:
- add_ball_owning_team_id: Add the ball-owning team ID from the event data to the tracking data
"""
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def add_ball_owning_team_id(
    tracking_data_df: pd.DataFrame, event_data_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Function to add the ball owning team ID to the tracking data

    :param tracking_data_df: Partially-processed tracking data dataframe
    :param event_data_df: Partially-processed event data dataframe
    :return: Further processed tracking data dataframe
    """
    logger.info(
        "Beginning task to add ball-owning team to tracking data (from event data)"
    )

    new_tracking_data_df = pd.DataFrame()
    for idx, event_row in event_data_df.iterrows():
        temp_df = tracking_data_df[
            (tracking_data_df["frame_id"] > event_row["start_frame"])
            & (tracking_data_df["frame_id"] <= event_row["end_frame"])
        ]
        temp_df["ball_owning_team_id"] = event_row["ball_owning_team"]
        temp_df["sequence_team_id"] = event_row["sequence_team_id"]

        new_tracking_data_df = pd.concat([new_tracking_data_df, temp_df])

    return new_tracking_data_df
