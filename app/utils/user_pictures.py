import boto3

s3 = boto3.client("s3")
BUCKET_NAME = "chat-app-flask"


def save_picture(file_path, object_name):
    s3.upload_file(file_path, BUCKET_NAME, object_name)


def get_picture(picture_path):
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=picture_path,
    )

    image_data = response["Body"].read()
    return image_data
