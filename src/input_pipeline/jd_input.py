import os 
import sys 
from src.exception import CustomException 
from src.logger import logging 

class Jd_Parsing():
    def __init__(self, data:str):
        self.data = data 
        
    def jd_data(self):
        return self.data