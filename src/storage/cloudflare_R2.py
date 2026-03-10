import os
import sys 
import io 
import boto3 
from src.logger import logging
from src.exception import CustomException
from pydantic import BaseModel, PrivateAttr
from dotenv import load_dotenv
from botocore.config import Config
from typing import Any
from fastapi import UploadFile
load_dotenv()

class R2_Storage(BaseModel):
    _client: Any = PrivateAttr()
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")
    
    def model_post_init(self, _):
        ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
        SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
        R2_ENDPOINT = os.getenv("R2_ENDPOINT")
        
        
        if not all([ACCESS_KEY_ID, SECRET_ACCESS_KEY, R2_ENDPOINT]):
            missing = [k for k, v in {
                "ACCESS_KEY_ID":ACCESS_KEY_ID,
                "SECRET_ACCESS_KEY":SECRET_ACCESS_KEY,
                "R2_ENDPOINT":R2_ENDPOINT
            }.items() if not v]
            raise ValueError(f"R2 environment variable not set: {', '.join(missing)}")
    
        
        self._client = boto3.client(
            service_name='s3',
            endpoint_url=R2_ENDPOINT,
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY,
            region_name='auto',
            config=Config(signature_version='s3v4')
        )
        
        
    def upload_resume_to_r2(self, file_obj: UploadFile, filename:str, candidate_id:str, application_id:str):
        """Uploads the candidate resume to R2 storage
        
        Path Structure: resumes/{candidate_id}/{application_id}_{filename}"""
        
        try:
            logging.info("Initializing R2_Storage client")
            
            r2_storage_path = f"resumes/{candidate_id}/{application_id}_{filename}"
            
            self._client.upload_fileobj(
                Fileobj=file_obj.file,
                Bucket=self.BUCKET_NAME,
                Key=r2_storage_path,
                ExtraArgs={
                    "ContentType": file_obj.content_type
                }
            )
            logging.info(f"Uploaded file to R2_Storage: {r2_storage_path}")
            
            return r2_storage_path
        
        except Exception as e:
            logging.info("Failed to upload file to R2_Storage")
            raise CustomException(e, sys)
        
        
        
            
        
    
    