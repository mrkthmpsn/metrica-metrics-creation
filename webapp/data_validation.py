"""
File for enums and pydantic classes used in the webapp
"""
from enum import Enum

import pandas as pd
from pydantic import BaseModel, ConfigDict


class PossessionLocationOptions(Enum):
    def __new__(cls, value, label, metrica_x):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        obj.metrica_x = metrica_x
        return obj

    GOAL_LINE = ("goal_line", "Goal line", 0)
    OWN_PENALTY_AREA = ("own_pen_area", "Own penalty area", 0.1)
    TWENTY_M = ("twenty_m", "20m", 20 / 105)
    TWENTY_FIVE_M = ("twenty_five_m", "25m", 25 / 105)
    THIRTY_M = ("thirty_m", "30m", 30 / 105)
    DEFENSIVE_THIRD = ("defensive_third", "Defensive third", 0.33)
    THIRTY_FIVE_M = ("thirty_five_m", "35m", 35 / 105)
    FORTY_M = ("forty_m", "40m", 40 / 105)
    FORTY_FIVE_M = ("forty_five_m", "45m", 45 / 105)
    FIFTY_M = ("fifty_m", "50m", 50 / 105)
    HALFWAY_LINE = ("halfway_line", "Halfway line", 0.5)


class SetPieceSequenceOptions(Enum):
    # The value in the data is essentially a user-facing label
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj

    GOAL_KICK = ("goal_kick", "Goal kick")
    FREE_KICK = ("free_kick", "Free kick")
    CORNER = ("corner", "Corner")
    THROW_IN = ("throw_in", "Throw-in")
    KICK_OFF = ("kick_off", "Kick-off")


class MetricComponentResult(BaseModel):
    metric_name: str
    metric_stats_data: pd.DataFrame
    metric_detailed_data: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)
