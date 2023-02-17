#!/bin/bash

# print help
if [ $1 = "-h" ]; then
    echo "Usage: archive_scrape.sh [YYYY-MM] [Subreddit]"
    echo "If no arguments are given, interactive prompt will ask for year, month, and subreddit."
    exit 0
fi

# if no arguments/1 are given, ask for current month and year in the same prompt
if [ $# -ne 2 ]; then
    read -p "Enter year and month (YYYY-MM): " year_month
    read -p "Enter subreddit (without prefix /r/): " subreddit
else
    year_month=$1
    subreddit=$2
fi

# if 

# construct URL for the month
url="https://files.pushshift.io/reddit/submissions/RS_${year_month}.zst"

curl $url --output - | zstd --long=31 -dc | rg -i "\"subreddit\":\"$subreddit\"" > "${subreddit}_${year_month}.json"