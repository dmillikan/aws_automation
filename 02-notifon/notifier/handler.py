import json


def hello(event, context):
    """Test"""
    print(event)

    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    
