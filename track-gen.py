#!/usr/bin/env python3

from optparse import OptionParser
import sys
import urllib.request
import json
import pprint
import re

import pdb

parser = OptionParser()
parser.add_option("-f", "--filename", dest="filename", action="store_true", help="Export track as Markdown-friendly bullet list and save to file.")
(options, args) = parser.parse_args()

# Ensure track ID
if len(args) < 1:
    print("We require a track (Integer) id as argument")
    sys.exit()
    
if args[1]:
    filename = f'output/{args[1]}'
    print(filename)
else:
    filename = "output/data.md"

# Query JSON endpoint
url = "https://learn.co/api/v1/tracks/" + args[0]

# For accumulating paths
stack = []

def parse_obj_json(obj, output):
    if "children" in obj:
        if type(obj["children"]) is list and len(obj["children"]) > 0:
            output_key = obj.get("title")
            output[output_key] = {}
            [parse_obj_json(ch, output[output_key]) for ch in obj["children"]]
        elif type(obj["children"]) is list and len(obj["children"]) == 0:
            if not "children" in output:
                output["children"] = []

            # Deal with null HTTP
            url = obj.get("github_url", "")
            url = "http:" + url if len(url) > 0 else "None"

            output["children"].append({
                "title": obj.get("title"),
                "github_url": url
                })
            output["children"] = sorted(output["children"], key=lambda x: x["title"])
    return output

def bulletify(obj, indent=0, filename="output/output.md"):
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
            writer.writelines((indent * ' ') + '- ' + " - ".join(stack[:] + [obj.get("title"), url])+'\n')
            writer.close()

# Fetch data and parse the JSON
try:
    content = urllib.request.urlopen(url).read()
    struc = json.loads(content)
    if options.filename:
        bulletify(struc, filename=filename)
    else:
        bulletify(struc)
except urllib.error.HTTPError as err:
    print("Unable to connect to {0} [{1}]".format(url, str(err)))
    sys.exit(1)



