from models.schemas import FilePath
import sys 
from pathlib import Path
from src.exception import CustomException
from src.logger import logging
import re 
from datetime import datetime 
from dateutil.relativedelta import relativedelta
import pdfplumber 
from fastapi import HTTPException, status
import json  
import io
import numpy as np


def check_file_extension(file_path: FilePath) -> FilePath:
    """Check if the file extension is supported."""
    
    filepath = Path(file_path)
    logging.info("file path loaded successfully")
    allowed_extensions = {".pdf", ".txt", ".docx"}
    extension = filepath.suffix.lower()
    
    if extension in allowed_extensions:
        logging.info(f"File {filepath.name} is valid.")
        return file_path
    
    error_msg = f"Unsupported file type '{extension}'. Please upload a .pdf, .docx, or .txt file."
    logging.error(error_msg)
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error_msg
    )
    
    
def check_file_size(file_size: int) -> None:
    """Check if the file size is within the allowed limits.""" 
       
    MIN_SIZE: int = 100 # 100 bytes
    MAX_SIZE: int = 2 * 1024 * 1024 # 2 Megabytes
    
    if MIN_SIZE <= file_size <= MAX_SIZE:
        logging.info('valid file size') 
        return 
          
    
    error_msg = f"Invalid file size. Limits: 100B to 2MB."
    logging.info('invalid file size')
    raise HTTPException(
        status_code=status.HTTP_413_CONTENT_TOO_LARGE,
        detail=error_msg
    )

def check_file_len(resume_text:str) -> None:
    """Check len of file content"""
    
    if len(resume_text.strip()) < 100:
        logging.warning(f"Resume content too short: {len(resume_text)} chars")
            
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume content is too short. Please upload a valid resume with at least 100 characters of text."
            )
    
def route_filetype(stream: bytes) -> str:
    # """Route to specific file extractors based on file type and extract content"""   
    
    try:
        
        file_obj = io.BytesIO(stream)
        full_text = []

        with pdfplumber.open(file_obj) as pdf:
            for page in pdf.pages: # Use .pages for clarity
                page_text = page.extract_text() # .extract_text() is the standard method
                if page_text:
                    full_text.append(page_text)
        
        # Join pages and clean up extra newlines/spaces
        cleaned_text = "\n".join(full_text).strip()
        return cleaned_text  
            
    except Exception as e:
        logging.info('failed to route filetype for extraction')
        raise CustomException(e, sys) 
    
def _recursive_strip(item):
    """strip and return data"""
    try:
        
        if isinstance(item, str):
            return item.strip()
        elif isinstance(item, list):
            return [_recursive_strip(i) for i in item]
        elif isinstance(item, dict):
            return {k: _recursive_strip(v) for k, v in item.items()}
        logging.info("striped data from strings successfully")
        
        return item
    
    except Exception as e:
        raise CustomException(e, sys)
    
    
def _recursive_lower(item):
    """convert the strings into lower and return data"""
    
    try:
        if isinstance(item, str):
            return item.lower()
        elif isinstance(item, list):
            return [_recursive_lower(i) for i in item]
        elif isinstance(item, dict):
            return {k: _recursive_lower(v) for k, v in item.items()}
        
        return item
        
    except Exception as e:
        raise CustomException(e, sys)    
          
    
def format_date(date:str) -> datetime:
    """format date and return"""
    
    try:
        date_formats = [
            "%b",
            "%B",
            "%b %Y",
            "%b %y",
            "%B %Y",
            "%B %y",
            "%d-%m-%Y",
            "%m-%Y",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%m/%Y",
            "%d/%m/%Y",
        ]
        
        date = date.strip()
        
        
        if date.lower() in ['present', 'current', 'currently', 'now', 'ongoing']:
            formated_date =  datetime.now()
            logging.info(f"date formated to current date - {formated_date}")
            return formated_date
        
        for format in date_formats:
            try:
                formated_date = datetime.strptime(date, format)
                logging.info(f"date formated to matching format - {formated_date}")
                return formated_date
            except ValueError:
                continue
            
            
        return None
       
    except Exception as e:
        logging.info(f"Unable to format date: {date}")
        raise CustomException(e, sys)            
        
        
