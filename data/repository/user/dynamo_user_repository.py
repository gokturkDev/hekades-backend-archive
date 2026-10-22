import os
from datetime import datetime
from typing import Union

import boto3
from botocore.client import BaseClient

from business.entity.user.user_entity import UserEntity, UserRole
from business.repository.user.user_repository import UserRepository


class DynamoUserRepository(UserRepository):
    def __init__(self):
        self._client: BaseClient = boto3.client(
            "dynamodb",
            region_name="eu-north-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )
        self._s3 = boto3.client("s3")

    def add(self, user: UserEntity, hashed_password: str):

        if self.get(user.email) is not None:
            raise ValueError("User already exists")

        self._client.put_item(
            TableName="hekades",
            Item={
                "PK": {
                    "S": f"user#{user.email}"
                },
                "SK": {
                    "S": f"user#{user.email}"
                },
                "created_at": {
                    "N": str(datetime.now().timestamp() * 1000),
                },
                "full_name": {
                    "S": user.full_name
                },
                "profile_picture": {
                    "S": "https://hekades-user-pictures.s3.eu-north-1.amazonaws.com/default.png"
                },
                "credits": {
                    "N": str(user.credits)
                },
                "password": {
                    "S": hashed_password
                },
                "is_active": {
                    "BOOL": False
                },
                "role": {
                    "S": user.role.value
                },
                "dob": {
                    "S": user.dob.isoformat() if user.dob is not None else None
                },
                "country": {
                    "S": user.country
                },
                "city": {
                    "S": user.city
                },
                "institution": {
                    "S": user.institution
                },
                "department": {
                    "S": user.department
                },
                "cell_phone": {
                    "S": user.cell_phone
                },
                "address": {
                    "S": user.address
                },
                "occupation": {
                    "S": user.occupation
                },
                "branch": {
                    "S": user.branch
                },
                "ssn": {
                    "S": user.ssn
                },
                "title": {
                    "S": user.title
                }
            }
        )

    def get(self, user_email: str) -> Union[UserEntity, None]:
        response = self._client.get_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"user#{user_email}"
                },
                "SK": {
                    "S": f"user#{user_email}"
                }
            }
        )
        if "Item" not in response:
            return None

        return UserEntity(
            email=user_email,
            full_name=response["Item"]["full_name"]["S"],
            profile_picture=response["Item"]["profile_picture"]["S"],
            credits=int(response["Item"]["credits"]["N"]),
            created_at=datetime.fromtimestamp(float(response["Item"]["created_at"]["N"]) / 1000),
            is_active=response["Item"]["is_active"]["BOOL"],
            role=UserRole(response["Item"]["role"]["S"]),
            dob=datetime.fromisoformat(response["Item"]["dob"]["S"]) if "dob" in response["Item"] else None,
            country=response["Item"]["country"]["S"] if "country" in response["Item"] else None,
            city=response["Item"]["city"]["S"] if "city" in response["Item"] else None,
            institution=response["Item"]["institution"]["S"],
            department=response["Item"]["department"]["S"],
            cell_phone=response["Item"]["cell_phone"]["S"],
            address=response["Item"]["address"]["S"] if "address" in response["Item"] else None,
            occupation=response["Item"]["occupation"]["S"] if "occupation" in response["Item"] else None,
            branch=response["Item"]["branch"]["S"] if "branch" in response["Item"] else None,
            ssn=response["Item"]["ssn"]["S"] if "ssn" in response["Item"] else None,
            title=response["Item"]["title"]["S"]
        )

    def get_user_password(self, user_email: str) -> Union[str, None]:
        response = self._client.get_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"user#{user_email}"
                },
                "SK": {
                    "S": f"user#{user_email}"
                }
            }
        )
        if "Item" not in response:
            return None

        return response["Item"]["password"]["S"]

    def update(self, user_email: str, full_name: Union[str, None]):
        if full_name is not None:
            self._client.update_item(
                TableName="hekades",
                Key={
                    "PK": {
                        "S": f"user#{user_email}"
                    },
                    "SK": {
                        "S": f"user#{user_email}"
                    }
                },
                UpdateExpression="SET full_name = :name",
                ExpressionAttributeValues={
                    ":name": {
                        "S": full_name
                    }
                }
            )

    def update_profile_picture(self, user_email: str, profile_picture: bytes):
        file_path = f"{user_email}.png"
        self._s3.put_object(
            Body=profile_picture,
            Bucket="hekades-user-pictures",
            GrantRead="",
            Key=file_path
        )

    def delete(self, email: str) -> bool:
        self._client.delete_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"user#{email}"
                },
                "SK": {
                    "S": f"user#{email}"
                }
            }
        )

        return True

    def set_user_active(self, user_email: str):
        self._client.update_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"user#{user_email}"
                },
                "SK": {
                    "S": f"user#{user_email}"
                }
            },
            UpdateExpression="SET is_active = :active",
            ExpressionAttributeValues={
                ":active": {
                    "BOOL": True
                }
            }
        )
