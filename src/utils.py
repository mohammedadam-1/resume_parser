import os 
import sys 
from pathlib import Path
from src.exception import CustomException
from src.logger import logging
import pymupdf
import re 
from datetime import datetime 
from dateutil.relativedelta import relativedelta
import pdfplumber 



def check_file_extension(file_path):
    try:
            
        filepath = Path(file_path)
        logging.info("file path loaded successfully")
        if filepath.suffix.lower() == ".pdf":
            return file_path
        elif filepath.suffix.lower() == ".docx":
            return file_path
        elif filepath.suffix.lower() == ".txt":
            return file_path
        else:
            logging.info('Invalid file: Upload valid filetype')
            print(f"invalid filetype. only accepted pdf, docx, txt filetype")
            
    except Exception as e:
        raise CustomException(e, sys)
    
    
def check_file_size(file_path):
    try:
        
        file_size = Path(file_path).stat().st_size
        file_size = bytes(file_size)
        min_file_size = b'\x00' * 100 * 10
        max_file_size = 5 * 1024 * 1024
        max_file_size = bytes(max_file_size)
        if file_size >= min_file_size and file_size <= max_file_size:
            logging.info('valid file size')
            return file_path    
        
        else:
            logging.info('invalid file size')
            print(f"invalid file size: {file_size}. Please upload file greater than 100bytes and less than 100Mb size")
        
    except Exception as e:
        raise CustomException(e, sys)    
    
    
def route_filetype(file_path):
    """route to specific file extension extractor"""   
    
    try:
        
        filepath = Path(file_path)
        full_text = []

        if filepath.suffix.lower() == '.pdf':
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages: # Use .pages for clarity
                    page_text = page.extract_text() # .extract_text() is the standard method
                    if page_text:
                        full_text.append(page_text)
        
        # Join pages and clean up extra newlines/spaces
        cleaned_text = "\n".join(full_text).strip()
        return cleaned_text  
            
    except Exception as e:
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
        
        
def score_points():
    
    try:
        points = {
            "required_skills": 0,
            "preferred_skills": 0,
            "min_experience_months":0,
            "education_required":0,
            "keywords":0
        }      

        return points  
    
    except Exception as e:
        raise CustomException(e, sys)  
    
def format_date(date):
    """format date and return"""
    
    try:
        date_formats = [
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
            logging.info("date formated to current date")
            return formated_date
        
        for format in date_formats:
            try:
                formated_date = datetime.strptime(date, format)
                logging.info("date formated to matching format")
                return formated_date
            except ValueError:
                continue
            
        return None
       
    except Exception as e:
        logging.info(f"Unable to format date: {date}")
        raise CustomException(e, sys)            
        
        
def calculate_experience(experience_data):
    """Extract dates from the data and calculate total months
    of experience"""
    
    try:
        
        date_pattern = r'''
    # Start date - multiple formats
    (
        [A-Z][a-z]+\.?\s+\d{4}         # Jan 2014, January 2014
        |
        \d{1,2}/\d{1,2}/\d{4}          # 8/5/2025, 08/05/2025
        |
        \d{1,2}/\d{4}                  # 01/2014
    )
    \s*[-–—to]\s*                      # Separator: -, –, —, or "to"
    # End date - same formats OR keywords
    (
        [A-Z][a-z]+\.?\s+\d{4}         # Oct 2016
        |
        \d{1,2}/\d{1,2}/\d{4}          # 6/3/2026
        |
        \d{1,2}/\d{4}                  # 10/2016
        |
        (?:Present|Current|Currently|Now|Ongoing)  # Keywords
        )'''
        
        date_pattern_compiled = re.compile(date_pattern, re.VERBOSE | re.IGNORECASE)
        matches = date_pattern_compiled.findall(experience_data)
        if matches:
            logging.info("Found and matched dates from experience section")
            total_exp = []
            for match in matches:
                start_date = match[0]
                end_date = match[1]
                
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
    
def parse_experience_from_resume(data):
    """Extract the resume section from the resume and return"""
    
    try:
        
        experience_headers = [
            r"^\s*Experience\s*$",
            r"^\s*Internships?\s*$",
            r"^\s*Internships?\s+Experience\s*$",
            r"^\s*Work\s+Experience\s*$",
            r"^\s*Previous\s+Experience\s*$",
            r"^\s*Professional\s+Experience\s*$",
            r"^\s*Employment\s+(?:History|Background)\s*$",
            r"^\s*Career\s+(?:History|Summary)\s*$"
        ] 
        
        section_headers = [
            r"^\s*(?:Education|Academic|Educational\s+History|Background|)\s*$",
            r"^\s*(?:Projects|Personal|Academic\s+Projects)\s*$",
            r"^\s*(?:Technical|Skills?|Professional|Soft\s+Skills)\s*$",
            r'^\s*(?:Certifications?|Licenses?|Courses?)\s*$',
            r'^\s*(?:Awards?|Honors?|Achievements?)\s*$',
            r'^\s*(?:Publications?|Research|Publications & Technical Writing)\s*$',
            r'^\s*(?:Languages?|Language\s+Proficiency)\s*$',
            r'^\s*(?:Competitions?|Interests?|Hobbies)\s*$',
            r'^\s*(?:References?|Reference|Other\s+Available|Activities?)\s*$',
            ]
        
        experience_pattern = "|".join(experience_headers)
        section_pattern = "|".join(section_headers)
        
        exp_matches = re.search(experience_pattern, data, re.IGNORECASE | re.MULTILINE)
        print("")
        if not exp_matches:
            logging.info("Experience Section Not Found")
            return None
        
        logging.info("Experience Section Found")
        start_pos = exp_matches.end()
        
        section_matches = re.search(section_pattern, data[start_pos:], re.IGNORECASE | re.MULTILINE)
        
        if section_matches:
            end_pos = start_pos + section_matches.start()
            experience_text = data[start_pos:end_pos].strip() 
            logging.info("Experience Text Extracted and stopped at start of other section")
        else:
            experience_text = data[start_pos:].strip()   
            logging.info("Experience Text Extracted, till end of page")
        print("\n\nExperience Text",experience_text)
        total_months_exp = calculate_experience(experience_text)
        print(total_months_exp)
        
    except Exception as e:
        logging.info("Unable to Extract Experience Section and Calculate Months")
        raise CustomException(e, sys)          
                
  

