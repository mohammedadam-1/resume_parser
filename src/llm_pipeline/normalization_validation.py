import os 
import sys 
from src.exception import CustomException
from src.logger import logging
from typing import List
import re

class Validate():
    def __init__(self, data: dict):
        self.data = data
        
        
    def data_validation(self) -> dict:
        
        try:
            
            if not isinstance(self.data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(self.data).__name__}'")
            
            logging.info('json data loaded for validation')
            
            invalid_values = ["", " ", [], "missing", "null", None]
            
            if self.data["name"] in invalid_values or isinstance(self.data['name'], int):
                self.data["name"] = None
            if self.data["emails"] in invalid_values or isinstance(self.data['emails'], int):
                self.data["emails"] = []
            if self.data["phone_numbers"] in invalid_values:
                self.data["phone_numbers"] = []
            if self.data["linkedin_url"] in invalid_values or isinstance(self.data['linkedin_url'], int):
                self.data["linkedin_url"] = None
            if self.data["github_url"] in invalid_values or isinstance(self.data['github_url'], int):
                self.data["github_url"] = None 
            if self.data["skills"] in invalid_values or isinstance(self.data['skills'], int):
                self.data["skills"] = []
                
            if "projects" in self.data:
                for item in self.data["projects"]:
                    for key, value in item.items():
                        if key == "title":
                            if value in invalid_values or isinstance(value, int):
                                value = None
                        if key == "technologies":
                            if value in invalid_values or isinstance(value, int):
                                value = []
                        if key == "description":
                            if value in invalid_values or isinstance(value, int):
                                value = []          
                    
            if "experience" in self.data:    
                for item in self.data["experience"]:
                    for key, value in item.items():
                        if key == "company":
                            if value in invalid_values or isinstance(value, int):
                                value = None
                        if key == "role":
                            if value in invalid_values or isinstance(value, int):
                                value = None
                        if key == "responsibilities":
                            if value in invalid_values or isinstance(value, int):
                                value = []   
                        if key == "duration_months":
                            if value in invalid_values:
                                value = None                 
                    
            if self.data["certifications"] in invalid_values or isinstance(self.data["certifications"], int):
                self.data["certifications"] = []
            if "education" in self.data:    
                for item in self.data["education"]:
                    for key, value in item.items():
                        if key == "degree":
                            if value in invalid_values or isinstance(value, int):
                                value = None
                        if key == "institution":
                            if value in invalid_values or isinstance(value, int):
                                value = None
                        if key == "details":
                            if value in invalid_values or isinstance(value, int):
                                value = None         
                                
            if self.data["other_info"] in invalid_values:
                self.data["other_info"] = []       
                        
            logging.info("checked for validation of data") 
            
                                          
            return self.data                                
                                
        except Exception as e:
            logging.info("error: check for validation pipeline")
            raise CustomException(e, sys)  
        
        
class Normalize():
    def __init__(self, data):
        self.data = data
        
    def string_normalization(self) -> dict:
        """Normalize the data and return dict"""
        
        try:
            if not isinstance(self.data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(self.data).__name__}'")
            
            logging.info("loaded data for string normalization")
            
            for key, value in self.data.items():
                if isinstance(value, str):
                    self.data[key] = value.strip()
                    
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                if isinstance(sub_value, str):
                                    item[sub_key] = sub_value.strip()
                                elif isinstance(sub_value, list):   
                                    item[sub_key] = [i.strip() if isinstance(i, str) else i for i in sub_value]  
                        elif isinstance(item, str):
                            self.data[key] = item.strip()
                                        
            logging.info("normalized the string type data")      
            print(self.data)                   
            return self.data                         
            
        except Exception as e:
            logging.info("error, unable to normalize the string type data")
            raise CustomException(e, sys)    
        
    def number_normalization(self) -> dict:
        """normalize the numbers into readable format"""
        
        try:
            logging.info("initialized number normalization")
            data = self.string_normalization()
            
            if not isinstance(data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(data).__name__}'")
            logging.info("data loaded for number normalization")
            
            for key, value in data.items():
                if key == "phone_numbers":
                    data[key] = [re.sub(r'\D', '', item) for item in value]
                            
            logging.info("normalized phone numbers data") 
             
             
            return data

        except Exception as e:
            raise CustomException(e, sys)    
        
    def emails(self) -> dict:
        """normalize emails and return data"""
        try:
            
            logging.info("Initialized emails normalization")
            data = self.number_normalization()
            
            if not isinstance(data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(data).__name__}'")
            
            logging.info("loaded data for emails normalization")
            atTheRate = "@"
            for key, value in data.items():
                if key == "emails":
                    data["emails"] = [value.lower()]#[item.lower() for item in value if atTheRate in item]
            print(f"\n\n\n{data}")    
            return data
            
        except Exception as e:
            raise CustomException(e, sys)            
                

        
        
            
        
        
                    
            
            
            
            