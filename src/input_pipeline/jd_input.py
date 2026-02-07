import os 
import sys 
from src.exception import CustomException 
from src.logger import logging
from pydantic import BaseModel

class Jd_Parsing(BaseModel):
    data: str
        
    def jd_data(self):
        return self.data