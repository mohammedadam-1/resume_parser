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
    
def _recursive_strip(item):
    """strip and return data"""
    try:
        
        if isinstance(item, str):
            return item.strip()
        elif isinstance(item, list):
            return [_recursive_strip(i) for i in item]
        elif isinstance(item, dict):
            return {k: _recursive_strip(v) for k, v in item.items()}
        logging.info("striped data from strings successfully")
        
        return item
    
    except Exception as e:
        raise CustomException(e, sys)
    
    
def _recursive_lower(item):
    """convert the strings into lower and return data"""
    
    try:
        if isinstance(item, str):
            return item.lower()
        elif isinstance(item, list):
            return [_recursive_lower(i) for i in item]
        elif isinstance(item, dict):
            return {k: _recursive_lower(v) for k, v in item.items()}
        
        return item
        
    except Exception as e:
        raise CustomException(e, sys)    
        
        