# Sammlr
Python scripts to collect data from the Facebook API and calculate networks of page likes, mutually liked pages, user overlap, and content overlap

UPDATE February 2018: As the Facebook API no longer seems to allow the unique identification of users, Sammlr is not able to compute a network of user-overlap anymore. Reactions are also not retrieved any more. The only networks you will get and that still work is content overlap, page likes, and common friends. The updated script file is still a bit rough, but should get the job done.

## What the scripts does: ##
- Sammlr uses the feed of a public Facebook page, to collect data from each post (e.g. status update, photo, video, etc.), all(!) comments made on that posts and all(!) reactions (e.g. like, love, hate, etc.). You can either specify a number of posts to collect or a date range. This data is stored as a comma-separated file on your drive and contains in each row info about the page's ID, page's name, unique user id (user name is not stored for privacy reasons), the type (of post, comment, reaction), a timestamp, and where applicable a permanent link to the post and the posts' or comments' message.
- So Sammlr is just another Facebook data collection tool, yeah, you got it! But wait, there's more to it: If you choose to collect data on a network of pages, Sammlr will provide the csv files with raw data, but in addition calculate four types of networks between these pages
  - 1) A network of unique user overlap, in which the weighted edges (links) between each pair of nodes (pages) are the number of users that were active (i.e. posting, commenting, or reacting) on both pages.
  - 2) A network of unique content overlap, in which the weighted edges (links) between each pair of nodes (pages) are the number of pieces of content (photos, videos, newspaper articles, basically everything with a hyperlink) that were either posted or mentioned in a comment in both of the pages' feed.
  - 3) Optional (as it takes some time): A network of page likes between the selected pages. This network is unweighted and directed.
  - 4) Optional (as it takes some time): A network of the overlap of any pages liked by the selected pages or pages, by which the selected pages were liked. This means a network in which the number of common friends (pages) are the weighted edges between each par of nodes.
- These networks are stored as simple edgelist to be processed with any network analysis package of choice, as well as a *.graphml-file, that can easily be opened with popular free network visualization software like Gephi and is easy to read with common network analysis packages like igraph (R,Python) or networkx (Python).

What you need before you can start:
- You will need to register as a Facebook developer to gain access to the Facebook Graph API (https://developers.facebook.com/tools/explorer) - from there, you can get the access token needed by the Sammlr application.
- You will also need the Facebook ID of the Facebook page you want to collect data fro. You can use pages like this (https://findmyfbid.com/) to find the numeric ID of a page.
- Sammlr is written in Python 3, so make sure you have a Python environment installed


## Dependencies ##
*(What libraries Sammlr uses:)*

Our scripts are still work in progress and depend on functions from a number of other libraries (most of them pretty common, but if your Python installation is missing any of these, install them before running our script

- urllib.request
- json
- csv
- re
- time
- sys
- networkx
- from networkx.algorithms the bipartite functions
- pandas
- os

install all via:
 $`pip install request json csv re networkx pandas`

or
 $`pip3 install request json csv re networkx pandas`

depending on your python installation

- you'll also need a Facebook API access token or app key from https://developers.facebook.com/tools/explorer/ in order to use Sammlr

## Usage ##
To use Sammlr,
- get an access token for the Graph-API from https://developers.facebook.com/tools/explorer/ (you can use the temporary access_token from the Graph API Interface for most reasonable sized measurements but for long running tasks might need a permanent token.)
- open your terminal
- clone this directory: $`git clone https://github.com/walfaelschung/Sammlr`
- open the downloaded directory $`cd Sammlr`
- install all Requirements (see above)
- run Sammlr $`python3 sammlr_script_30_11_17.py`
- follow the instructions in the command prompt

## Copyrights ##

What licenses apply:
- CC-BY-NC-4.0
Creative Commons License for non-commercial use
https://creativecommons.org/licenses/by-nc/4.0/legalcode

## Contributors: ##
- All code written and poorly tested by Matthias Hoffmann with help by machinaeXphilip. For the construction of a network of content overlap between the pages, we rely on a regular expression to detect hyperlinks in strings, that was written by Diego Perini (https://gist.github.com/dperini/729294).
