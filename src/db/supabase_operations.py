from src.db.supabase_client import supabase
from src.logger import logging
from src.exception import CustomException
import sys
from datetime import datetime

class CandidateOperations:
    
    @staticmethod
    def create_candidate(
        candidate_id: str,
        resume_data: dict,
        resume_hash: str,
        resume_filename: str,
        resume_r2_path: str
    )-> dict:
        
        """Create new candidate with explicit UUID."""
        
        try:
            logging.info("Initialized to create candidate in DB")
            candidate = {
                "id": candidate_id,
                "name": resume_data.get("name", "unknown"),
                "email": resume_data.get("emails", [None])[0],
                "phone": resume_data.get("phone_numbers", [None])[0],
                "resume_file_name": resume_filename,
                "resume_hash": resume_hash,
                "resume_r2_path": resume_r2_path,
                "full_parsed_data": resume_data
            }
            
            response = supabase.table("candidates").insert(candidate).execute()
            
            if response.data:
                logging.info(f"Created candidate in DB: {candidate_id}")
                
                return response.data[0]
            
            
        except Exception as e:
            logging.info("Failed to create candidate in db")
            raise CustomException(e, sys) 
        
        
    @staticmethod
    def get_candidate_by_hash(resume_hash:str) -> dict | None:
        """Check if resume hash already exists"""
        
        try:
            
            response = supabase.table("candidates")\
                .select("*")\
                .eq("resume_hash", resume_hash)\
                .limit(1)\
                .execute()              
                
            if response.data:
                logging.info("Found existing candidate with hash") 
                    
                return response.data[0]
        
            return None
    
        except Exception as e:
            logging.info("Error while fetching candidate resume hash")
            raise CustomException(e, sys)

class ApplicationOperations:
            
    @staticmethod    
    def create_application(
        application_id: str,
        candidate_id: str,
        job_id: str,
        total_score: float,
        score_breakdown: dict,
        resume_r2_path: str,
        classification: str,
        processing_duration: float
    ) -> dict:
        """Create new application with explicit UUID."""
        
        try:
            logging.info("Initialized to create application in db")
            application = {
                "id": application_id,  # Explicit UUID
                "candidate_id": candidate_id,
                "job_id": job_id,
                "total_score": total_score,
                "score_breakdown": score_breakdown,
                "classification": classification,
                "status": 'processed' if classification != 'Not a fit' else 'rejected',
                "submitted_at": datetime.now().isoformat(),
                "processing_duration_seconds": processing_duration,
                "resume_r2_path": resume_r2_path
            }
            
            
            response = supabase.table("applications").insert(application).execute()
            
            if response.data:
                logging.info(f"Created application in db: {application_id}")
                
                return response.data[0]
            
            
        except Exception as e:
            logging.info("Failed to create application in db")
            raise CustomException(e, sys)    
        
    @staticmethod    
    def check_duplicate_application(candidate_id: str, job_id: str) -> dict | None:
        """Check if candidate has already applied to this job."""
        
        try:
            
            response = supabase.table("applications")\
                .select('*')\
                .eq("candidate_id", candidate_id)\
                .eq("job_id", job_id)\
                .limit(1)\
                .execute()
                
            if response.data:
                logging.info(f"Application already exists")
                return response.data[0]
            
            return None
        
        except Exception as e:
            logging.info("Error while checking for duplicate application")
            raise CustomException(e, sys)
        
class JobOperations:
        
    @staticmethod
    def create_job(
        job_id: str,
        jd_data: dict,
        jd_text: str,
        jd_hash: str
    ) -> dict:
        
        """Create new job with explicit UUID."""
        
        try:
        
            job = {
                "id": job_id,
                "job_title": jd_data.get("job_title", "unknown"),
                "required_skills": jd_data.get("required_skills", []),
                "preferred_skills": jd_data.get("preferred_skills", []),
                "min_experience_months": jd_data.get("min_experience_months", ""),
                "required_education": jd_data.get("required_education", {}),
                "keywords": jd_data.get("keywords", []),
                "jd_text": jd_text,
                "jd_hash": jd_hash,
                "status": "active"

            }
            
            response = supabase.table("job_postings").insert(job).execute()
            
            if response.data:
                logging.info(f"Created JD in db: {job_id}")
                
                return response.data[0]
            
        except Exception as e:
            logging.info("Failed to create JD in db")
            raise CustomException(e, sys)
    
    @staticmethod
    def get_job_by_hash(jd_hash) -> dict|None :
        """Check if the JD hash already exists"""
        
        try:
            
            response = supabase.table("job_postings")\
                .select('*')\
                .eq("jd_hash", jd_hash)\
                .limit(1)\
                .execute()
                
            if response.data:
                logging.info("Found existing JD")
                return response.data[0]
            
            return None    
            
        except Exception as e:
            logging.info("Error while fetching Jd hash")     
            raise CustomException(e, sys)
        
        
        
        
            
            