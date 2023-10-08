"""
File to house the functions to save postprocessed event and tracking data in the `processed_data` folder
"""
import json
import logging
import os

import pandas as pd

from data_processing.event_data.event_postprocessing import (
    add_possession_id,
    add_time_since_possession_change,
    add_ball_owning_team,
    flip_team_event_coordinates,
    process_set_piece_events,
    add_sequence_play_type_info,
)
from data_processing.event_data.metrica_events_parser import process_metrica_events_json
from data_processing.hybrid_data.postprocessing_utils import add_ball_owning_team_id
from data_processing.tracking_data.metrica_tracking_loading import (
    load_metrica_epts_tracking_with_kloppy,
    load_metrica_epts_pitch_dimensions,
    load_metrica_epts_player_team_id,
)
from data_processing.tracking_data.metrica_tracking_processing_utils import (
    add_player_velocities,
    add_player_speed_m_s,
    add_player_direction_degrees,
    add_player_distance_to_ball,
    add_pitch_unit_coordinates,
    convert_tracking_df_format,
)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def save_event_data(raw_event_data_file_path: str) -> None:
    """
    Function to save event data from the raw Metrica data JSON, with some 'basic' processed features, and saves as a
    CSV in the `processed_data` folder.

    :param raw_event_data_file_path: Path to Metrica events JSON file
    :return: None
    """
    assert os.path.isfile(raw_event_data_file_path), "File does not exist"
    assert (
        os.path.splitext(raw_event_data_file_path)[-1].lower() == ".json"
    ), "File should be a JSON"
    logger.info("Starting task to create processed event data")

    with open(raw_event_data_file_path) as file:
        raw_event_data_json = json.load(file)

    parsed_event_data_df = process_metrica_events_json(
        raw_event_data=raw_event_data_json["data"]
    )

    processed_event_data_df = process_set_piece_events(
        match_event_data=parsed_event_data_df
    )
    processed_event_data_df = flip_team_event_coordinates(
        match_event_data=processed_event_data_df
    )
    processed_event_data_df = add_ball_owning_team(
        match_event_data=processed_event_data_df
    )
    processed_event_data_df = add_possession_id(
        match_event_data=processed_event_data_df
    )
    processed_event_data_df = add_time_since_possession_change(
        match_event_data=processed_event_data_df
    )
    processed_event_data_df = add_sequence_play_type_info(
        match_event_data=processed_event_data_df
    )

    logger.info("Saving processed event data...")
    # TODO: Check if how to confirm that `to_csv` has worked successfully
    processed_event_data_df.to_csv("./processed_data/event_data.csv", index=False)


def save_tracking_data(
    raw_tracking_data_file_path: str, metadata_file_path: str
) -> None:
    """
    Function to save tracking data from the raw Metrica data txt file and xml metadata file, with some 'basic' processed
    features, and saves as a CSV in the `processed_data` folder.

    :param raw_tracking_data_file_path: File to Metrica tracking data txt file, in FIFA EPTS format
    :param metadata_file_path: File to Metrica metadata xml file, in FIFA EPTS format
    :return: None
    """
    assert os.path.isfile(
        raw_tracking_data_file_path
    ), "Tracking data file does not exist"
    assert os.path.isfile(metadata_file_path), "Metadata file does not exist"

    assert (
        os.path.splitext(raw_tracking_data_file_path)[-1].lower() == ".txt"
    ), "Tracking data file should be .txt"
    assert (
        os.path.splitext(metadata_file_path)[-1].lower() == ".xml"
    ), "Tracking data file should be .xml"

    logger.info("Starting task to create processed tracking data")

    match_pitch_dimensions = load_metrica_epts_pitch_dimensions(
        metadata_file_path=metadata_file_path
    )

    match_player_team_dict = load_metrica_epts_player_team_id(
        metadata_file_path=metadata_file_path
    )

    kloppy_metrica_tracking = load_metrica_epts_tracking_with_kloppy(
        raw_tracking_data_file_path=raw_tracking_data_file_path,
        metadata_file_path=metadata_file_path,
    )

    tracking_data_df = convert_tracking_df_format(
        kloppy_metrica_tracking=kloppy_metrica_tracking
    )
    tracking_data_df["team_id"] = tracking_data_df["id"].apply(
        lambda x: match_player_team_dict.get(x)
    )
    tracking_data_df = add_pitch_unit_coordinates(
        tracking_data_df=tracking_data_df,
        pitch_width_m=match_pitch_dimensions.pitch_width_m,
        pitch_length_m=match_pitch_dimensions.pitch_length_m,
    )
    tracking_data_df = add_player_velocities(tracking_data_df=tracking_data_df)
    tracking_data_df = add_player_speed_m_s(tracking_data_df=tracking_data_df)
    tracking_data_df = add_player_direction_degrees(tracking_data_df=tracking_data_df)
    tracking_data_df = add_player_distance_to_ball(tracking_data_df=tracking_data_df)

    logger.info("Saving processed tracking data...")
    # TODO: Check if how to confirm that `to_csv` has worked successfully
    tracking_data_df.to_csv("./processed_data/tracking_data.csv", index=False)


def save_hybrid_data_features(
    tracking_data_df: pd.DataFrame, event_data_df: pd.DataFrame
) -> None:
    """
    Function to implement basic processing features which rely on both the tracking data and event data in some way, and
    (re-)save the relevant dataframe as a CSV.

    :param tracking_data_df: Tracking data dataframe, saved via previous function in this file
    :param event_data_df: Event data dataframe, saved via previous function in this file
    :return: None
    """
    logger.info("Starting task to process hybrid data features")

    tracking_data_df = add_ball_owning_team_id(
        tracking_data_df=tracking_data_df, event_data_df=event_data_df
    )

    logger.info("Saving processed tracking data with hybrid features...")
    # TODO: Check if how to confirm that `to_csv` has worked successfully
    tracking_data_df.to_csv("./processed_data/tracking_data.csv", index=False)
