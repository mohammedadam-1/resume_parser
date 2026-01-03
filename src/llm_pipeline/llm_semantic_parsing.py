import os 
import sys 
from pathlib import Path
from src.exception import CustomException
from src.logger import logging
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import json



class Parse_Data():
    def __init__(self, data:str) -> dict:
        self.data = data
        self.model = "openai/gpt-oss-120b"
        self.client = Groq()
        
    def llm_parser(self):
        """Parses the string data into a JSON object"""
        
        try:
            
            if not isinstance(self.data, str):
                raise TypeError(f"Expected 'str', but got '{type(self.data).__name__}'")
            
            client = Groq(
                api_key=os.getenv('GROQ_API_KEY')
            )
            
            output_schema = {
                "name": "",
                "emails": [], 
                "phone_numbers": [],
                "linkedin_url": "",
                "github_url": "",
                "skills": [],
                "projects": [{"title": "",
                              "technologies_used": [],
                              "description": []}],
                "experience": [
                    {
                        "company": "",
                        "role": "",
                        "responsibilities": [],
                        "duration_months": 0
                    }
                ],
                "certifications": [],
                "education": [{"degree": "",
                               "institution": "",
                               "details": ""}],
                "other_info": []
                
            }
            
            system_prompt = f"""
            You are a resume parser AI assistant. Given the data by the user, you have to parse, structure and strictly return 
            the response in the given json format schema.
            
            And 
            
            schema: ""{output_schema}""
            Note: In schema for the values containing lists can hold multiple items and subitems in it, if present.
            """
            
            response = client.chat.completions.create(
                messages=[
                    {
                        'role':'system',
                        'content':system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.data
                    },
                ],
                model=self.model
            )
            
            logging.info(f"received response from {self.model} LLM")
            json_data =  response.choices[0].message.content
            data = json.loads(json_data)
            logging.info("loaded json object as python dict")
            print(data,"\n\n")
            return data
            
            
        except Exception as e:
            logging.info("Unable to receive LLM response")
            raise CustomException(e, sys)  
        
        
                
        
        
                