def calculate_experience(experience_data: str) -> int:
    """Extract dates from the data and calculate total months
    of experience"""
    
    try:
        
        date_pattern = r'''
    # Start date - multiple formats
    (
        [A-Z][a-z]+\.?\s+\d{4}         # January 2024 or Jan 2024
        |
        \d{1,2}/\d{1,2}/\d{4}          # 8/5/2025
        |
        \d{1,2}/\d{4}                  # 01/2014
    )
    \s*[-–—to]\s*                      # Separator: -, –, —, or space+"to"+space
    (
        [A-Z][a-z]+\.?\s+\d{4}         # March 2025
        |
        \d{1,2}/\d{1,2}/\d{4}          # 6/3/2026
        |
        \d{1,2}/\d{4}                  # 10/2016
        |
        (?:Present|Current|Currently|Now|Ongoing)
    )
'''
        
        date_pattern_compiled = re.compile(date_pattern, re.VERBOSE | re.IGNORECASE)
        matches = date_pattern_compiled.findall(experience_data)
        # print(matches)
        if matches:
            logging.info("Found and matched dates from experience section")
            total_exp = []
            
            for match in matches:
                start_date = match[0]
                # print(start_date)
                end_date = match[1]
                # print(end_date)
                logging.info("Start date - End date extracted")
                # if start_date in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"
                #                   "Jan", "Feb", "Mar", "Apr", "Aug", "Sept", "Oct", "Nov", "Dec"]:
                #     end_date_year = re.sub(r"\D","", end_date)
                #     start_date = re.sub(r"\d", "", start_date)
                #     start_date = " ".join([start_date, end_date_year])
                #     date1 = format_date(start_date)
                #     date2 = format_date(end_date)
                
                # else:    
                date1 = format_date(start_date)
                date2 = format_date(end_date)
                
                calculate_diff = relativedelta(date2, date1)
                total_months = calculate_diff.years * 12 + calculate_diff.months
                total_exp.append(total_months)
                total_months = sum(total_exp)
                logging.info("Calculated Total Experience of Candidate in Months")
        else:
            logging.info("Dint find any matched dates in experience section")
            return None    
        
        return total_months   
            
    except Exception as e:
        logging.info("Unable to calculate the experience")
        raise CustomException(e, sys)   
    
