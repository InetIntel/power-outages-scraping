import boto3
from botocore.client import Config


class StorageClient:
    def __init__(self):
        self.bucket_exists = False
        # self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url="http://host.docker.internal:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )

    def _upload_file(self, local_path, s3_path):
        if not self.bucket_exists:
            try:
                self.client.create_bucket(Bucket=self.bucket_name)
            except self.client.exceptions.BucketAlreadyOwnedByYou:
                self.bucket_exists = True

        print(f"Uploading {local_path} to s3://{s3_path}")
        self.client.upload_file(local_path, self.bucket_name, s3_path)

    def upload_file_raw(self, local_path, s3_path):
        new_s3_path = f"raw/{s3_path}"
        self._upload_file(local_path, new_s3_path)
    
    def upload_file_processed(self, local_path, s3_path):
        new_s3_path = f"processed/{s3_path}"
        self._upload_file(local_path, new_s3_path)


    def read_object(self, s3_path, download_path=None):
        """
        Downloads an object from S3.

        Args:
            s3_path (str): The full key of the object in S3 (e.g., 'raw/2024/data.csv').
            download_path (str, optional): If provided, downloads the file locally to this path.
                                           If None, returns the content as bytes/string.
        Returns:
            str or None: The content of the file as a string if download_path is None, 
                         otherwise None.
        """
        print(f"Reading object from s3://{self.bucket_name}/{s3_path}")
        
        # Scenario 1: Large file: Download the file to a specific local path
        if download_path:
            self.client.download_file(self.bucket_name, s3_path, download_path)
            print(f"Successfully downloaded to: {download_path}")
            return None
        
        # Scenario 2: Small txt/json file: Read content directly into memory
        else:
            response = self.client.get_object(Bucket=self.bucket_name, Key=s3_path)
            file_content = response['Body'].read().decode('utf-8') # Assuming CSV/text data
            return file_content
        
    def list_keys_by_prefix(self, prefix: str) -> list[str]:
        """
        Lists all object keys within a given simulated directory (prefix).
        """
        keys = []
        paginator = self.client.get_paginator('list_objects_v2')
        
        # Iterate through all pages of results (S3 limits list results to 1000 per page)
        pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
        for page in pages:
            if 'Contents' in page:
                # 'Contents' is a list of dictionaries with metadata
                for obj in page['Contents']:
                    keys.append(obj['Key'])
                    
        return keys
