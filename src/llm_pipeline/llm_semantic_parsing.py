import os 
import sys 
from pathlib import Path
from src.exception import CustomException
from src.logger import logging
from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import json



class Parse_Resume_Data():
    
    def __init__(self, data:str) -> dict:
        self.data = data
        self.model = "openai/gpt-oss-120b"
        self.client = Groq()
        
    def llm_resume_parser(self):
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
                              "description": []},],
                "experience": [
                    {
                        "company": "",
                        "role": "",
                        "responsibilities": [],
                        "duration_months": 0
                    },
                ],
                "certifications": [],
                "education": [{"degree": "",
                               "institution": "",
                               "details": ""},],
                "other_info": []
                
            }
            
            system_prompt = f"""
You are a resume parsing and normalization engine.

Your task is to extract information from the provided resume content and return
a STRICTLY VALID JSON object that EXACTLY matches the given schema.

====================
GLOBAL RULES (MANDATORY)
====================

1. You MUST return ONLY a valid JSON object.
2. Do NOT include explanations, comments, markdown, or extra text.
3. Do NOT change schema keys.
4. Do NOT add new fields.
5. Do NOT remove fields.
6. If a value is not present in the resume:
   - use null for scalar fields
   - use an empty array for list fields
7. Do NOT invent, assume, or infer information that is not explicitly present.
8. Preserve factual accuracy at all times.
9. The output must strictly conform to the provided schema.

====================
SKILLS EXTRACTION & EXPANSION RULES
====================

The "skills" field must contain a normalized list of technical skills.

When extracting skills:

1. Include ONLY skills that are explicitly mentioned in the resume.
2. You MAY expand a skill ONLY into:
   - common abbreviations
   - common aliases
   - atomic components of the same skill
3. Do NOT add related but unmentioned technologies.
4. Do NOT infer skills from:
   - job titles
   - company names
   - responsibilities
   - tools commonly associated with a role
5. Do NOT infer proficiency or seniority.
6. Each skill token must be:
   - lowercase
   - concise (1–4 words)
   - technically equivalent to the original skill
7. Limit expansion to a SMALL and CONTROLLED set:
   - Maximum 6 tokens per original skill (including the original).
8. Remove duplicates after expansion.

Examples (for guidance only):

- "AWS Lambda" → ["aws lambda", "aws", "lambda", "serverless"]
- "LLMs" → ["llms", "large language models", "language models"]
- "CI/CD" → ["ci/cd", "cicd", "ci", "cd"]
- "Python" → ["python"]

If no valid expansion exists, include ONLY the original skill.

====================
EXPERIENCE & EDUCATION RULES
====================

- Do NOT infer years of experience unless explicitly stated.
- Do NOT infer per-skill experience.
- Do NOT guess education levels or degrees.
- Preserve education and experience exactly as written, without enrichment.
- Extract all the Experience And Education if the resume has multiple experience and education as list of dictionaries mentioned in output_schema

====================
OUTPUT SCHEMA
====================

Return the result strictly in the following JSON schema:

{output_schema}
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
            
            return data
            
            
        except Exception as e:
            logging.info("Unable to receive LLM response")
            raise CustomException(e, sys)  
        
class Parse_Jd_Data():
    
    def __init__(self, data):
        self.data = data 
        self.model = "openai/gpt-oss-120b"
                
    def llm_jd_parser(self) -> dict:
        """Parses the JDs and returns a json object"""
        try:
            
            logging.info("Initialized parsing of JD data")
            
            
            
            jd_schema = {
                "job_title" : "",
                "required_skills": [],
                "preferred_skills": [],
                "min_experience_months": int,
                "experience_requirements": [],
                "required_education": "",
                "keywords": []
            }
            
            jd_system_prompt = f"""

You are a Job Description (JD) parsing and normalization engine.

Your task is to read the provided Job Description text and return a
STRICTLY VALID JSON object that EXACTLY matches the given output schema.

====================
GLOBAL RULES (MANDATORY)
====================

1. You MUST return ONLY a valid JSON object.
2. Do NOT include explanations, comments, markdown, or extra text.
3. Do NOT change schema keys.
4. Do NOT add new fields.
5. Do NOT remove fields.
6. If a value is not explicitly present in the JD:
   - use null for scalar fields
   - use an empty array for list fields
7. Do NOT invent, assume, or infer requirements.
8. Preserve factual accuracy at all times.
9. The output must strictly conform to the provided schema.

====================
SKILL EXTRACTION RULES (VERY IMPORTANT)
====================

The fields "required_skills" and "preferred_skills" must contain ONLY
clean, atomic, standalone technical skill names.

When extracting skills:

1. Extract ONLY skills that are explicitly mentioned in the JD.
2. Do NOT infer skills based on:
   - job title
   - role expectations
   - industry norms
3. Each skill MUST be:
   - lowercase
   - concise (1–4 words)
   - a standalone technical term
4. Do NOT include:
   - brackets or parentheses
   - explanations
   - examples
   - qualifiers
   - commas inside skill names
5. Do NOT include phrases such as:
   - "experience with"
   - "knowledge of"
   - "hands-on"
   - "familiarity with"
6. Do NOT merge multiple skills into one string.

❌ INVALID:
- "aws (sagemaker, lambda)"
- "mlops (ci/cd, monitoring)"
- "python experience"
- "machine learning & ai"

✅ VALID:
- "aws sagemaker"
- "aws lambda"
- "mlops"
- "ci/cd"
- "python"
- "machine learning"
- "ai"

7. If a skill appears with brackets or examples in the JD:
   - extract ONLY the core skill name
   - extract sub-skills as SEPARATE skill entries if explicitly listed

Example:
JD text: "Experience with AWS (SageMaker, Lambda, EKS)"
Extract:
- "aws sagemaker"
- "aws lambda"
- "aws eks"

====================
REQUIRED vs PREFERRED SKILLS
====================

- Add a skill to "required_skills" ONLY if the JD clearly states it is required or mandatory.
- Add a skill to "preferred_skills" ONLY if the JD clearly states it is optional, preferred, or a plus.
- If the JD does not clearly distinguish, treat the skill as "required".
- Do NOT duplicate the same skill across both lists.

====================
EXPERIENCE RULES
====================

- Extract "min_experience_months" ONLY if an explicit numeric requirement is stated.
- Convert years to months (e.g., 5 years → 60 months).
- If experience is vague or implied, set "min_experience_months" to null.
- Do NOT infer experience per skill.
- Preserve other experience-related statements as human-readable strings in "experience_requirements".

====================
EDUCATION RULES
====================

- Populate "required_education" ONLY if an explicit education requirement is stated.
- If not stated, set "required_education" to null.
- Do NOT infer education requirements.

====================
KEYWORDS RULES
====================

The "keywords" field is for SOFT relevance signals ONLY.

1. Extract short, meaningful keywords explicitly mentioned in the JD.
2. Keywords must be:
   - lowercase
   - concise (1–3 words)
3. Do NOT include any keyword already present in:
   - required_skills
   - preferred_skills
4. Do NOT infer new keywords.
5. Keywords must NOT affect hard constraints.

====================
OUTPUT SCHEMA
====================

Return the result strictly in the following JSON schema:

{jd_schema}
"""


            
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": jd_system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.data
                    },
                ],
                model = self.model
            )
            
            json_data = response.choices[0].message.content
            data = json.loads(json_data)
            logging.info("llm parsed and returned JD as json object")
            
            return data
            
        
        except Exception as e:
            logging.info("llm Failed to parse JD")
            raise CustomException(e, sys)      
            
        
        
                
        
        
                