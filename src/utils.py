import os 
import sys 
from pathlib import Path
from src.exception import CustomException
from src.logger import logging
import pymupdf


def check_file_extension(file_path):
    try:
            
        filepath = Path(file_path)
        logging.info("file path loaded successfully")
        if filepath.suffix.lower() == ".pdf":
            return file_path
        elif filepath.suffix.lower() == ".docx":
            return file_path
        elif filepath.suffix.lower() == ".txt":
            return file_path
        else:
            logging.info('Invalid file: Upload valid filetype')
            print(f"invalid filetype. only accepted pdf, docx, txt filetype")
            
    except Exception as e:
        raise CustomException(e, sys)
    
    
def check_file_size(file_path):
    try:
        
        file_size = Path(file_path).stat().st_size
        file_size = bytes(file_size)
        min_file_size = b'\x00' * 100 * 10
        max_file_size = 5 * 1024 * 1024
        max_file_size = bytes(max_file_size)
        if file_size >= min_file_size and file_size <= max_file_size:
            logging.info('valid file size')
            return file_path    
        
        else:
            logging.info('invalid file size')
            print(f"invalid file size: {file_size}. Please upload file greater than 100bytes and less than 100Mb size")
        
    except Exception as e:
        raise CustomException(e, sys)    
    
    
def route_filetype(file_path):
    """route to specific file extension extractor"""   
    
    try:
        
        filepath = Path(file_path)
        if filepath.suffix.lower() == '.pdf':
            doc = pymupdf.open(filepath)
            for page in doc:
                text = page.get_text()
        
        return text    
            
    except Exception as e:
        raise CustomException(e, sys) 
    
    
        
        
        
        