import os
import shutil

DATA_DIR = os.environ.get("DATA_DIR", "/data")


class Uploader:
    """File-based storage using a shared volume mount.
    Files are stored at DATA_DIR/<bucket_name>/<key>.
    """

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.base_path = os.path.join(DATA_DIR, bucket_name)
        os.makedirs(self.base_path, exist_ok=True)
        self.client = _VolumeClient()

    def upload_file(self, local_path, s3_path):
        dest = os.path.join(self.base_path, s3_path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(local_path, dest)
        print(f"Uploaded {local_path} -> {dest}")

    def download_file(self, s3_path, local_path):
        src = os.path.join(self.base_path, s3_path)
        if not os.path.exists(src):
            raise FileNotFoundError(f"File not found: {src}")
        os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
        shutil.copy2(src, local_path)
        print(f"Downloaded {src} -> {local_path}")


class _VolumeClient:
    """Provides list_objects_v2 for code that accesses uploader.client directly."""

    def list_objects_v2(self, Bucket, Prefix=""):
        bucket_path = os.path.join(DATA_DIR, Bucket)
        search_root = os.path.join(bucket_path, Prefix) if Prefix else bucket_path
        contents = []
        if os.path.isdir(search_root):
            for root, _, files in os.walk(search_root):
                for fname in files:
                    full = os.path.join(root, fname)
                    key = os.path.relpath(full, bucket_path).replace("\\", "/")
                    contents.append({"Key": key})
        return {"Contents": contents} if contents else {}
