from qiniu import Auth,put_file

def get_token(access_key,secret_key,bucket_name,timeout=3600,policy=None):
    q = Auth(access_key,secret_key)
    return q.upload_token(bucket=bucket_name,expires=timeout,policy=policy)