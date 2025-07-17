import json

def response(status_code, body=None, headers=None, pagination=None):
    resp = {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body or {})
    }
    if headers:
        resp["headers"].update(headers)
    if pagination:
        resp["headers"]["X-Pagination"] = json.dumps(pagination)
    return resp

def error_response(status_code, message):
    return response(status_code, {"error": message})
