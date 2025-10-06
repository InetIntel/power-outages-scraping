from Aneel import Aneel 
import boto3
from botocore.client import Config

def check_upload():
    s3 = boto3.client(
        "s3",
        endpoint_url="http://host.docker.internal:9000",  # Your MinIO server URL
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    response = s3.list_objects_v2(Bucket="brazil")

    if "Contents" in response:
        for obj in response["Contents"]:
            print(f"- {obj['Key']}")
    else:
        print("No files found.")

if __name__ == "__main__":
    s = Aneel()
    s.upload()
    check_upload()
