import os 
import sys 
from src.exception import CustomException
from src.logger import logging
import tempfile
from src.utils import check_file_extension, check_file_size
from pathlib import Path 
import shutil
from src.extraction_pipeline.data_extraction import Extract
from src.llm_pipeline.llm_semantic_parsing import Parse_Data
from src.llm_pipeline.normalization_validation import Validate
from src.llm_pipeline.normalization_validation import Normalize

 
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
                        
                        filename = os.path.basename(self.file_path)
                        temp_file_path = os.path.join(temp_dir, filename)
                        
                        # copying the file
                        shutil.copy2(self.file_path, temp_file_path)

                        return temp_dir, temp_file_path
                           
                        
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
    
    check_filepath = FileInput('data/test2_pdf.pdf')  
    temp_dir, file_path = check_filepath.return_valid_file()
    
    file_obj = Extract(file_path)
    file_content = file_obj.extract_text()
    
    llm_obj = Parse_Data(file_content)
    llm_response = llm_obj.llm_parser()
    
    validate_obj = Validate(llm_response)
    validated_data = validate_obj.data_validation()
    
    normalize_obj = Normalize(validated_data)
    normalized_data = normalize_obj.string_normalization()
    
    
    
    shutil.rmtree(temp_dir) 
            
            