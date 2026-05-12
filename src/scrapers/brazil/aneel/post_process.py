from utils.upload import Uploader

if __name__ == "__main__":
    uploader = Uploader("brazil")
    response = uploader.client.list_objects_v2(Bucket="brazil")

    contents = response.get("Contents", [])
    if contents:
        for obj in contents:
            print(f"- {obj['Key']}")
    else:
        print("No files found.")
