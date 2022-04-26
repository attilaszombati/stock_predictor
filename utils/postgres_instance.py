import json
from pprint import pprint

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

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

    credentials = GoogleCredentials.get_application_default()

    service = discovery.build('sqladmin', 'v1', credentials=credentials)

    project = 'crawling-315317'

    instance = 'postgres3'

    req = service.instances().patch(project=project, instance=instance, body=BODY)
    resp = req.execute()
    pprint(resp)
    return {'operation_type': resp["operationType"]}
