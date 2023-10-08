"""
File to save extra post-processed data versions of event and/or tracking data. Saves to `extra_processed_data` folder.
"""
import logging

import pandas as pd

from analytics.processing_utils import add_carry_event_pressure_metrics

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def save_extra_hybrid_data_features(
    event_data: pd.DataFrame, tracking_data: pd.DataFrame
) -> None:
    """
    Function to save extra hybrid data features to event or tracking data.

    :param event_data: Processed event data dataframe
    :param tracking_data: Processed tracking data dataframe
    :return: None
    """
    logger.info("Starting task to create extra, analytics-type processed event data")

    event_data = add_carry_event_pressure_metrics(
        event_data_df=event_data, tracking_data_df=tracking_data
    )

    logger.info("Saving extra processed event data...")
    # TODO: Check if how to confirm that `to_csv` has worked successfully
    event_data.to_csv("./extra_processed_data/event_data.csv", index=False)
