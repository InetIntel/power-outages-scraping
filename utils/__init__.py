from .StorageClient import StorageClient
# import boto3
# from botocore.client import Config


# class Uploader:
#     def __init__(self, bucket_name):
#         self.bucket_exists = False
#         self.bucket_name = bucket_name
#         self.client = boto3.client(
#             "s3",
#             endpoint_url="http://host.docker.internal:9000",
#             aws_access_key_id="minioadmin",
#             aws_secret_access_key="minioadmin",
#             config=Config(signature_version="s3v4"),
#             region_name="us-east-1",
#         )

#     def upload_file(self, local_path, s3_path):
#         if not self.bucket_exists:
#             try:
#                 self.client.create_bucket(Bucket=self.bucket_name)
#             except self.client.exceptions.BucketAlreadyOwnedByYou:
#                 self.bucket_exists = True

#         print(f"Uploading {local_path} to s3://{s3_path}")
#         self.client.upload_file(local_path, self.bucket_name, s3_path)