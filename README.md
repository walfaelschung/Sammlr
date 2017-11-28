# Sammlr
Python scripts to collect data from the Facebook API and calculate networks of page likes, mutually liked pages, user overlap, and content overlap

What the scripts does:
- 

What you need before you can start:
- You will need to register as a Facebook developer to gain access to the Facebook Graph API (https://developers.facebook.com/tools/explorer) - from there, you can get the access token needed by the Sammlr application.
- You will also need the Facebook ID of the Facebook page you want to collect data fro. You can use pages like this (https://findmyfbid.com/) to find the numeric ID of a page.
- Sammlr is written in Python 3, so make sure you have a Python environment installed

What libraries Sammlr uses:
Our scripts are still work in progress and depend on functions from a number of other libraries (most of them pretty common, but if your Python installation is missing any of these, install them before running our script)
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

What licenses apply:
- GPLv3

Contributors:
- All code written and poorly tested by Matthias Hoffmann and Philip Steimel. For the construction of a network of content overlap between the pages, we rely on a regular expression to detect hyperlinks in strings, that was written by Diego Perini (https://gist.github.com/dperini/729294).
