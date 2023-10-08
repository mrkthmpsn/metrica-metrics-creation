"""
Test file for Streamlit webapp components
"""
import itertools

import numpy as np
from streamlit_extras import row

import streamlit as st
import pandas as pd

# Relative path to this file, for Streamlit purposes
from utils import format_sequence_selectbox_label, create_temp_video_from_images
from data_validation import (
    PossessionLocationOptions,
    MetricComponentResult,
    SetPieceSequenceOptions,
)


def build_up_metric_component(
    idx: int, event_data: pd.DataFrame
) -> MetricComponentResult:
    with st.expander(f"Build-up metric {idx+1}"):
        metric_name = st.text_input(label="Metric name:", key=f"metric_name_{idx}")

        phase_design_col, phase_outputs_col = st.columns(2)
        with phase_design_col:
            st.write("**Design a phase of play**")
            start_possession_bounds = st.select_slider(
                label="Starting location area",
                options=PossessionLocationOptions,
                value=[
                    PossessionLocationOptions.GOAL_LINE,
                    PossessionLocationOptions.DEFENSIVE_THIRD,
                ],
                key=f"start_possession_slider_{idx}",
                format_func=lambda x: x.label,
            )

            st.divider()

            # TODO: Do these values all need to completely match up?
            # Values are arbitrary - could develop metric further
            pressure_options = [
                {"label": "None", "min_value": 0, "max_value": 0},
                {"label": "Low", "min_value": 0.1, "max_value": 0.25},
                {"label": "Medium", "min_value": 0.25, "max_value": 0.6},
                {"label": "High", "min_value": 0.6, "max_value": 100},
            ]
            under_pressure_option = st.select_slider(
                "Pressure on first action",
                options=pressure_options,
                value=[pressure_options[0], pressure_options[3]],
                help="To select just 'None', drag right-hand slider onto 'None' option. Click on the text options to "
                "re-activate the slider if both options have been put at the same level.",
                format_func=lambda x: x["label"],
                key=f"pressure_option_{idx}",
            )

            st.divider()
            st.write("Phase of play")
            open_play_row = row.row([1, 1], vertical_align="top")
            settled_possession_check = open_play_row.toggle(
                label="Include open-play sequences",
                key=f"settled_possession_check_{idx}",
                value=True,
            )

            settled_possession_slider = open_play_row.slider(
                label="Time since open-play turnover (s)",
                min_value=0.0,
                max_value=10.0,
                value=3.0 if settled_possession_check else 0.0,
                step=0.5,
                key=f"settled_possession_slider_{idx}",
                disabled=not settled_possession_check,
            )

            # TODO: Bugfix non-goal kick sequences, have a project 'ticket' for that
            set_piece_select = st.multiselect(
                "...or dead-ball situations which could start a phase of play:",
                options=SetPieceSequenceOptions,
                help="Set-pieces will not be included if they fall outside of the chosen starting location.",
                placeholder="Select to choose option(s)",
                key=f"set_piece_select_{idx}",
                format_func=lambda x: x.label,
            )

        with phase_outputs_col:
            st.write("**Outputs for report**")
            st.write(
                "'Avenue' features (e.g. wing play, long ball). Bit of a v1.1 concept."
            )
            avenue_option_checks = st.multiselect(
                label="Avenue options",
                options=["suffered_pressure_wave"],
                key=f"avenue_options_{idx}",
                help="'suffered_pressure_wave' = three consecutive carries comes under pressure",
            )

            st.write("Outputs")
            output_options = [
                "reached_middle_third",
                "reached_opp_half",
                "reached_final_third",
                "contained_shot",
                "ended_own_third",
                "ended_own_half",
            ]
            output_option_checks = st.multiselect(
                label="Output options",
                options=output_options,
                key=f"output_options_{idx}",
            )

        filtered_events_data = event_data[
            (
                (settled_possession_check)
                & (
                    event_data["time_since_sequence_change"]
                    >= settled_possession_slider
                )
            )
            | (
                (SetPieceSequenceOptions.GOAL_KICK in set_piece_select)
                & (
                    event_data["sequence_type"]
                    == SetPieceSequenceOptions.GOAL_KICK.label
                )
            )
            | (
                (SetPieceSequenceOptions.FREE_KICK in set_piece_select)
                & (
                    event_data["sequence_type"]
                    == SetPieceSequenceOptions.FREE_KICK.label
                )
            )
            | (
                (SetPieceSequenceOptions.CORNER in set_piece_select)
                & (event_data["sequence_type"] == SetPieceSequenceOptions.CORNER.label)
            )
            | (
                (SetPieceSequenceOptions.THROW_IN in set_piece_select)
                & (
                    event_data["sequence_type"]
                    == SetPieceSequenceOptions.THROW_IN.label
                )
            )
            | (
                (SetPieceSequenceOptions.KICK_OFF in set_piece_select)
                & (
                    event_data["sequence_type"]
                    == SetPieceSequenceOptions.KICK_OFF.label
                )
            )
        ]

        sequence_summary_df = (
            filtered_events_data.groupby(["period", "sequence_id", "sequence_team_id"])
            .agg(
                # TODO: Do I need to change the x and y coordinates to more public-facing ones?
                start_loc_x=pd.NamedAgg(column="start_x", aggfunc=lambda x: x.iloc[0]),
                start_loc_y=pd.NamedAgg(column="start_y", aggfunc=lambda x: x.iloc[0]),
                # This could be done with start time and end time of events instead of this single-column hack
                duration=pd.NamedAgg(
                    column="time_since_sequence_change",
                    aggfunc=lambda x: x.max() - x.min(),
                ),
                start_time=pd.NamedAgg(
                    column="start_time", aggfunc=lambda x: x.iloc[0]
                ),
                end_time=pd.NamedAgg(column="end_time", aggfunc=lambda x: x.iloc[-1]),
                start_frame=pd.NamedAgg(
                    column="start_frame", aggfunc=lambda x: x.iloc[0]
                ),
                end_frame=pd.NamedAgg(column="end_frame", aggfunc=lambda x: x.iloc[-1]),
                reached_middle_third=pd.NamedAgg(
                    "start_x",
                    aggfunc=lambda x: len([1 for i in x if (i >= 0.33) and (i < 0.67)])
                    >= 1,
                ),
                reached_opp_half=pd.NamedAgg(
                    "start_x", aggfunc=lambda x: len([1 for i in x if i > 0.5]) >= 1
                ),
                reached_final_third=pd.NamedAgg(
                    "start_x", aggfunc=lambda x: len([1 for i in x if i >= 0.67]) >= 1
                ),
                ended_own_third=pd.NamedAgg(
                    "end_x", aggfunc=lambda x: 1 if x.iloc[-1] <= 0.33 else 0
                ),
                ended_own_half=pd.NamedAgg(
                    "end_x", aggfunc=lambda x: 1 if x.iloc[-1] <= 0.5 else 0
                ),
                contained_shot=pd.NamedAgg(
                    "type_id", aggfunc=lambda x: len([1 for i in x if i == 2]) >= 1
                ),
                pressure_on_first_carry=pd.NamedAgg(
                    # TODO: Might need to change this end result to 0
                    "carry_start_pressure",
                    aggfunc=lambda x: [i for i in x if not np.isnan(i)][0]
                    if len([i for i in x if not np.isnan(i)]) > 0
                    else None,
                ),
                suffered_pressure_wave=pd.NamedAgg(
                    "carry_avg_pressure",
                    # This is a very rough, makeshift metric
                    # aggfunc=lambda x: 1 if len([i for i in x if not np.isnan(i) and i > 0.75]) > 2 else 0
                    # This is a very complicated set of logic that should be separated out into a function (and could
                    # still be improved on from there)
                    aggfunc=lambda x: 1
                    if len(
                        [
                            i
                            for i in [
                                sum(1 for _ in group)
                                for is_larger, group in itertools.groupby(
                                    [carry for carry in x if not np.isnan(carry)],
                                    lambda value: value >= 0.5,
                                )
                                if is_larger
                            ]
                            if i >= 2
                        ]
                    )
                    > 0
                    else 0,
                ),
            )
            .reset_index()
        )

        filtered_sequences_df = sequence_summary_df[
            (sequence_summary_df["start_loc_x"] >= start_possession_bounds[0].metrica_x)
            & (
                sequence_summary_df["start_loc_x"]
                <= start_possession_bounds[1].metrica_x
            )
            & (
                sequence_summary_df["pressure_on_first_carry"]
                >= under_pressure_option[0]["min_value"]
            )
            & (
                sequence_summary_df["pressure_on_first_carry"]
                <= under_pressure_option[1]["max_value"]
            )
        ]

        with phase_outputs_col:
            st.divider()

            # TODO: Do I want to give the user an immediate sense of the output, and if so what kind?
            st.dataframe(
                filtered_sequences_df.groupby("sequence_team_id")
                .agg({"sequence_id": "count"})
                .rename(columns={"sequence_id": "total"})
            )

        st.divider()

        video_show_toggle = st.toggle(
            "Check a sequence based on your phase of play design from the list below",
            key=f"video_show_{idx}",
        )
        sequence_input = st.selectbox(
            label="Sequence...",
            options=filtered_sequences_df.to_records(),
            format_func=format_sequence_selectbox_label,
            index=None,
            key=f"select_sequence_box_{idx}",
            label_visibility="collapsed",
        )
        if video_show_toggle and sequence_input:
            video_file_path = create_temp_video_from_images(
                list(
                    range(
                        int(
                            filtered_sequences_df.loc[sequence_input["index"]][
                                "start_frame"
                            ]
                        )
                        - 20,
                        int(
                            filtered_sequences_df.loc[sequence_input["index"]][
                                "end_frame"
                            ]
                        )
                        + 20,
                    )
                )
            )
            video_file = open(video_file_path, "rb")
            video_bytes = video_file.read()
            # TODO: Ideally this would depend on the screen size: on mobile this wouldn't be needed
            row1 = row.row([1, 4, 1], vertical_align="center")
            row1.empty()
            row1.video(video_bytes, format="video/mp4")
            row1.empty()

        result_summary_data = (
            filtered_sequences_df.groupby("sequence_team_id")
            .agg(
                dict(
                    **{"sequence_id": "count"},
                    **{avenue: "sum" for avenue in avenue_option_checks},
                    **{output: "sum" for output in output_option_checks},
                )
            )
            .rename(columns={"sequence_id": "total"})
            .reset_index()
        )
        result_detailed_data = filtered_sequences_df[
            [
                "sequence_team_id",
                "period",
                "start_time",
                "end_time",
                *avenue_option_checks,
                *output_option_checks,
            ]
        ]

        return MetricComponentResult(
            metric_name=metric_name,
            metric_stats_data=result_summary_data,
            metric_detailed_data=result_detailed_data,
        )
