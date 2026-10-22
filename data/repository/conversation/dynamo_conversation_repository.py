import datetime
import json
import os
from typing import List, Union

import boto3
from botocore.client import BaseClient

from business.entity.conversation.conversation_entity import ConversationEntity, ConversationType
from business.entity.conversation.message_entity import MessageEntity, UserMessageEntity, SystemMessageEntity
from business.repository.conversation.conversation_repository import ConversationRepository


class DynamoDBConversationRepository(ConversationRepository):
    def __init__(self):
        self._client: BaseClient = boto3.client(
            "dynamodb",
            region_name="eu-north-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )

    def add(self, conversation: ConversationEntity):
        item_dict = {
            "PK": {
                "S": f"conversation#{conversation.convo_id}"
            },
            "SK": {
                "S": f"conversation#{conversation.convo_id}"
            },
            "created_at": {
                "N": str(conversation.created_at.timestamp())
            },
            "title": {
                "S": conversation.title
            },
            "user_email": {
                "S": conversation.user_email
            },
            "gs1pk": {
                "S": conversation.user_email
            },
            "gs1sk": {
                "S": str(conversation.created_at.timestamp())
            },
        }

        if conversation.literature_docs:
            item_dict["serialized_literature_docs"] = {
                "S": json.dumps(conversation.literature_docs)
            }
        if conversation.pubmed_summary:
            item_dict["pubmed_summary"] = {
                "S": conversation.pubmed_summary
            }
        if conversation.confidence_index:
            item_dict["confidence_index"] = {
                "N": str(conversation.confidence_index)
            }

        if conversation.patient_id:
            item_dict["patient_id"] = {
                "S": conversation.patient_id
            }

        self._client.put_item(
            TableName="hekades",
            Item=item_dict
        )

    def get_conversations_of_user(self, user_id: str) -> List[ConversationEntity]:
        conversations: List[ConversationEntity] = []

        response = self._client.query(
            TableName="hekades",
            IndexName="gs1pk-gs1sk-index",
            KeyConditions={
                "gs1pk": {
                    "AttributeValueList": [
                        {
                            "S": user_id,
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )

        conversations: List[ConversationEntity] = []
        for item in response["Items"]:
            conversations.append(self._get_conversation_entity_from_dict(item))

        while 'LastEvaluatedKey' in response:
            response = self._client.query(
                TableName="hekades",
                IndexName="gs1pk-gs1sk-index",
                KeyConditions={
                    "gs1pk": {
                        "AttributeValueList": [
                            {
                                "S": user_id,
                            },
                        ],
                        "ComparisonOperator": "EQ",
                    }
                },
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
                    
            for item in response["Items"]:
                conversations.append(self._get_conversation_entity_from_dict(item))

        return conversations


    def get_conversation_by_id(self, convo_id: str) -> ConversationEntity:
        response = self._client.query(
            TableName="hekades",
            KeyConditions={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": f"conversation#{convo_id}",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )
        item = response["Items"][0]
        return self._get_conversation_entity_from_dict(item)

    def update_conversation(self, conversation: ConversationEntity):
        update_items = []
        expression_attribute_values = {}

        def _set_item_to_be_updated(item_name: str, value: dict):
            update_items.append(f"{item_name} = :{item_name}")
            expression_attribute_values[f":{item_name}"] = value

        if conversation.literature_docs:
            _set_item_to_be_updated("serialized_literature_docs", {"S": json.dumps(conversation.literature_docs)})
        if conversation.pubmed_summary:
            _set_item_to_be_updated("pubmed_summary", {"S": conversation.pubmed_summary})
        if conversation.confidence_index:
            _set_item_to_be_updated("confidence_index", {"N": str(conversation.confidence_index)})
        if conversation.patient_id:
            _set_item_to_be_updated("patient_id", {"S": conversation.patient_id})
        if conversation.type:
            _set_item_to_be_updated("convo_type", {"S": conversation.type.value})

        update_expression = "SET " + ",".join(update_items)

        if len(expression_attribute_values.values()) == 0:
            return

        self._client.update_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"conversation#{conversation.convo_id}"
                },
                "SK": {
                    "S": f"conversation#{conversation.convo_id}"
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values

        )

    def add_message(self, message: MessageEntity):
        if isinstance(message, UserMessageEntity):
            role = "user"
        else:
            role = "ai"

        item_dict = {
            "PK": {
                "S": f"conversation#{message.convo_id}"
            },
            "SK": {
                "S": f"message#{message.order}"
            },
            "created_at": {
                "N": str(message.created_at.timestamp())
            },
            "role": {
                "S": role
            }
        }

        if isinstance(message, SystemMessageEntity):
            if message.sources is not None:
                item_dict["serialized_sources"] = {"S": json.dumps(message.sources)}

            if message.phases is not None:
                item_dict["serialized_phases"] = {"S": json.dumps(message.phases)}

        if message.content is not None:
            item_dict["content"] = {"S": message.content}

        self._client.put_item(
            TableName="hekades",
            Item=item_dict
        )

    def update_message(self, convo_id: str, system_message: SystemMessageEntity):
        update_items = []
        expression_attribute_values = {}

        def _set_item_to_be_updated(item_name: str, value: dict):
            update_items.append(f"{item_name} = :{item_name}")
            expression_attribute_values[f":{item_name}"] = value

        if system_message.content is not None:
            _set_item_to_be_updated("content", {"S": system_message.content})
        if system_message.sources is not None:
            _set_item_to_be_updated("serialized_sources", {"S": json.dumps(system_message.sources)})
        if system_message.phases is not None:
            _set_item_to_be_updated("serialized_phases", {"S": json.dumps(system_message.phases)})

        update_expression = "SET " + ",".join(update_items)

        self._client.update_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"conversation#{convo_id}"
                },
                "SK": {
                    "S": f"message#{system_message.order}"
                }
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values

        )

    def get_conversation_messages(self, convo_id: str) -> List[MessageEntity]:
        response = self._client.query(
            TableName="hekades",
            KeyConditions={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": f"conversation#{convo_id}",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )

        items = response["Items"]
        del items[0]
        messages: List[MessageEntity] = []

        for item in items:
            messages.append(self._get_message_entity_from_dict(item))

        return messages

    def get_latest_message(self, convo_id: str) -> Union[MessageEntity, None]:
        response = self._client.query(
            TableName="hekades",
            KeyConditions={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": f"conversation#{convo_id}",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )
        item = response["Items"][(response["Count"] - 1)]
        if "content" in item:
            return self._get_message_entity_from_dict(item)
        else:
            return None

    def _get_message_entity_from_dict(self, item):
        role = item["role"]
        if role["S"] == "ai":
            return SystemMessageEntity(
                convo_id=item["PK"]["S"].replace("conversation#", ""),
                order=int(item["SK"]["S"].replace("message#", "")),
                created_at=datetime.datetime.fromtimestamp(float(item["created_at"]["N"])),
                content=item["content"]["S"] if "content" in item else None,
                sources=json.loads(item["serialized_sources"]["S"]) if "serialized_sources" in item else None,
                pubmed_summary=item["pubmed_summary"]["S"] if "pubmed_summary" in item else None,
                confidence_index=int(item["confidence_index"]["N"]) if "confidence_index" in item else None,
                phases=json.loads(item["serialized_phases"]["S"]) if "serialized_phases" in item else None,
                literature_docs=json.loads(
                    item["serialized_literature_docs"]["S"]) if "serialized_literature_docs" in item else None,

            )
        return UserMessageEntity(
            convo_id=item["PK"]["S"].replace("conversation#", ""),
            order=int(item["SK"]["S"].replace("message#", "")),
            content=item["content"]["S"],
            created_at=datetime.datetime.fromtimestamp(float(item["created_at"]["N"])),
        )

    def _get_conversation_entity_from_dict(self, item):
        return ConversationEntity(
            convo_id=item["PK"]["S"].replace("conversation#", ""),
            title=item["title"]["S"],
            user_email=item["user_email"]["S"],
            created_at=datetime.datetime.fromtimestamp(float(item["created_at"]["N"])),
            patient_id=item["patient_id"]["S"] if "patient_id" in item else None,
            literature_docs=json.loads(
                item["serialized_literature_docs"]["S"]) if "serialized_literature_docs" in item else None,
            pubmed_summary=item["pubmed_summary"]["S"] if "pubmed_summary" in item else None,
            confidence_index=int(item["confidence_index"]["N"]) if "confidence_index" in item else None,
            type=ConversationType(item["convo_type"]["S"]) if "convo_type" in item else None
        )
