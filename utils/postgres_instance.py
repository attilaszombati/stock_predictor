import json
import os
from pprint import pprint

from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

BODY = {
    "settings":
        {
            "activationPolicy": "NEVER"
        }
}


def update_postgres_instance_status(request):
    request = request.get_data()
    try:
        request_json = json.loads(request.decode())
    except ValueError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return "JSON Error", 400
    status = request_json.get('status', 'ALWAYS')
    BODY['settings']['activationPolicy'] = status

    cred = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict=os.getenv(''))

    service = discovery.build('sqladmin', 'v1', credentials=cred)

    project = 'crawling-315317'

    instance = 'postgres3'

    req = service.instances().patch(project=project, instance=instance, body=BODY)
    resp = req.execute()
    pprint(resp)
    return {'done': 1}
