import os 
import sys 
from pathlib import Path 
from src.exception import CustomException 
from src.logger import logging 
from src.utils import route_filetype


class Extract():
    def __init__(self, file_path):
        self.file_path = file_path 
        
    def extract_text(self):
        """Pass the file path to their specific file extractors,
        and return the extracted content"""
        
        try:
            
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"The specified path was not found: {self.file_path}")
            
            file_content = route_filetype(self.file_path)
        
            logging.info('extracted content from the file')
            return file_content
        
        except Exception as e:
            logging.info('failed to extract content from the file')
            raise CustomException(e, sys)
            
    
    