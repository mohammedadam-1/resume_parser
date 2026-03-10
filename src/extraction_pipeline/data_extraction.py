import os 
import sys 
from src.exception import CustomException 
from src.logger import logging 
from src.utils import route_filetype, check_file_len
from models.schemas import FilePath
from fastapi import HTTPException
from pydantic import BaseModel
import io



class Extract(BaseModel):
    file_bytes: bytes
        
    def extract_text(self) -> str:
        # """Extract text from the given file, based on its type."""
        
        try:
            
            # if not os.path.exists(self.file_path):
            #     raise FileNotFoundError(f"The specified path was not found: {self.file_path}")
            
            file_content = route_filetype(stream=self.file_bytes)
            check_file_len(file_content)    
            logging.info('extracted content from the file')
            
            return file_content
        
        except HTTPException:
            raise
        
        except Exception as e:
            logging.info('failed to extract content from the file')
            raise CustomException(e, sys)
        
        
    
    