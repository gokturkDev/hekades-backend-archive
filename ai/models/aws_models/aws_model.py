import boto3


class AWSModel:

    def __init__(self, model_id):
        self.client = boto3.client('bedrock-runtime', region_name="us-west-2")
        self.model_id = model_id
