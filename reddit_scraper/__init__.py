import subprocess

# curl https://files.pushshift.io/reddit/submissions/RS_2008-11.zst --output - | zstd --long=31 -dc | rg -e '"subreddit":"SuicideWatch"'

def  s