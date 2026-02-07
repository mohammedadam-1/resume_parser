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


class ParseResumeData(BaseModel):
    data: str # default none and break loop
    model: str = "openai/gpt-oss-120b"
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
                    },
                ],
                "total_experience_months": None,
                "certifications": [],
                "education": [{"degree_level": "",
                               "degree_name": "",
                               "field": ""},],
                "keywords": []
                
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

1. Include ONLY skills explicitly mentioned in the resume.
2. You MAY expand a skill ONLY into:
   - common abbreviations
   - common aliases
   - atomic components of the same skill
3. Do NOT add related or unmentioned technologies.
4. Do NOT infer skills from job titles, companies, or responsibilities.
5. Do NOT infer proficiency or seniority.
6. Skill tokens must be:
   - lowercase
   - concise (1–4 words)
   - technically equivalent
7. Limit expansion to a maximum of 6 tokens per original skill.
8. Remove duplicates after expansion.

====================
EXPERIENCE RULES
====================

- Extract experience entries as written.
- Do NOT infer years, durations, or seniority.
- You MUST NOT extract or reason about experience dates.
- For ALL experience entries, set all date-related fields to null.
- Date extraction and experience calculation are handled externally.

====================
EDUCATION EXTRACTION RULES (IMPORTANT)
====================

1. Extract ONLY the highest completed or currently pursuing qualification.
2. Ignore lower or earlier qualifications once the highest is identified.
3. Do NOT infer or guess degree level, field, or institution.
4. Preserve wording exactly as written where applicable.
5. Normalize degree level into ONE of:
   - phd
   - masters
   - bachelors
   - diploma
   - high_school

6. Extract ONLY the primary field / specialization (if explicitly stated).
7. Do NOT infer related or equivalent fields.
8. Institution name must be extracted only if explicitly mentioned.
9. Graduation year must be extracted only if explicitly mentioned; otherwise null.
10. Do NOT rank or judge institutions.
11. Do NOT extract multiple education entries.

====================
KEYWORDS RULES
====================

The "keywords" field is for SOFT relevance signals ONLY.

1. Extract short, meaningful keywords explicitly mentioned in the resume.
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

{output_schema}
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
                model=self.model
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
    
class ParseJdData(BaseModel):
    data: str = Field(min_length=1)
    model: str = "openai/gpt-oss-120b"
    _client: Groq = PrivateAttr()
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def model_post_init(self, _):
        api_key = os.getenv("GROQ_API_KEY")
        self._client = Groq(api_key=api_key)
                
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
                "required_education": 
                    [{"degree_level": "",
                      "degree_name": "",
                      "field": ""},],
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
EDUCATION EXTRACTION RULES
====================

1. Extract ONLY the minimum required qualification mentioned in the job description.
2. Extract degree_level strictly as one of:
   - phd
   - masters
   - bachelors
   - diploma
   - high_school
3. Extract ONLY the primary field / specialization (if explicitly stated).
4. Do NOT infer related or equivalent fields.
5. Institution name must be extracted only if explicitly mentioned.
6. Graduation year must be extracted only if explicitly mentioned; otherwise null.
7. Do NOT rank or judge institutions.
8. Do NOT extract multiple education entries.
9. If the job description has NO education requirement, set the entire education object to null.


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
            response = self._client.chat.completions.create(
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
            logging.info("Llm parsed and returned JD as json object")
            
            data = safe_json_loads(json_data)  
            logging.info("Loaded json obj into python dict")                              
            
            return data
            
        except Exception as e:
            logging.info("llm Failed to parse JD")
            raise CustomException(e, sys)      
            
        
        
                
        
        
                