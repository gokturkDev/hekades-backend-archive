import os
from typing import Union

import boto3
from botocore.client import BaseClient

from business.entity.patient.patient_entity import PatientEntity
from business.repository.patient.patient_repository import PatientRepository


class DynamoPatientRepository(PatientRepository):
    def __init__(self):
        self._client: BaseClient = boto3.client(
            "dynamodb",
            region_name="eu-north-1",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )

    def get_all_patients(self, user_id: str) -> list[PatientEntity]:
        response = self._client.query(
            TableName="hekades",
            IndexName="gs2pk-gs2sk-index",
            KeyConditions={
                "gs2pk": {
                    "AttributeValueList": [
                        {
                            "S": user_id,
                        },
                    ],
                    "ComparisonOperator": "EQ",
                }
            },
        )
        patients = []
        for item in response["Items"]:
            patient = PatientEntity(
                patient_id=item["PK"]["S"].replace("patient#", ""),
                user_id=item["user_id"]["S"],
                patient_name=item["patient_name"]["S"],
                last_visit_date=item["last_visit_date"]["N"],
                patient_file_text=item["patient_file_text"]["S"],
                patient_summary=item["patient_summary"]["S"],
            )
            patients.append(patient)
        return patients
    
    def get_patient(self, patient_id: str) -> Union[PatientEntity, None]:
        response = self._client.get_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"patient#{patient_id}"
                },
                "SK": {
                    "S": f"patient#{patient_id}"
                },
            },
        )
        if "Item" not in response:
            return None

        item = response["Item"]
        patient = PatientEntity(
            patient_id=item["PK"]["S"].replace("patient#", ""),
            user_id=item["user_id"]["S"],
            patient_name=item["patient_name"]["S"],
            last_visit_date=item["last_visit_date"]["N"],
            patient_file_text=item["patient_file_text"]["S"],
            patient_summary=item["patient_summary"]["S"],
        )
        return patient

    def add_patient(self, patient: PatientEntity):
        self._client.put_item(
            TableName="hekades",
            Item={
                "PK": {
                    "S": f"patient#{patient.patient_id}"
                },
                "SK": {
                    "S": f"patient#{patient.patient_id}"
                },
                "user_id": {
                    "S": patient.user_id
                },
                "patient_name": {
                    "S": patient.patient_name
                },
                "patient_summary": {
                    "S": patient.patient_summary
                },
                "last_visit_date": {
                    "N": str(patient.last_visit_date.timestamp())
                },
                "patient_file_text": {
                    "S": patient.patient_file_text
                },
                "gs2pk": {
                    "S": patient.user_id
                },
                "gs2sk": {
                    "S": patient.patient_name
                },
            }
        )

    def update_patient(self, patient: PatientEntity):
        self._client.update_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"patient#{patient.patient_id}"
                },
                "SK": {
                    "S": f"patient#{patient.patient_id}"
                },
            },
            UpdateExpression="SET patient_name = :n, last_visit_date = :lvd, patient_file_text = :pft, patient_summary = :ps",
            ExpressionAttributeValues={
                ":n": {
                    "S": patient.patient_name
                },
                ":lvd": {
                    "N": str(patient.last_visit_date.timestamp())
                },
                ":pft": {
                    "S": patient.patient_file_text
                },
                ":ps": {
                    "S": patient.patient_summary
                }
            }
        )

    def delete_patient(self, patient_id: str):
        self._client.delete_item(
            TableName="hekades",
            Key={
                "PK": {
                    "S": f"patient#{patient_id}"
                },
                "SK": {
                    "S": f"patient#{patient_id}"
                },
            }
        )
