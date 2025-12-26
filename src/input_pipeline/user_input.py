import os 
import sys 
from src.exception import CustomException
from src.logger import logging
import tempfile
from src.utils import check_file_extension, check_file_size
from pathlib import Path 

 
class FileInput():
    def __init__(self, file_path):
        self.file_path : str = file_path
        
        
        
    def return_valid_file(self):
        """User uploads a resume file. Based on the conditions the
        file is uploaded successfully, else"""
        
        try:
            
            if os.path.exists(self.file_path):
                logging.info(f'the file {self.file_path} exists')
                file_type = check_file_extension(self.file_path)
                
                if file_type == self.file_path:
                    logging.info('file extension is valid, return file path')
                    file_size_type = check_file_size(self.file_path)
                    
                    if file_size_type == self.file_path:
                        logging.info('file size is valid, return file path')
                        
                        temp_dir = tempfile.mkdtemp()
                        with open(self.file_path, "w", encoding='utf-8') as f:
                            f.write(temp_dir)
                            logging.info('file saved in temp dir')
                            
                            return self.file_path   
                        
                    else:
                        print(f"invalid file size, filesize supported till 100Mb")   
                        
                else:
                    print(f"Please check and re-upload a valid file.")
                    
            else:
                print("File does not exists") 
                   
        except Exception as e:
            logging.info('invalid file')
            raise CustomException(e, sys)
        
        
if __name__ == '__main__':
    
    check_filepath = FileInput('data/test.txt')  
    file_path = check_filepath.return_valid_file()
                    
                    
            
            