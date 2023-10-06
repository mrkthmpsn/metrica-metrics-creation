# Metrics creation using Metrica open tracking & event data
Using data from [Metrica's open sample](https://github.com/metrica-sports/sample-data/tree/master).

## Introduction
The aim of this project is to produce an interface that enables users to create useful metrics from tracking and event data. It uses data from [Metrica's open sample](https://github.com/metrica-sports/sample-data/tree/master), specifically Game 3 (which is in a different format to Games 1 and 2, for more on that see 'Loading the data' section).

## More on various stuff
### Loading the data
I ended up using a hybrid of kloppy's functions to load in Metrica data and my own code to parse the documents. The reasons for using kloppy were:
- The parsing functions were there and if the parsing functions are there you'd be a fool not to take them.
- Metrica's third game of sample data used FIFA's EPTS format for its metadata xml and tracking data file set-up, a data format which I'm not familiar with... 

EPTS - or 'Electronic Performance & Tracking System' - is a scheme which has had a major push over the last five years or so, offering quality tests for tracking data and wearables systems. The set of documents for that, and the 2017 document on a standard data format, can be found on [this Football Innovation and Technology documents web page](https://www.fifa.com/technical/football-technology/documents?filterId=0x442d7bc5aec4b6469491caa061802eed).
The fact that Metrica's third game of sample tracking data used this FIFA format _was_ a large part of the reason for choosing it as the focus of this project. FIFA's move towards being an authority in this area is really interesting, and this was a good excuse to learn more. But I was happy to take the help in parsing the complicated documents.

However, I ended up with more of my own code than I'd originally envisioned, particularly for the event data, for a couple of reasons:
- While there's a lot that can be standardised between similar data sources from different providers, I am personally uncomfortable about doing that to the event data itself, which kloppy does by default. 
- This was my first project using kloppy and my first in a few years using Metrica's event data - I found it difficult to know what features were Metrica's and what features were kloppy. This was particularly important when features appeared to be missing, which I think came from the Metrica data not having all of the features that kloppy has in its power to add.
- Metrica's event data JSON was quite simple so writing my own basic parser wasn't too difficult.

## Running the project yourself
_To write_
_Note that other than the raw data, no further data will be added to the repo itself as this would add a lot of files. It would also being superfluous, as the data can be generated from the functions._

## Links section
- https://kloppy.pysport.org/getting-started/metrica/
