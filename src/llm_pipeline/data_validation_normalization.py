import sys 
from src.exception import CustomException
from src.logger import logging
import re
from src.utils import _recursive_strip, _recursive_lower
from pydantic import BaseModel, Field, field_validator
from typing import Any

# class Projects(BaseModel):
#     title: str | None = None
#     technologies: list[str] = Field(default_factory=list)
#     description: list[str] = Field(default_factory=list)
    
class Education(BaseModel):
    degree_level: str | None = None
    degree_name: str | None = None
    field: str | None = None
    
# class Experience(BaseModel):
#     company: str | None = None
#     role: str | None = None
#     responsibilities: list[str] = Field(default_factory=list)


class ResumeSchema(BaseModel):
    name: str | None = None
    emails: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)
    linkedin_url: str | None = None
    github_url: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    # projects: list[Projects] = Field(default_factory=list)
    total_experience_months: int | None = None
    # experience: list[Experience] = Field(default_factory=list)
    # certifications: list[str] = Field(default_factory=list) 
    keywords: list[str] = Field(default_factory=list)

    @field_validator('emails', 'phone_numbers', 'skills', 'education', 'keywords', mode='before')
    @classmethod
    def ensure_list(cls, v: Any) -> Any:
        if v is None:
            return []
        return v

class ValidateResume(BaseModel):
    data: ResumeSchema
  
class RequiredEducation(BaseModel):
    degree_level: str | None = None
    degree_name: str | None = None
    field: str | None = None
    
class JdSchema(BaseModel):
    job_title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_experience_months: int | None = None
    # experience_requirements: list[str] = Field(default_factory=list)
    required_education: list[RequiredEducation] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    
    @field_validator('required_education', 'required_skills', 'preferred_skills', 'keywords', mode='before')
    @classmethod
    def ensure_list(cls, v: Any) -> Any:
        if v is None:
            return []
        return v
    
class ValidateJd(BaseModel):   
    data: JdSchema
    
  
class NormalizeResume(BaseModel):
    data: ResumeSchema
    
    def str_norm(self) -> ResumeSchema:
        """Strip whitespaces and normalize the strings data"""
        try:
            temp_dict = self.data.model_dump()
            cleaned_dict = _recursive_strip(temp_dict)
            
            self.data = self.data.__class__(**cleaned_dict)            
            logging.info("Cleaned and returned 'str' type data")
            
            return self.data
        
        except Exception as e:
            logging.info("Unable to strip data, please debug")
            raise CustomException(e, sys)
            
      
    def number_normalization(self) -> ResumeSchema:
        """normalize the numbers into readable format"""
        
        try:
            logging.info("initialized number normalization")
            model = self.str_norm()
            
            if model.phone_numbers:
                normalized_numbers = [re.sub(r"\D","", str(item)) for item in model.phone_numbers]
                logging.info("normalized phone numbers data") 
                model.phone_numbers = list(set(normalized_numbers)) 
                
            return model

        except Exception as e:
            logging.info("Unable to normalize numbers data")
            raise CustomException(e, sys)    
        
    def emails(self) -> ResumeSchema:
        """validate and normalize emails and return data"""
        try:
            
            logging.info("Initialized emails normalization")
            model = self.number_normalization()
            
            logging.info("loaded data for emails normalization")
            
            atTheRate = "@"
            if model.emails:
                model.emails = list(set([item.lower() for item in model.emails if atTheRate in item]))
            
            logging.info("Normalized and returned emails data")    
            return model
            
        except Exception as e:
            logging.info("Unable to normalize emails, please debug")
            raise CustomException(e, sys)  
    
    def lower_keys(self) -> ResumeSchema:
        """lower the values of keys"""
        
        try:
            model = self.emails()
            temp_dict = model.model_dump()
            normalized_dict = _recursive_lower(temp_dict)
            logging.info("lowered the values of keys")  
            
            model = model.__class__(**normalized_dict)
                  
            return model
        
        except Exception as e:
            logging.info("Unable to lower the keys")
            raise CustomException(e, sys)
        
    def remove_duplicates(self) -> ResumeSchema:
        """Remove duplicates from the list"""    
        
        try:
            model = self.lower_keys()
            target_keys = {"skills", "certifications", "keywords"}
            for key, value in model:
                if key in target_keys:
                    deduplicated = list(set(value))
                    setattr(model, key, deduplicated)
            logging.info("Successfully deduplicated target fields")
                 
            return model           
            
        except Exception as e:
            logging.info("Unable to remove duplicates")
            raise CustomException(e, sys)
     
class NormalizeJd(BaseModel):
    data: JdSchema
    
    def strip_str(self) -> JdSchema:
        """normalize the str type and return data"""

        try:
            logging.info("Initialized JD data normalization")
            temp_dict = self.data.model_dump() 
            logging.info("loaded data for str normalization")    
            cleaned_dict = _recursive_strip(temp_dict)     
            
            self.data = self.data.__class__(**cleaned_dict)
            logging.info("normalized str and returned data")
            return self.data

        except Exception as e:
            logging.info("Unable to normalize str, please debug")
            raise CustomException(e, sys)    
        
    def lowerjd_keys(self) -> JdSchema:
        """lower the keys in Jd and return"""
        
        try:
            model = self.strip_str()
            temp_dict = model.model_dump()
            normalized_dict = _recursive_lower(temp_dict)
            logging.info("lowered the values of keys")  
            
            model = model.__class__(**normalized_dict)     
            return model
            
        except Exception as e:
            logging.info("Unable to lower keys, please debug")
            raise CustomException(e, sys)
        
    def removejd_duplicates(self) -> JdSchema:
        """remove duplicates from Jd keys"""
        
        try:
            model = self.lowerjd_keys()
            target_keys = {"required_skills", "preferred_skills", "keywords"}
            
            for key, value in model:
                if key in target_keys:
                    deduplicated = list(set(value))
                    setattr(model, key, deduplicated)  
            logging.info("removed duplicates from the Jd keys")
            return model      
            
        except Exception as e:
            logging.info("Unable to remove duplicates")
            raise CustomException(e, sys)    
            
            
            

      
            
            