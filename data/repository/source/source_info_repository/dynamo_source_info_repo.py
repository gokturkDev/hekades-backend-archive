import os
from typing import List

import boto3
from botocore.client import BaseClient

from business.entity.source.source_info import SourceInfo
from data.repository.source.source_info_repository.source_info_repository import SourceInfoRepository


class DynamoSourceInfoRepository(SourceInfoRepository):

    def __init__(self):
        self._client: BaseClient = boto3.client(
            "dynamodb",
            region_name="eu-north-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )

    def add_source_info(self, info):
        self._client.put_item(
            TableName="hekades",
            Item={
                "PK": {
                    "S": "source"
                },
                "SK": {
                    "S": f"source#{info.id}"
                },
                "name": {
                    "S": info.name
                },
                "link": {
                    "S": info.link
                },
                "status": {
                    "S": info.status.value
                },
            }
        )

    def get_source_info(self, source_id: str) -> SourceInfo:
        response = self._client.query(
            TableName="hekades",
            KeyConditions={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": "source",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                },
                "SK": {
                    "AttributeValueList": [
                        {
                            "S": f"source#{source_id}"
                        }
                    ],
                    "ComparisonOperator": "EQ"
                }
            },
        )

        item = response["Items"][0]
        return SourceInfo(
            id=item["SK"]["S"].replace("source#", ""),
            name=item["name"]["S"],
            link=item["link"]["S"],
            status=item["status"]["S"],
        )

    def update_source_info(self, info: SourceInfo):
        self._client.update_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": "source"
                },
                "SK": {
                    "S": f"source#{info.id}"
                }
            },
            UpdateExpression="SET #status = :status",
            ExpressionAttributeNames={
                "#status": "status"
            },
            ExpressionAttributeValues={
                ":status": {
                    "S": info.status.value
                }
            }
        )

    def delete_source_info(self, source_id: str):
        self._client.delete_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": "source"
                },
                "SK": {
                    "S": f"source#{source_id}"
                }
            }
        )

    def get_all_sources_info(self) -> List[SourceInfo]:
        response = self._client.query(
            TableName="hekades",
            KeyConditions={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": "source",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )
        info_entities = []
        for item in response["Items"]:
            info = SourceInfo(
                id=item["SK"]["S"].replace("source#", ""),
                name=item["name"]["S"],
                link=item["link"]["S"],
                status=item["status"]["S"]
            )

            info_entities.append(info)
        return info_entities
