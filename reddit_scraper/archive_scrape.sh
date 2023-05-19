#!/usr/bin/env bash

# print help
if [ $1 = "-h" ]; then
    echo "Usage: archive_scrape.sh [DATA_SOURCE_DIR] [YYYY-MM] [Subreddit]"
    echo "If no arguments are given, interactive prompt will ask for data source, year, month, and subreddit."
    exit 0
fi

# if no arguments/1 are given, ask for current month and year in the same prompt
if [ $# -le 2 ]; then
    read -p "Enter data source directory: " DATA_SOURCE_DIR
    read -p "Enter year and month (YYYY-MM): " year_month
    read -p "Enter subreddit (without prefix /r/): " subreddit
else
    DATA_SOURCE_DIR=$1
    year_month=$2
    subreddit=$3
fi

DATADIR=$(realpath -e  -- "$(dirname -- "${BASH_SOURCE[0]}";)";)/../data

# Function to create directory if it doesn't exist
create_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
    fi
}

# construct URL for the month (deprecated in favor of academic torrents)
# url="https://files.pushshift.io/reddit/submissions/RS_${year_month}.zst"

# Create output directory if it doesn't exist
create_directory "$DATADIR"

zstd --long=31 -dc "${DATA_SOURCE_DIR}/RS_${year_month}.zst" | rg -i "\"subreddit\":\"($subreddit)\"" > "$DATADIR/temp.json"
# if $subreddit contains |, then for each regex case, pipe to a different file (makedirs -p if necessary)
# else, rename the file to ${subreddit}/${year_month}.json (makedirs -p if necessary)
if [[ $subreddit == *"|"* ]]; then
    # Multiple subreddit as regex
    regex_subreddits=$(echo "$subreddit" | tr "|" "\n")

    # Loop through each regex subreddit and filter the results
    for regex in $regex_subreddits; do
        # Create output directory if it doesn't exist
        create_directory "$DATADIR/${regex}"

        # Filter the results for each subreddit and redirect to respective file
        rg -i "\"subreddit\":\"$regex\"" "$DATADIR/temp.json" > "$DATADIR/${regex}/${year_month}.json"
        echo "Saved to data/${regex}/${year_month}.json"
    done
else
    # Single subreddit
    # Create output directory if it doesn't exist
    create_directory "$DATADIR/$subreddit"

    # Move the temporary file to the desired output file
    mv "$DATADIR/temp.json" "$DATADIR/${subreddit}/${year_month}.json"
    echo "Saved to data/${subreddit}/${year_month}.json"
fi

# Remove the temporary file
rm "$DATADIR/temp.json"