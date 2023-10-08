"""
Tests for the webapp functionality
"""
import os

import pandas as pd
import pytest

# TODO: This doesn't feel super robust - maybe it should be an env variable
def test_file_existence():
    assert os.path.isfile("./extra_processed_data/event_data.csv")


@pytest.fixture
def event_data_fixture():
    return pd.read_csv("./extra_processed_data/event_data.csv")


def test_event_data_not_empty(event_data_fixture):
    assert not event_data_fixture.empty


# Check that fields used in the webapp are present in the data
def test_time_since_possession_change_presence(event_data_fixture):
    assert "time_since_sequence_change" in event_data_fixture.columns
    assert event_data_fixture["time_since_sequence_change"].dtype == "float"


def test_sequence_team_id_presence(event_data_fixture):
    assert "sequence_team_id" in event_data_fixture.columns
    assert event_data_fixture["sequence_team_id"].dtype == "object"


def test_sequence_type_presence(event_data_fixture):
    assert "sequence_type" in event_data_fixture.columns
    assert event_data_fixture["sequence_type"].dtype == "object"


def test_period_id_presence(event_data_fixture):
    assert "period" in event_data_fixture.columns
    assert event_data_fixture["period"].dtype == "int64"


def test_start_coordinates_presence(event_data_fixture):
    assert "start_x" in event_data_fixture.columns
    assert "start_y" in event_data_fixture.columns

    assert event_data_fixture["start_x"].dtype == "float"
    assert event_data_fixture["start_y"].dtype == "float"


def test_start_end_time_presence(event_data_fixture):
    assert "start_time" in event_data_fixture.columns
    assert "end_time" in event_data_fixture.columns

    assert event_data_fixture["start_time"].dtype == "float"
    assert event_data_fixture["end_time"].dtype == "float"


def test_start_end_frame_presence(event_data_fixture):
    assert "start_frame" in event_data_fixture.columns
    assert "end_frame" in event_data_fixture.columns

    assert event_data_fixture["start_frame"].dtype == "int64"
    assert event_data_fixture["end_frame"].dtype == "int64"


def test_type_id_presence(event_data_fixture):
    assert "type_id" in event_data_fixture.columns
    assert event_data_fixture["type_id"].dtype == "int64"


def test_carry_start_pressure_presence(event_data_fixture):
    assert "carry_start_pressure" in event_data_fixture.columns
    assert event_data_fixture["carry_start_pressure"].dtype == "float"
