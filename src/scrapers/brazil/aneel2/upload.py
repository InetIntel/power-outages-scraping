from Aneel import Aneel


def check_upload(aneel):
    response = aneel.uploader.client.list_objects_v2(Bucket="brazil")

    if "Contents" in response:
        for obj in response["Contents"]:
            print(f"- {obj['Key']}")
    else:
        print("No files found.")


if __name__ == "__main__":
    s = Aneel()
    s.upload()
    check_upload(s)
