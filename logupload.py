import boto3
from datetime import datetime

def upload_file_to_s3(file_path, bucket_name):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name, file_extension = file_path.split('.')
    new_file_name = f"{file_name}_{timestamp}.{file_extension}"

    s3 = boto3.client('s3')
    try:
        # Upload the file with the new name to S3
        s3.upload_file(file_path, bucket_name, new_file_name)
        print(f"Log File uploaded successfully with timestamp: {timestamp}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

if __name__ == "__main__":
    bucket_name = "ad-user-disable-logs"
    file_path = "Deleted_AD_Account.txt"
    upload_file_to_s3(file_path, bucket_name)
