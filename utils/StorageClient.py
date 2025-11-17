import boto3
from botocore.client import Config
import traceback
import sys
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
class StorageClient:
    def __init__(self):
        self.bucket_exists = False
        # self.bucket_name 
        self.client = boto3.client(
            "s3",
            # TODO: diff endpoint url if local vs in docker
            endpoint_url="http://host.docker.internal:9000",
            # endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        try:
                self.client.create_bucket(Bucket="raw")
                self.client.create_bucket(Bucket="processed")
        except self.client.exceptions.BucketAlreadyOwnedByYou:
            self.bucket_exists = True


    def _upload_file(self, local_path: str, s3_path:str, is_raw: bool):
        if not self.bucket_exists:
            try:
                self.client.create_bucket(Bucket="raw")
                self.client.create_bucket(Bucket="processed")
            except self.client.exceptions.BucketAlreadyOwnedByYou:
                self.bucket_exists = True

        print(f"Uploading {local_path} to s3://{s3_path}")
        bucket = "raw" if is_raw else "processed"
        self.client.upload_file(local_path, bucket, s3_path)


    def upload_file_raw(self, local_path, s3_path):
        try:
            new_s3_path = f"{s3_path}"
            self._upload_file(local_path, new_s3_path, is_raw=True)
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc() 
            sys.exit(1)


    def upload_file_processed(self, local_path, s3_path):
        new_s3_path = f"{s3_path}"
        self._upload_file(local_path, new_s3_path, is_raw=False)


    def get_keys_since_time(self, 
                        prefix: str, 
                        start_time: datetime) -> List[str]:
        """
        Lists all object keys under a prefix that were modified after the start_time.

        Args:
            prefix: The virtual directory to search within (e.g., 'brazil/aneel/2024/').
            start_time: Only files with LastModified > this time will be returned.

        Returns:
            A sorted list of full S3 keys (e.g., ['raw/2024/f1.csv', 'raw/2024/f2.csv'])

        (AI)
        """
        # full_prefix_path = f"{zone_prefix}{prefix}"
        full_prefix_path = f"{prefix}"
        print(f"Listing files in '{full_prefix_path}' modified since {start_time}", file=sys.stderr)
        
        target_keys_with_time: List[Tuple[datetime, str]] = []
        paginator = self.client.get_paginator('list_objects_v2')
        
        # Set the prefix to search within
        pages = paginator.paginate(Bucket="raw", Prefix=full_prefix_path)
        
        # fix datetime to be timezone agnostic/UTC
        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None:
            # Assumes the user provided a naive time that should be treated as UTC
            start_time = start_time.replace(tzinfo=timezone.utc)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    last_modified: datetime = obj['LastModified']
                    key: str = obj['Key']
                    
                    if last_modified > start_time:
                        target_keys_with_time.append((last_modified, key))

        if not target_keys_with_time:
            return []

        target_keys_with_time.sort(key=lambda x: x[0])
        
        return [key for _, key in target_keys_with_time]

    def download_file(self, s3_path: str, local_path: str, is_raw):
        """
        Downloads an object from S3 to a specific local path.
        """
        bucket = "raw" if is_raw else "processed"
        print(f"Downloading s3://{bucket}/{s3_path} to {local_path}")
        self.client.download_file(bucket, s3_path, local_path)