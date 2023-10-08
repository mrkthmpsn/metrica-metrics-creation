"""
Streamlit webapp landing/app page
"""

import streamlit as st
import pandas as pd

# Relative path to this file, for Streamlit purposes
from components import build_up_metric_component

event_data = pd.read_csv("./extra_processed_data/event_data.csv")

st.markdown("## _RoundEyes_ football metrics creator")
st.markdown(
    """
    Create intuitive football metrics tailored to your game model.
    
    Everything is created through event data and tracking data, but check you have what you're after with tracking data 
    'video clips'. 
    
    Spend less time staring at video. Keep the square eyes away with **RoundEyes**.
    """
)

metric_numbers = st.number_input(
    label="How many metrics do you want to make?",
    min_value=1,
    max_value=5,
    value=1,
    step=1,
    format="%i",
)

buildup_metric_data = []

for i in range(metric_numbers):
    metric_data = build_up_metric_component(idx=i, event_data=event_data)
    buildup_metric_data.append(metric_data)


metric_names_string = st.session_state.get("metric_names", "")
rendering_metrics_data = st.session_state.get("rendering_metrics_data", [])

if st.button("Update metrics data"):
    metric_names_string = f"Metrics created: {', '.join([metric.metric_name for metric in buildup_metric_data])}"
    st.session_state.metric_names_string = metric_names_string

    rendering_metrics_data = buildup_metric_data
    st.session_state.rendering_metrics_data = buildup_metric_data

st.write(metric_names_string)
if len(rendering_metrics_data) > 0:
    stats_tab, detailed_tab = st.tabs(["Metric Stats", "Sequence Details"])
    with stats_tab:
        for ind_metric in rendering_metrics_data:
            st.write(ind_metric.metric_name)
            st.dataframe(ind_metric.metric_stats_data)
    with detailed_tab:
        for ind_metric in rendering_metrics_data:
            st.write(ind_metric.metric_name)
            st.dataframe(ind_metric.metric_detailed_data)
