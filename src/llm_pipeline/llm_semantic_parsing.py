import os 
import sys 
from src.exception import CustomException
from src.logger import logging
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
from src.utils import parse_experience_from_resume
from src.utils import safe_json_loads
from pydantic import BaseModel, PrivateAttr, Field, ConfigDict
from functools import lru_cache
import copy


class ParseResumeData(BaseModel):
    data: str # default none and break loop
    model: str = "openai/gpt-oss-120b"
    model_temperature: float = 0.0
    _client: Groq = PrivateAttr()
     # Configuration to allow the custom Groq type
    model_config = ConfigDict(arbitrary_types_allowed=True) 
    
    def model_post_init(self, _):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self._client = Groq(
                api_key=api_key
            )
        
    def llm_resume_parser(self) -> dict:
        """Parses the string data into a JSON object"""
        
        try:
            
            resume_schema = {
                "type":"object",
                "properties": {
                    "name": {"type": "string"},
                    "emails": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "phone_numbers": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "linkedin_url": {"type": ["string", "null"]},
                    "github_url": {"type": ["string", "null"]},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "total_experience_months" : {"type": ["integer", "null"]},
                    "education": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "degree_level": {"type": "string"},
                                "degree_name": {"type": "string"},
                                "field": {"type": "string"}
                            },
                            "required": ["degree_level", "degree_name", "field"],
                            "additionalProperties": False
                        }
                    },
                     "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": [
                    "name", 
                    "emails", 
                    "phone_numbers", 
                    "linkedin_url",
                    "github_url",
                    "skills", 
                    "total_experience_months",
                    "education", 
                    "keywords"
                ],
                "additionalProperties": False
                }
            
            system_prompt = f"""

You are a resume parsing and normalization engine.

Your task is to extract information from the provided resume content and return
a STRICTLY VALID JSON object that EXACTLY matches the given schema.

====================
GLOBAL RULES (MANDATORY)
====================

1. You MUST return ONLY a valid JSON object matching the schema.
2. Do NOT include explanations, comments, markdown, or extra text.
3. Do NOT change schema keys.
4. Do NOT add new fields.
5. Do NOT remove fields.
6. If a value is not present in the resume:
   - use null for nullable fields
   - use an empty array [] for array fields
   - use empty string "" for required string fields
7. Do NOT invent, assume, or infer information that is not explicitly present.
8. Preserve factual accuracy at all times.

====================
SKILLS EXTRACTION & EXPANSION RULES
====================

1. Include ONLY skills explicitly mentioned in the resume.
2. You MAY expand a skill ONLY into:
   - common abbreviations
   - common aliases
   - atomic components of the same skill
3. Do NOT add related or unmentioned technologies.
4. Do NOT infer skills from job titles, companies, or responsibilities.
5. Skill tokens must be lowercase and concise.
6. Limit expansion to a maximum of 6 tokens per original skill.

====================
EXPERIENCE RULES
====================

- ALWAYS set "total_experience_months" to null.
- Experience calculation is handled externally.

====================
EDUCATION EXTRACTION RULES
====================

1. Extract ONLY the highest completed or currently pursuing qualification.
2. Normalize degree_level into ONE of:
   - "phd"
   - "masters"
   - "bachelors"
   - "diploma"
   - "high_school"
3. If no education is found, return an empty array [].

====================
KEYWORDS RULES
====================

1. Extract short, meaningful keywords explicitly mentioned in the resume.
2. Keywords must be lowercase and concise (1–3 words).
3. Do NOT include keywords already in skills.
"""

            response = self._client.chat.completions.create(
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
                model=self.model,
                temperature=self.model_temperature,
                response_format={
                    "type":"json_schema",
                    "json_schema": {
                        "name": "resume_schema",
                        "strict":True,
                        "schema": resume_schema
                    }
                }
            )
            
            logging.info(f"received response from {self.model} LLM")
            json_data =  response.choices[0].message.content
            data = safe_json_loads(json_data)
            logging.info("loaded json object as python dict")
            
            llm_response = self.load_candidate_experience(data)
            logging.info("loaded experience of candidate and returned llm response")
            
            return llm_response
            
        except Exception as e:
            logging.info("Unable to receive LLM response")
            raise CustomException(e, sys)  
        
    def load_candidate_experience(self, llm_data:dict) -> dict:
        """Load and store the candidate experience in duration_months"""
        try:
            
            total_exp = parse_experience_from_resume(self.data)
            llm_data["total_experience_months"] = total_exp
            return llm_data
        
        except Exception as e:
            logging.info("Failed to load candidate experience in 'total_experience_months'")
            raise CustomException(e, sys)

