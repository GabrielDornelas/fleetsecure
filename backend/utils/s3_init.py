import os
import boto3
import logging
import time
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# S3 setup
BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'fleetsecure')
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL', 'http://localstack:4566')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'test')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'test')
AWS_REGION = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

def create_s3_bucket():
    """Create S3 bucket in LocalStack if it doesn't exist"""
    # Wait for localstack to be ready
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            # Create S3 client
            s3_client = boto3.client(
                's3',
                endpoint_url=AWS_ENDPOINT_URL,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            
            # Check if bucket exists
            try:
                s3_client.head_bucket(Bucket=BUCKET_NAME)
                logger.info(f"Bucket {BUCKET_NAME} already exists")
                return
            except ClientError:
                logger.info(f"Creating bucket: {BUCKET_NAME}")
                s3_client.create_bucket(Bucket=BUCKET_NAME)
                
                # Configure bucket for public access
                s3_client.put_bucket_acl(
                    ACL='public-read',
                    Bucket=BUCKET_NAME
                )
                
                # Configure bucket CORS
                try:
                    cors_configuration = {
                        'CORSRules': [{
                            'AllowedHeaders': ['*'],
                            'AllowedMethods': ['GET', 'PUT', 'POST'],
                            'AllowedOrigins': ['*'],
                            'ExposeHeaders': ['ETag'],
                            'MaxAgeSeconds': 3000
                        }]
                    }
                    
                    s3_client.put_bucket_cors(
                        Bucket=BUCKET_NAME,
                        CORSConfiguration=cors_configuration
                    )
                    logger.info(f"CORS configuration applied to bucket {BUCKET_NAME}")
                except Exception as e:
                    logger.warning(f"Failed to configure CORS on bucket: {e}")
                
                logger.info(f"Bucket {BUCKET_NAME} created successfully")
                return
                
        except Exception as e:
            logger.warning(f"Failed to create S3 bucket (attempt {retry_count+1}/{max_retries}): {e}")
            retry_count += 1
            time.sleep(2)
    
    logger.error(f"Failed to create S3 bucket after {max_retries} attempts")

if __name__ == "__main__":
    create_s3_bucket() 