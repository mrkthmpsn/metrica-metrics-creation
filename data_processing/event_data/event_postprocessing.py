"""
File to process fields based purely on event data

The functions and uses are as follows:
- process_set_piece_events: Processes awkward behaviour around set-piece events where event marked with the set-piece
    type ID does not have coordinates, and the subsequent pass event which represents the actual set-piece doesn't have
    any indicators that it is a set-piece.
- flip_team_event_coordinates: Flips team coordinates so that a team's event always has a direction of attack of
    left-to-right
- add_ball_owning_team: Adds field for which team is in control of the ball at that moment, for use in further functions
- add_possession_id: Adds sequential ID for possession sequences
- add_time_since_possession_change: Adds field for the time since the last possession sequence change to each event
- add_sequence_play_type_info: Adds field for either which set-piece type a sequence started with or whether it started
    in open play
"""
import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s | %(asctime)s | %(message)s"
)


def process_set_piece_events(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to deal with the bizarre system where Set-Piece type events don't have coordinates and the pass/shot
    events which follow them don't have set-piece tags.

    :param match_event_data: Dataframe of events parsed from the original JSON
    :return: Altered dataframe
    """
    logger.info("Beginning task to process set-piece events properly")

    match_event_data = match_event_data.sort_values(
        ["period", "start_time", "end_time"]
    ).reset_index()

    for i in match_event_data.index[1:]:
        if (match_event_data.loc[i - 1]["type_id"] == 5) and (
            match_event_data.loc[i]["start_time"]
            == match_event_data.loc[i - 1]["start_time"]
        ):
            match_event_data.at[i, "subtype_id"] = match_event_data.loc[i - 1][
                "subtype_id"
            ]

    return match_event_data


def flip_team_event_coordinates(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to flip the coordinates of the data so that teams' events are always 0 -> 1 attacking to defending

    The default Metrica system, as investigated in Sample Game 3, places coordinates 'as is' without flipping to
    normalise attacking left to right and also flips the teams at half-time (as happens in football!).

    :param match_event_data: Partially processed events dataframe
    :return: Further processed events dataframe
    """
    logger.info("Beginning task to normalise team event coordinates")

    team_1h_x_loc_mean = (
        match_event_data[match_event_data["period"] == 1]
        .groupby(["team_id"])["start_x"]
        .mean()
    )

    for stat_slug in ["start_x", "start_y", "end_x", "end_y"]:
        match_event_data[stat_slug] = match_event_data.apply(
            lambda row: 1 - row[stat_slug]
            if (row["team_id"] == team_1h_x_loc_mean.idxmax() and row["period"] == 1)
            | (row["team_id"] != team_1h_x_loc_mean.idxmax() and row["period"] == 2)
            else row[stat_slug],
            axis=1,
        )

    return match_event_data


def add_ball_owning_team(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to replicate the `ball_owning_team` column that Kloppy produces, which I miss having and adds a simple
    indicator for which team 'has' the ball on each event. This doesn't always align with the team ID of the event.

    :param match_event_data: Partially processed events dataframe
    :return: Further processed events dataframe
    """
    logger.info("Beginning task to add 'ball-owning team' field to events")

    match_teams = match_event_data["team_id"].unique()
    team_opponent_dict = {
        match_teams[0]: match_teams[1],
        match_teams[1]: match_teams[0],
    }

    match_event_data["opp_team_id"] = match_event_data["team_id"].apply(
        lambda x: team_opponent_dict[x]
    )
    match_event_data["ball_owning_team"] = np.where(
        match_event_data["type_id"] in [8, 9],
        match_event_data["opp_team_id"],
        match_event_data["team_id"],
    )

    return match_event_data


def add_possession_id(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add sequential possession sequence IDs to events, as well as when the ball changes hands and the start
    and end of possession sequences.

    The possession sequence logic looks for:
    - The presence of a Ball Lost, Ball Out, or Foul Suffered event
    - A set-piece happening

    :param match_event_data: Partially processed events dataframe
    :return: Further processed events dataframe
    """
    logger.info("Beginning task to add possession sequence IDs to events")

    match_event_data["last_ball_owning_team"] = match_event_data.groupby("period")[
        "ball_owning_team"
    ].shift(1)
    match_event_data["ball_possession_change"] = match_event_data.apply(
        # Empty string signifies card event, no point making that look like a new possession change
        lambda row: 1
        if (row["ball_owning_team"] != "")
        and (row["last_ball_owning_team"] != row["ball_owning_team"])
        else 0,
        axis=1,
    )
    # match_event_data["possession_id"] = match_event_data["possession_change"].cumsum()
    match_event_data["end_sequence"] = match_event_data.apply(
        lambda row: 1
        if row["type_id"] in [4, 6, 7]
        or row["type_id"] == 2
        and type(row["subtype_id"]) is str
        and ("30" in row["subtype_id"] or "31" in row["subtype_id"])
        else 0,
        axis=1,
    )
    match_event_data["new_sequence"] = match_event_data["end_sequence"].shift(1)
    match_event_data["new_sequence"] = match_event_data.apply(
        lambda row: 1
        if (row["type_id"] == 5)
        or ((row["type_id"] == 1) and ("20" in str(row["subtype_id"])))
        else row["new_sequence"],
        axis=1,
    )
    match_event_data["sequence_id"] = match_event_data["new_sequence"].cumsum()

    sequence_team_id_df = (
        match_event_data[match_event_data["type_id"] != 9]
        .groupby(["sequence_id"])["team_id"]
        .apply(lambda x: x.value_counts().idxmax())
        .reset_index()
        .rename(columns={"team_id": "sequence_team_id"})
    )

    match_event_data = match_event_data.merge(
        sequence_team_id_df, on="sequence_id", how="left"
    )
    match_event_data = match_event_data.drop(["last_ball_owning_team"], axis=1)

    return match_event_data


def add_time_since_possession_change(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add a field for the time since the start of the possession sequence, in seconds.

    :param match_event_data: Partially processed events dataframe
    :return: Further processed events dataframe
    """
    logger.info("Beginning task to add time since possession sequence change")

    event_data_possession_times = match_event_data[
        match_event_data["new_sequence"] == 1
    ][["sequence_id", "period", "start_time"]]
    event_data_possession_times = event_data_possession_times.rename(
        columns={"start_time": "sequence_start_time"}
    )

    match_event_data = match_event_data.merge(
        event_data_possession_times[["sequence_id", "sequence_start_time"]],
        left_on="sequence_id",
        right_on="sequence_id",
    )
    match_event_data["time_since_sequence_change"] = (
        match_event_data["start_time"] - match_event_data["sequence_start_time"]
    )

    # TODO: Can drop some columns here that were used for calculation?

    return match_event_data


def add_sequence_play_type_info(match_event_data: pd.DataFrame) -> pd.DataFrame:
    """
    Function to add whether the sequence started with a goal-kick, throw-in, corner, free-kick, penalty, kick-off, or
    began in open-play.

    :param match_event_data: Partially processed events dataframe
    :return: Fully processed events dataframe!
    """
    logger.info("Beginning task to add sequence play-type field")

    sequence_starter_events_df = match_event_data[
        match_event_data["new_sequence"] == 1
    ][["sequence_id", "subtype_id"]]
    sequence_starter_events_df["subtype_id"] = (
        sequence_starter_events_df["subtype_id"].astype(str).fillna(" ")
    )

    sequence_starter_events_df["sequence_type"] = np.select(
        [
            sequence_starter_events_df["subtype_id"].str.contains("20"),
            sequence_starter_events_df["subtype_id"].str.contains("32"),
            sequence_starter_events_df["subtype_id"].str.contains("33"),
            sequence_starter_events_df["subtype_id"].str.contains("34"),
            sequence_starter_events_df["subtype_id"].str.contains("35"),
            sequence_starter_events_df["subtype_id"].str.contains("36"),
        ],
        ["Goal kick", "Free kick", "Corner", "Throw-in", "Kick-off", "Penalty"],
        "Open play",
    )
    sequence_starter_events_df = sequence_starter_events_df.drop("subtype_id", axis=1)

    match_event_data = match_event_data.merge(
        sequence_starter_events_df, on="sequence_id", how="left"
    )

    return match_event_data