@lru_cache(maxsize=50)
def _cached_jd_parser(data: str, model: str , model_temperature: float) -> dict:
    """
    Cached JD parsing function.
    
    Args:
        jd_text: The job description text (must be hashable)
        model: The model name
        model_temperature: The model temperature
        client: Groq
        
    Returns:
        Parsed JD as dictionary
    """
    
    try:
        logging.info("Cache miss - parsing JD with LLM")
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        _client = Groq(api_key=api_key)
        
        jd_schema = {
            "type": "object",
            "properties": {
                "job_title": {"type": "string"},
                "required_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "preferred_skills": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "min_experience_months": {"type": ["integer", "null"]},
                "required_education": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "degree_level": {"type": "string"},
                            "degree_name": {"type": "string"},
                            "field": {"type": "string"}
                        },
                        "required": ["degree_level", "degree_name", "field"],
                        "additionalProperties": False
                    }
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": [
                "job_title",
                "required_skills",
                "preferred_skills",
                "min_experience_months",
                "required_education",
                "keywords"
            ],
            "additionalProperties": False
        }
            
        jd_system_prompt = """
You are a Job Description (JD) parsing and normalization engine.

Your task is to read the provided Job Description text and return a
STRICTLY VALID JSON object that EXACTLY matches the given schema.

====================
GLOBAL RULES (MANDATORY)
====================

1. You MUST return ONLY a valid JSON object matching the schema.
2. Do NOT include explanations, comments, markdown, or extra text.
3. If a value is not present:
   - use null for nullable fields
   - use empty array [] for array fields
   - use empty string "" for required string fields
4. Do NOT invent or infer requirements.

====================
SKILL EXTRACTION RULES
====================

1. Extract ONLY skills explicitly mentioned in the JD.
2. Each skill must be lowercase and concise.
3. Do NOT include brackets, parentheses, or explanations.
4. If a skill has sub-components (e.g., "AWS (Lambda, S3)"):
   - Extract as separate skills: ["aws lambda", "aws s3"]

====================
REQUIRED vs PREFERRED SKILLS
====================

- "required_skills": Skills marked as required or mandatory
- "preferred_skills": Skills marked as optional, preferred, or a plus
- If unclear, treat as required

====================
EXPERIENCE RULES
====================

- Extract "min_experience_months" ONLY if explicitly stated
- Convert years to months (e.g., 5 years → 60)
- If vague or not stated, use null

====================
EDUCATION RULES
====================

1. Extract minimum required qualification only
2. degree_level must be one of: "phd", "masters", "bachelors", "diploma", "high_school"
3. If no education requirement, return empty array []
"""
        response = _client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": jd_system_prompt
                    },
                    {
                        "role": "user",
                        "content": data
                    },
                ],
                model = model,
                temperature=model_temperature,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name":"jd_schema",
                        "strict": True,
                        "schema": jd_schema
                    }
                }
            )
            
        json_data = response.choices[0].message.content
        logging.info("LLM parsed and returned JD as json object")
            
        data = safe_json_loads(json_data)  
        logging.info("Loaded json obj into python dict")    
        logging.info("Cached JD parsing result")                          
        
        return copy.deepcopy(data) # clear concept here - shallow and deep copy
        
    except Exception as e:
        logging.info("Error in cached_jd_parser method")
        raise CustomException(e, sys)
    
class ParseJdData(BaseModel):
    data: str = Field(min_length=1)
    model: str = "openai/gpt-oss-120b"
    model_temperature: float = 0.0
    _client: Groq = PrivateAttr()
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
          
    def llm_jd_parser(self) -> dict:
        """
        Parses the JDs and returns a json object.
        Uses cached function for identical JD texts.
        """
        try:
            logging.info("Initialized JD parsing...")
            return _cached_jd_parser(data=self.data, model=self.model, model_temperature=self.model_temperature)
            
        except Exception as e:
            logging.info("llm Failed to parse JD")
            raise CustomException(e, sys)      
            
        
        
                
        
        
                