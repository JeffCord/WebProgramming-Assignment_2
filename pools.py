from flask import Flask, request as flask_request
import requests
import xml.etree.ElementTree as ET
import json

app = Flask(__name__)
etags = []  # TODO change to list

# TODO This should generate JSON output showing all the pool names as below:
#  {
#    pools: [{pool_name: <pool_name>}, {pool_name: <pool_name>}, .....
#  }
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

    # return json.dumps(pools_dict, indent=2)
    return pools_dict


# If <pool_name> does not exists:
# HTTP response status: 404 NOT Found
# If <pool_name> exists:HTTP response status: 200 OK
# HTTP response body:

# {
#   pool_name: <pool_name>,
#   status: <status>,
#   phone: <phone>,
#   pool_type: <pool_type>,
# }
@app.route('/pools/<pool_name>', methods=['GET'])
def find_pool(pool_name):
    # check for ETAG
    if pool_name in etags:
        # for i in etags[pool_name]:
        #     print(etags[pool_name][i])

        return pool_name, 304, {'ETag': pool_name}

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
                pool_dict = create_dict(pool_name, root[i])
                pool_found = True
                break

    # a non-existent pool name should return a 404 error
    # TODO ask about where this 404 message should be displayed:
    #   on command line (CHECK ASSIGNMENT PAGE FOR UPDATES)
    if not pool_found:
        return 'Pool not found.', 404

    # with open ('pool_found.json', 'w') as f:
    #     new_json = json.dump(pool_dict, f, indent=2)

    # add etag if not in etags dictionary
    etags.append(pool_name)

    # flask converts the dictionary into a human-readable string (json format)
    return pool_dict, 200, {'ETag': pool_name}


def create_dict(pool_name, xml_element):
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
