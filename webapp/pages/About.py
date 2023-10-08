"""
'About' page for the Streamlit webapp
"""

import streamlit as st

st.header("About")

st.markdown(
    """
    ##### _A note on the data_
    This project uses a match of Metrica Sport's openly-available event and tracking data. The data is anonymised, which 
    is why the team IDs are 'FIFATMA' and 'FIFATMB'. 
    
    ### The project
    The aim of this project was to make a prototype webapp to create football metrics using event and tracking data. 
    This is as much a product-type challenge as a data-type one, because ideas about the game differ from person to 
    person, club to club, and a user would need to be sure that they can create the statistics that reflect how 
    they/their team see the game.
    
    At the same time, it's clear that coaches and analysts have a job bordering on untenable. The amount of time spent 
    watching video to code and analyse matches is an area which seems ripe for improving. 
    
    The options in the metric-creation area are designed to match up with how professionals see the game. As a v1, 
    they're not exhaustive, but give an indication of the concept.
    
    Both of the previous two paragraphs are also why the sequence viewer is important: coaches/analysts will want to 
    make sure that the definition aligns with what's in their head, and they may want to check specific moments even 
    while not having to watch the full match. This is also why the metrics export with timestamps for each sequence 
    belonging to each metric, as a nod to the fact that the ideal would be to link with the actual video.
    
    ### How future versions would look
    There are two main concepts that an expanded prototype would include:
    - Different types/defaults of metrics (e.g. advanced possession, transition, pressing)
    - User management
    
    The latter speaks for itself, but it's worth a brief word on the former. 
    
    With the amount of things that can happen in football, it seemed sensible to slightly narrow the type of metric that 
    could be created in each section. A simple example of this is in the location selection: some phases of play/a game 
    model are inherently based around certain areas of the pitch. It would be a waste of screen space to always have a 
    selection tool which can control the whole pitch. 
    
    You could build this out more as well. When attacking in the final third it might be useful to have options for the 
    amount of attackers (or defenders) in the box, but that's not going to be important for deeper build-up.   
    """
)
