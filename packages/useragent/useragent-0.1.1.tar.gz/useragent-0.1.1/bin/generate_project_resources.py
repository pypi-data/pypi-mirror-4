import json
import urllib

import yaml

def get_yaml_data(filename):
    url = "https://raw.github.com/tobie/ua-parser/master/" + filename
    return urllib.urlopen(url).read()

def convert_yaml_to_json(yaml_file, json_file):
    with open(json_file, 'w') as fp:
        json.dump(yaml.load(get_yaml_data(yaml_file)), fp)

resource_map = {
    'regexes.yaml': 'user_agent_data.json',
    'test_resources/test_device.yaml': 'test_device.json',
    'test_resources/test_user_agent_parser_os.yaml': 'test_os.json',
    'test_resources/test_user_agent_parser.yaml': 'test_browser.json',
    'test_resources/pgts_browser_list.yaml': 'test_pgts_browser.json',
    'test_resources/firefox_user_agent_strings.yaml': 'test_firefox.json',
    'test_resources/additional_os_tests.yaml': 'test_additional_os.json',
}

map(lambda args: convert_yaml_to_json(*args), resource_map.items())