def parse_experience_from_resume(data: str) -> int:
    """Extract the experience section from the resume, calculate the
    total experience and return"""
    
    try:
        
        experience_headers = [
            r"^\s*[\d\.\-\W_]*\s*Experience\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Internships?\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Internships?\s+Experience\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Work\s+Experience\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Previous\s+Experience\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Professional\s+Experience\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Employment\s+(?:History|Background)\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*Career\s+(?:History|Summary)\s*[\d\.\-\W_]*$",
            # pattern change
            r"^\s*[\d\.\-\W_]*\s*Experience\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Internships?\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Internships?\s+Experience\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Work\s+Experience\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Previous\s+Experience\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Professional\s+Experience\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Employment\s+(?:History|Background)\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*Career\s+(?:History|Summary)\s*[\d\.\-\W_]*",
            # pattern change
            # r"^\s*[\d\.\-\W_]*\s*\bExperience\b\s*[\d\.\-\W_]*$",
            # r"^\s*[\d\.\-\W_]*\s*\bInternships\b?\s*[\d\.\-\W_]*$",
            # r"^\s*[\d\.\-\W_]*\s*\bInternships\b?\s+Experience\s*[\d\.\-\W_]*$",
            # r"^\s*[\d\.\-\W_]*\s*\bWork\s+Experience\b\s*[\d\.\-\W_]*$",
            # r"^\s*[\d\.\-\W_]*\s*\bPrevious\s+Experience\b\s*[\d\.\-\W_]*$",
            # r"^\s*[\d\.\-\W_]*\s*\bProfessional\s+Experience\b\s*[\d\.\-\W_]*$",
        ] 
        
        section_headers = [
            r"^\s*[\d\.\-\W_]*\s*(?:Education|Academic|Educational\s+History|Background)\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*(?:Projects|Personal|Academic|Significant\s+Projects)\s*[\d\.\-\W_]*$",
            r"^\s*[\d\.\-\W_]*\s*(?:Technical|Skills?|Professional|Soft\s+Skills|\bCoursework\b)\s*[\d\.\-\W_]*",
            r'^\s*[\d\.\-\W_]*\s*(?:Certifications?|Licenses?|\bCourses\b)\s*[\d\.\-\W_]*$',
            r'^\s*[\d\.\-\W_]*\s*(?:Awards?|Honors?|Achievements?)\s*[\d\.\-\W_]*$',
            r'^\s*[\d\.\-\W_]*\s*(?:Publications?|Research|Publications & Technical Writing)\s*[\d\.\-\W_]*$',
            r'^\s*[\d\.\-\W_]*\s*(?:Languages?|Language\s+Proficiency)\s*[\d\.\-\W_]*$',
            r'^\s*[\d\.\-\W_]*\s*(?:Competitions?|Interests?|Hobbies)\s*[\d\.\-\W_]*$',
            r'^\s*[\d\.\-\W_]*\s*(?:References?|Reference|Other\s+Available|Activities?)\s*[\d\.\-\W_]*$',
            # pattern change
            r"^\s*[\d\.\-\W_]*\s*(?:Education|Academic|Educational\s+History|Background)\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*(?:Projects|Personal|Academic|Significant\s+Projects)\s*[\d\.\-\W_]*",
            r"^\s*[\d\.\-\W_]*\s*(?:Technical|Skills?|Professional|Soft\s+Skills)\s*[\d\.\-\W_]*",
            r'^\s*[\d\.\-\W_]*\s*(?:Certifications?|Licenses?)\s*[\d\.\-\W_]*',
            r'^\s*[\d\.\-\W_]*\s*(?:Awards?|Honors?|Achievements?)\s*[\d\.\-\W_]*',
            r'^\s*[\d\.\-\W_]*\s*(?:Publications?|Research|Publications & Technical Writing)\s*[\d\.\-\W_]*',
            r'^\s*[\d\.\-\W_]*\s*(?:Languages?|Language\s+Proficiency)\s*[\d\.\-\W_]*',
            r'^\s*[\d\.\-\W_]*\s*(?:Competitions?|Interests?|Hobbies)\s*[\d\.\-\W_]*',
            r'^\s*[\d\.\-\W_]*\s*(?:References?|Reference|Other\s+Available|Activities?)\s*[\d\.\-\W_]*',
            ]
       
        
        experience_pattern = "|".join(experience_headers)
        section_pattern = "|".join(section_headers)   
        
        exp_matches = re.search(experience_pattern, data, re.IGNORECASE | re.MULTILINE)  
        # print(f"\n\nexp_matches: {exp_matches}\n\n")                       
        if not exp_matches:
            logging.info("Experience Section Not Found")
            return None
        
        logging.info("Experience Section Found")
        start_pos = exp_matches.end()
        
        section_matches = re.search(section_pattern, data[start_pos:], re.IGNORECASE | re.MULTILINE)
        # print(f"\nsection_matches: {section_matches}\n")
        if section_matches:
            end_pos = start_pos + section_matches.start()
            experience_text = data[start_pos:end_pos].strip() 
            logging.info("Experience Text Extracted and stopped at start of other section using section_matches")    
            
        
        else:
            experience_text = data[start_pos:].strip()   
            logging.info("Experience Text Extracted, till end of page")
            
        # print("\n\nexperince_text: ",experience_text)    
        total_months_exp = calculate_experience(experience_text)
        
        return total_months_exp
        
    except Exception as e:
        logging.info("Unable to Extract Experience Section and Calculate Months")
        raise CustomException(e, sys)     
  
def safe_json_loads(text: str) -> dict:
    """Extracts and parses the first valid json object from an LLM response"""
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    
    json_str = match.group(0)
    
    try:
        return json.loads(json_str)    
    except json.JSONDecodeError as e:
        raise ValueError("No JSON object found in LLM response")    
                
  
def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    try:
        a = np.array(a).flatten()  # (1, 384) → (384,)
        b = np.array(b).flatten()  # (1, 384) → (384,)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    except Exception as e:
        raise CustomException(e, sys)
