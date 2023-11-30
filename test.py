import boto3
aws_access_key_id = "AKIAUFTPQN5O75N6A7EW"
aws_secret_access_key = "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"

def list_files_with_prefix(prefix):
    s3 = boto3.client('s3',region_name='ap-southeast-2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    response = s3.list_objects_v2(Bucket="findstock", Prefix=prefix)

    files = []
    if 'Contents' in response:
        for item in response['Contents']:
            files.append(item['Key'])

    return files

prefix = '123'  # 您要搜尋的前綴
files = list_files_with_prefix(prefix)

print("找到的檔案:", files)