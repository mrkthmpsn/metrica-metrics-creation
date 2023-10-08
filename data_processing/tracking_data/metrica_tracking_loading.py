"""
File for functions used to process Metrica tracking data and associated metadata

The tracking data function itself uses the Kloppy package to return a dataframe
"""
import logging
from typing import Optional, Union, Dict

import pandas as pd

from kloppy import metrica

from bs4 import BeautifulSoup
from pydantic import BaseModel

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


class PitchDimensions(BaseModel):
    pitch_length_m: Union[int, float]
    pitch_width_m: Union[int, float]


def load_metrica_epts_pitch_dimensions(metadata_file_path: str) -> PitchDimensions:
    """
    Function to load pitch dimensions from the Metrica metadata file

    :param metadata_file_path: File path of a Metrica metadata xml file in the FIFA EPTS format
    :return: PitchDimensions object to enforce expected format
    """
    logger.info("Beginning task to load pitch dimensions from Metrica metadata file")

    with open(metadata_file_path, "r") as f:
        metadata_xml = f.read()

    metadata_soup = BeautifulSoup(metadata_xml, "xml")
    pitch_length_m = int(metadata_soup.find("FieldSize").find("Width").text)
    pitch_width_m = int(metadata_soup.find("FieldSize").find("Height").text)

    return PitchDimensions(pitch_length_m=pitch_length_m, pitch_width_m=pitch_width_m)


def load_metrica_epts_player_team_id(metadata_file_path: str) -> Dict[int, str]:
    """
    Function to gather a dictionary of the player ID-player team ID relationship in a match.

    :param metadata_file_path: File path of a Metrica metadata xml file in the FIFA EPTS format
    :return: Dictionary of player IDs and their accompanying team IDs (in this data, the team ID is a string)
    """
    logger.info("Beginning task to gather player-team ID dictionary")

    with open(metadata_file_path, "r") as f:
        metadata_xml = f.read()

    metadata_soup = BeautifulSoup(metadata_xml, "xml")
    player_list = metadata_soup.findAll("Player")

    return {player["id"]: player["teamId"] for player in player_list}


def load_metrica_epts_tracking_with_kloppy(
    raw_tracking_data_file_path: str,
    metadata_file_path: str,
    sample_denominator: Optional[int] = 5,
) -> pd.DataFrame:
    """
    Function to load the Metrica tracking data from Sample Game 3 (in the FIFA EPTS format) using the Kloppy package

    :param raw_tracking_data_file_path: File path of a Metrica tracking data txt file
    :param metadata_file_path: File path of a Metrica metadata xml file in the FIFA EPTS format
    :param sample_denominator: Optional parameter to create a sample rate for the tracking data frames to pass to the
        Kloppy `load_tracking_epts` function
    :return: Basic dataframe of tracking data
    """
    logger.info(
        "Beginning task to load a dataframe of tracking data using the Kloppy package"
    )

    tracking_data = metrica.load_tracking_epts(
        meta_data=metadata_file_path,
        raw_data=raw_tracking_data_file_path,
        # Optional arguments
        sample_rate=1 / sample_denominator,
        coordinates="metrica",
    ).to_df()

    return tracking_data
