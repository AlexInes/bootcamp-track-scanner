import requests
from optparse import OptionParser
import sys
import urllib.request
import os
import json
from slugify import slugify

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

download_folder = slugify("")
os.mkdir(download_folder)

track_path = f"{download_folder}/curriculum_num.md"
REPO_NUMBER = 1


def get_filename(repo_link, REPO_NUMBER):
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
    return urls

LESSON_NUMBER = 1

def bulletify(obj, indent=0, filename=track_path):
    if "children" in obj:
        if type(obj["children"]) is list and len(obj["children"]) > 0:
            writer = open(filename,'a')
            writer.writelines((indent * ' ') + '+ ' + obj.get("title")+'\n')
            writer.close()
            [bulletify(ch, indent + 2, filename) for ch in obj["children"]]
        elif type(obj["children"]) is list and len(obj["children"]) == 0:
            url = obj.get("github_url", "")
            #url = quote_wrap(url) if len(url) > 0 else "None"
            writer = open(filename,'a')
            global LESSON_NUMBER
            writer.writelines((indent * ' ') + '- ' + f"{LESSON_NUMBER} " + " - ".join(stack[:] + [obj.get("title"), url])+'\n')
            writer.close()
            LESSON_NUMBER+= 1

try:
    content = urllib.request.urlopen(api_url).read()
    struc = json.loads(content)
    bulletify(struc)
    urls = only_urls(struc)
except urllib.error.HTTPError as err:
    print("Unable to connect to {0} [{1}]".format(api_url, str(err)))
    sys.exit(1)

download_repos(urls, REPO_NUMBER)


