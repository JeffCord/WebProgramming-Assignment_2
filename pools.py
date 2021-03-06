from flask import Flask, request as flask_request
import requests
import xml.etree.ElementTree as ET
import json
import urllib.parse

app = Flask(__name__)
etags = []

# generates JSON output showing all the pool names as below:
@app.route('/pools')
def find_all_pools():
    pools_dict = {'pools': []}

    url_xml_data = 'https://raw.githubusercontent.com/devdattakulkarni/elements-of-web-programming' \
                   '/master/data/austin-pool-timings.xml'

    request_headers = flask_request.headers
    request_user_agent = request_headers['User-Agent']

    xml_to_str = requests.get(url_xml_data).text

    root = ET.fromstring(xml_to_str)

    for i in range(len(root)):
        current_dict = {}
        for j in root[i]:
            if j.tag == 'pool_name':
                current_dict['pool_name'] = j.text
                pools_dict['pools'].append(current_dict)
                break

    # with open ('all_pools.json', 'w') as f:
    #     new_json = json.dump(pools_dict, f, indent=2)

    return json.dumps(pools_dict)
    # return pools_dict


# returns json data for a requested pool
# {
#   pool_name: <pool_name>,
#   status: <status>,
#   phone: <phone>,
#   pool_type: <pool_type>,
# }
@app.route('/pools/<pool_name>', methods=['GET'])
def find_pool(pool_name):
    # check for ETAG
    etag_header = flask_request.headers.get('If-None-Match')

    if etag_header is not None:
        etag_header = urllib.parse.unquote(etag_header)

        if etag_header in etags:
            return '', 304

    url_xml_data = 'https://raw.githubusercontent.com/devdattakulkarni/elements-of-web-programming' \
                   '/master/data/austin-pool-timings.xml'

    request_headers = flask_request.headers
    request_user_agent = request_headers['User-Agent']

    xml_to_str = requests.get(url_xml_data).text

    root = ET.fromstring(xml_to_str)

    pool_dict = {}
    pool_found = False

    # iterate through xml data to find the pool we are looking for
    for i in range(len(root)):
        for j in root[i]:
            # if pool is found, create a dictionary of that pool's data,
            # and break out of the loop
            if j.tag == 'pool_name' and j.text == pool_name:
                pool_dict = create_dict(root[i])
                pool_found = True
                break

    # a non-existent pool name should return a 404 error
    if not pool_found:
        # return the proper 404 error message
        error_dict = {'error': pool_name + ' not found'}
        return error_dict, 404

    # with open ('pool_found.json', 'w') as f:
    #     new_json = json.dump(pool_dict, f, indent=2)

    # add etag if not in etags list
    etags.append(pool_name)

    # flask converts the dictionary into a human-readable string (json format)
    return pool_dict, 200, {'ETag': pool_name}


def create_dict(xml_element):
    result_dict = {}
    wanted_tags = ['pool_name', 'status', 'phone', 'pool_type']

    for i in range(len(wanted_tags)):
        for element in xml_element:
            if element.tag == wanted_tags[i]:
                result_dict[element.tag] = element.text
                break

    return result_dict


if __name__ == '__main__':
    app.run(debug=True)
