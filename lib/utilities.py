from os.path import exists #check if file exists
import math, sys, os, json, subprocess, re

def load_json(file):
    fname = '{}'.format(file)
    if not file_exists(fname):
        sys.exit()
    try:
        with open(fname,'r') as myfile:
            return json.load(myfile)
    except:
        print(f'\033[31m Error in unilities.py: I am not able to load json table from {fname}', '\033[0m')
        sys.exit()

def file_exists(myfile):
    if not exists(myfile):
        print('file_exists(): File {} does not exist'.format(myfile))
        return False
    print('file_exists(): File found {}'.format(myfile))
    return True

def json_oneline_lists(data, indent=4):
    # Serialize JSON with normal formatting first
    formatted_json = json.dumps(data, indent=indent)

    # Use regex to find and format lists on a single line
    def compact_lists(match):
        # Collapse the multiline list into a single line
        return match.group(1) + "[" + match.group(2).replace("\n", "").replace(" ", "") + "]"

    # Regex pattern to match lists split across multiple lines
    pattern = re.compile(r"(\s*\".*?\": )\[\s*(.*?)\s*\]", re.DOTALL)
    compacted_json = re.sub(pattern, lambda m: compact_lists(m), formatted_json)

    return compacted_json

# # Process JSON to make lists one line
# formatted_json = json_oneline_lists(data, indent=4)
#
# # Save to file
# with open("output.json", "w") as f:
#     f.write(formatted_json)
#
# # Print the output
# print(formatted_json)

