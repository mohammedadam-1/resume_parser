import os 
import sys 
from src.exception import CustomException
from src.logger import logging
from typing import List
import re
from src.utils import _recursive_strip, _recursive_lower

class Validate():
    def __init__(self, data: dict):
        self.data = data
        
        
    def data_validation(self) -> dict:
        
        try:
            
            if not isinstance(self.data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(self.data).__name__}'")
            
            logging.info('json data loaded for validation')
            
            invalid_values = ["", " ", [], "missing", "null", None, 0]
            
            resume_list = ["name", "emails", "phone_numbers", "linkedin_url", "github_url", "skills",
                           "certifications", "other_info"]
            for item in resume_list:
                if item in self.data:
            
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
            
        # check for validation of JD data
            jd_list = ["job_title", "required_skills", "preferred_skills", "min_experience_months",
                       "experience_requirements", "required_education", "keywords"]
            for item in jd_list:
                
                if item in self.data:
                    
                    if self.data["job_title"] in invalid_values or isinstance(self.data["job_title"], int):
                        self.data["job_title"] = None 
                        
                    if self.data["required_skills"] in invalid_values or isinstance(self.data["required_skills"], int):
                        self.data["required_skills"] = []
                        
                    if self.data["preferred_skills"] in invalid_values or isinstance(self.data["preferred_skills"], int): 
                        self.data["preferred_skills"] = []
                        
                    if self.data["min_experience_months"] in invalid_values:
                        self.data["min_experience_months"] = None
                        
                    if self.data["experience_requirements"] in invalid_values or isinstance(self.data["experience_requirements"], int):   
                        self.data["experience_requirements"] = []
                        
                    if self.data["required_education"] in invalid_values or isinstance(self.data["required_education"], int): 
                        self.data["required_education"] = None 
                        
                    if self.data["keywords"] in invalid_values or isinstance(self.data["keywords"], int):    
                        self.data["keywords"] = []
                    
                        
            logging.info("checked for validation of data") 
            
                                          
            return self.data                                
                                
        except Exception as e:
            logging.info("error: check for validation pipeline")
            raise CustomException(e, sys)  
        
        
class Normalize():
    def __init__(self, data: dict):
        self.data = data
    
    
    def str_norm(self) -> dict:
        """normalize the strings data"""
        try:
            
            if not isinstance(self.data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(self.data).__name__}'")
        
            self.data = _recursive_strip(self.data)
           
            logging.info("Cleaned and returned 'str' type data")
            
            return self.data
        
        except Exception as e:
            logging.info("Unable to strip data, please debug")
            raise CustomException(e, sys)
            
      
    def number_normalization(self) -> dict:
        """normalize the numbers into readable format"""
        
        try:
            logging.info("initialized number normalization")
            data = self.str_norm()
            
            if not isinstance(data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(data).__name__}'")
            logging.info("data loaded for number normalization")
            
            for key, value in data.items():
                if key == "phone_numbers":
                    data[key] = list(set([re.sub(r'\D', '', item) for item in value]))
                            
            logging.info("normalized phone numbers data") 
             
            return data

        except Exception as e:
            logging.info("Unable to normalize numbers data")
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
                    data[key] = list(set([item.lower() for item in value if atTheRate in item]))
            
            logging.info("Normalized and returned emails data")    
            return data
            
        except Exception as e:
            logging.info("Unable to normalize emails, please debug")
            raise CustomException(e, sys)  
        
    def skills(self) -> dict:
        """normalize the skills data and return data"""   
        
        try:
            
            data = self.emails()
            for key, value in data.items():
                if key == "skills":
                    data[key] = list(set([item.lower() for item in value]))
            logging.info("normalized skills data")
            
            return data        
            
        except Exception as e:
            logging.info("Unable to normalize skills data, please debug")
            raise CustomException(e, sys)
        
    def projects(self) -> dict:
        
        data = self.skills()
        
        for key, value in data.items():
            if key == "projects":
                data[key] = _recursive_lower(value)
       
        logging.info("normalized the strings to lower")  

        return data

    def normalize_jd(self) -> dict:
        """normalize the JD data and return data"""

        try:
            logging.info("Initialized JD data normalization")

            if not isinstance(self.data, dict):
                raise TypeError(f"Expected 'dict', but got '{type(self.data).__name__}'")

            logging.info("loaded data for JD normalization") 

            data = self.str_norm()   
            
            for key, value in data.items():
                if key == "required_skills" or key == "preferred_skills" or key == "keywords":
                    data[key] = _recursive_lower(value) 
            
            logging.info("normalized the JD data")

            return data

        except Exception as e:
            logging.info("Unable to normalize JD data, please debug")
            raise CustomException(e, sys)    
            
            

      
            
            