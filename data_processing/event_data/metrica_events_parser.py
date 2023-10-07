"""
File to parse the Metrica events JSON file

The JSON is quite simple and parsing the event data from scratch allows us a bit more knowledge of what's going on
than using a third-party parser which adds some of its own event schema on top.
"""
import logging
from typing import Union, List

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def _process_subtype_field(subtype_json_field: Union[list, dict, None]) -> List[int]:
    """
    Util function to process the subtypes field, which can be either `None`, a single dict, or a list of dicts.

    For ease, we want to transform it into a list, which will contain either zero, one, or multiple subtype IDs.

    :param subtype_json_field: JSON field for 'subtype' from the Metrica event data
    :return: A list of subtype IDs for the event (or an empty list)
    """

    # TODO: Investigate and fix why this results in an nan if there's nothing there in the eventual dataframes
    if type(subtype_json_field) is None:
        return []
    elif type(subtype_json_field) is dict:
        return [subtype_json_field["id"]]
    elif type(subtype_json_field) is list:
        return [subtype["id"] for subtype in subtype_json_field]


def process_metrica_events_json(raw_event_data: List[dict]) -> pd.DataFrame:
    """
    Function to iterate over each event in the Metrica event data and parse it into a flatter/less nested
    dictionary object, before turning these records into a pandas dataframe.

    :param raw_event_data: List of event dictionaries as it comes directly from the loaded JSON
    :return: Event dataframe, ordered by match period, event start time, and Metrica index
    """
    logger.info("Beginning task to process metrica events from JSON")

    processed_event_records = []

    for event in raw_event_data:
        flat_object = {
            "index": event["index"],
            "team_id": event["team"]["id"],
            "type_id": event["type"]["id"],
            "subtype_id": _process_subtype_field(event["subtypes"]),
            "start_frame": event["start"]["frame"],
            "start_time": event["start"]["time"],
            "start_x": event["start"]["x"],
            "start_y": event["start"]["y"],
            "end_frame": event["end"]["frame"],
            "end_time": event["end"]["time"],
            "end_x": event["end"]["x"],
            "end_y": event["end"]["y"],
            "period": event["period"],
            "player_id": event["from"]["id"] if event["from"] is not None else None,
            "receiver_id": event["to"]["id"] if event["to"] is not None else None,
        }

        processed_event_records.append(flat_object)

    return pd.DataFrame.from_records(processed_event_records).sort_values(
        ["period", "start_time", "index"]
    )
