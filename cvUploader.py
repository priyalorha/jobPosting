import logging
import os
import base64
import boto3
from random import randint

from models import cv


class S3Functionality:
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.s3_resource = boto3.resource("s3",
                                          aws_access_key_id=aws_access_key_id,
                                          aws_secret_access_key=aws_secret_access_key)

    def write_data_to_s3(self, image: str, bucket: str, key: str) -> dict:
        try:
            print(f"bucketname {bucket} key {key}")
            return self.s3_resource.Object(bucket, f'{key}').put(Body=image)
        except Exception as e:
            logging.error(e)
            return {"error": e}

    def get_data_from_s3(self, bucket: str, key: str) -> dict:
        content_object = self.s3_resource.Object(bucket, key)
        file_content = content_object.get()['Body'].read().decode('utf-8')
        return file_content

    def delete_image_from_s3(self, file_name):
        res = self.s3_resource.Object("priya", file_name).delete()
        return res


s3_operations = S3Functionality(os.getenv('aws_access_key_id'),
                                os.getenv('aws_secret_access_key'))


def delete_cv(file_name):
    res = s3_operations.delete_image_from_s3(file_name)
    if res['ResponseMetadata']['HTTPStatusCode'] // 100 == 2:
        return True

    return False


def upload_cv(file_name: str) -> dict:
    try:
        os.path.isfile(file_name)
        logging.info("file exists")
        with open(file_name, "rb") as cv_file:
            encoded_string = base64.b64encode(cv_file.read())
            res = s3_operations.write_data_to_s3(encoded_string, 'priya', file_name)
            print(f"res {res}")
            if res['ResponseMetadata']['HTTPStatusCode'] // 100 == 2:
                return
        return {"message": "document stored"}
    except FileNotFoundError:
        logging.error(f"file not found {file_name}")
        return {"error": f"file not found,checking at {os.getcwd()}"}


def get_cv(file_name: str):
    if cv.objects(name=file_name):
        data = s3_operations.get_data_from_s3("priya", file_name)
        return {"data": data, "format": file_name.split('.')[-1]}
    else:
        return {"error": f"could not find image {file_name}"}


def get_list_of_all_cvs() -> list:
    image = [i['name'] for i in cv.objects().as_pymongo()]
    return image
