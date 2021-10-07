import requests
from optparse import OptionParser
import sys
import urllib.request
import os
import json

parser = OptionParser()
(options, args) = parser.parse_args()

# Ensure track ID
if len(args) < 1:
    print("We require a track (Integer) id as argument")
    sys.exit()

# Query JSON endpoint
api_url = "https://learn.co/api/v1/tracks/" + args[0]

# For accumulating paths
stack = []

download_folder = "career_prep"
os.mkdir(download_folder)

REPO_NUMBER = 1


repo_url = 'https://github.com/AlexInes/phase-3-sinatra-react-project'

def get_filename(repo_link, REPO_NUMBER):
    #filename = repo_link.replace('https://github.com/learn-co-curriculum/', '') + '.zip'
    filename = repo_link.replace('https://github.com/learn-co-curriculum/', f"{REPO_NUMBER}_") + '.zip'
    filename = f"{download_folder}/{filename}"
    return filename

def get_download_link(repo_url):
    return f'{repo_url}/archive/refs/heads/main.zip'

def download_repos(repo_urls, REPO_NUMBER=1):
    for repo_url in repo_urls:
        download_url = get_download_link(repo_url)
        r = requests.get(download_url, allow_redirects=True)
        open(get_filename(repo_url,REPO_NUMBER), 'wb').write(r.content)
        REPO_NUMBER += 1


urls = []

def only_urls(obj, indent=0):    
    if "children" in obj:
        if type(obj["children"]) is list and len(obj["children"]) > 0:
            [only_urls(ch, indent + 2) for ch in obj["children"]]
        elif type(obj["children"]) is list and len(obj["children"]) == 0:
            url = obj.get("github_url", "")
            urls.append(url)
            #print(url)
            #urls+=url
            #print(urls)
    return urls

try:
    content = urllib.request.urlopen(api_url).read()
    struc = json.loads(content)
    urls = only_urls(struc)
except urllib.error.HTTPError as err:
    print("Unable to connect to {0} [{1}]".format(api_url, str(err)))
    sys.exit(1)

download_repos(urls, REPO_NUMBER)


