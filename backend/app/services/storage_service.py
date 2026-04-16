import cloudinary
from app.config import settings
import boto3


cloudinary.config( 
  cloud_name = settings.cloud_name,
  api_key = settings.api_key,
  api_secret = settings.api_secret,
)

s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key,
    aws_secret_access_key=settings.aws_secret_key,
    region_name=settings.aws_region
)