from fastapi import HTTPException, BackgroundTasks
import sys

from src.logger import logging
from src.exception import CustomException

from src.extraction_pipeline.data_extraction import Extract
from src.llm_pipeline.llm_semantic_parsing import (
    ParseResumeData,
    ParseJdData,
)
from src.llm_pipeline.data_validation_normalization import (
    ValidateResume,
    ValidateJd,
    NormalizeResume,
    NormalizeJd
)
from src.input_pipeline.jd_input import Jd_Parsing
from src.semantic_scoring.candidate_score import Candidate_Score
from src.semantic_scoring.candidate_fail_fast import Fail_Fast
from src.classify_candidates.classify import Classify

from src.db.supabase_operations import (
    CandidateOperations,
    JobOperations,
    ApplicationOperations
)

from src.services.email_service import EmailService
from src.llm_pipeline.llm_rate_limiting import GROQ_LIMITER
from src.storage.cloudflare_R2 import R2_Storage
from fastapi import UploadFile
import asyncio
import hashlib
import uuid
from datetime import datetime

LLM_SEMAPHORE = asyncio.Semaphore(5)

async def run_pipeline(
    resume_bytes: bytes, 
    jd_text: str,
    file_obj: UploadFile,
    background_tasks: BackgroundTasks
):

    try:
        
        start_time = datetime.now()
        
        resume_hash = hashlib.sha256(resume_bytes).hexdigest()
        logging.info("Hashed resume data")
        jd_hash = hashlib.sha256(jd_text.encode()).hexdigest()
        logging.info("Hashed jd data")
        
        existing_job = JobOperations.get_job_by_hash(jd_hash)
        existing_candidate = CandidateOperations.get_candidate_by_hash(resume_hash)
        
        needs_jd_parsing = not existing_job
        needs_resume_parsing = not existing_candidate
        
        if needs_jd_parsing and needs_resume_parsing:
            
            job_id = str(uuid.uuid4())
            logging.info(f"New Job_Id: {job_id} created")
            candidate_id = str(uuid.uuid4())
            application_id = str(uuid.uuid4())
            
            logging.info(f" New Candidate ID: {candidate_id} created")
            logging.info(f" New Application ID: {application_id} created")
            
            jd_obj = Jd_Parsing(data=jd_text)
            jd_raw = jd_obj.jd_data()
            llm_jd = ParseJdData(data=jd_raw)
            
            extract_obj = Extract(file_bytes=resume_bytes)
            resume_text = extract_obj.extract_text()
            llm_resume = ParseResumeData(data=resume_text)
            
            logging.info("Running CONCURRENT JD + Resume parsing")
            
            await GROQ_LIMITER.acquire()
            await GROQ_LIMITER.acquire()
                
            async with LLM_SEMAPHORE:
                jd_llm_output, resume_llm_output = await asyncio.gather(
                    asyncio.to_thread(llm_jd.llm_jd_parser),
                    asyncio.to_thread(llm_resume.llm_resume_parser)
                )
            logging.info("Concurrently parsed JD & Resume")
            
            validatedJd_output = ValidateJd(data=jd_llm_output).data
            normalized_jd = NormalizeJd(data=validatedJd_output).removejd_duplicates()
            
            JobOperations.create_job(
                job_id=job_id,
                jd_data=normalized_jd.model_dump(),
                jd_text=jd_text,
                jd_hash=jd_hash
            )    
            
            validated_output = ValidateResume(data=resume_llm_output).data
            normalized_resume = NormalizeResume(data=validated_output).remove_duplicates()
            
            r2_storage = R2_Storage()
            resume_r2_path = r2_storage.upload_resume_to_r2(
            file_obj=file_obj,
            filename=file_obj.filename,
            candidate_id=candidate_id,
            application_id=application_id
            )
            
            CandidateOperations.create_candidate(
                candidate_id=candidate_id,
                resume_data=normalized_resume.model_dump(),
                resume_hash=resume_hash,
                resume_filename=file_obj.filename,
                resume_r2_path=resume_r2_path
            )
    
    
        elif needs_jd_parsing and not needs_resume_parsing:
            
            candidate_id = existing_candidate['id']
            resume_r2_path = existing_candidate['resume_r2_path']
            application_id = str(uuid.uuid4())    
            normalized_resume = ValidateResume(data=existing_candidate['full_parsed_data']).data
            
            job_id = str(uuid.uuid4())
            logging.info(f"New Job_Id: {job_id} created")
            
            jd_obj = Jd_Parsing(data=jd_text)
            jd_raw = jd_obj.jd_data()
            llm_jd = ParseJdData(data=jd_raw)
            
            await GROQ_LIMITER.acquire()

            async with LLM_SEMAPHORE:
                jd_llm_output = await asyncio.to_thread(llm_jd.llm_jd_parser)
                
            validatedJd_output = ValidateJd(data=jd_llm_output).data
            normalized_jd = NormalizeJd(data=validatedJd_output).removejd_duplicates()
            
            JobOperations.create_job(
                job_id=job_id,
                jd_data=normalized_jd.model_dump(),
                jd_text=jd_text,
                jd_hash=jd_hash
            )    
            
        
        elif not needs_jd_parsing and needs_resume_parsing:
            
            job_id = existing_job['id']
            logging.info(f"Reusing existing job: {job_id}")
            
            normalized_jd = ValidateJd(data={
                "job_title": existing_job["job_title"],
                "required_skills": existing_job["required_skills"],
                "preferred_skills": existing_job["preferred_skills"],
                "min_experience_months": existing_job["min_experience_months"],
                "required_education": existing_job["required_education"],
                "keywords": existing_job["keywords"]
            }).data
            
            candidate_id = str(uuid.uuid4())
            application_id = str(uuid.uuid4())
            
            logging.info(f" New Candidate ID: {candidate_id} created")
            logging.info(f" New Application ID: {application_id} created")
          
            extract_obj = Extract(file_bytes=resume_bytes)
            resume_text = extract_obj.extract_text()
            llm_resume = ParseResumeData(data=resume_text)
            
            await GROQ_LIMITER.acquire()

            async with LLM_SEMAPHORE:
                resume_llm_output = await asyncio.to_thread(llm_resume.llm_resume_parser)
                
            validated_output = ValidateResume(data=resume_llm_output).data
            normalized_resume = NormalizeResume(data=validated_output).remove_duplicates()
            
            r2_storage = R2_Storage()
            resume_r2_path = r2_storage.upload_resume_to_r2(
            file_obj=file_obj,
            filename=file_obj.filename,
            candidate_id=candidate_id,
            application_id=application_id
            )
            
            CandidateOperations.create_candidate(
                candidate_id=candidate_id,
                resume_data=normalized_resume.model_dump(),
                resume_hash=resume_hash,
                resume_filename=file_obj.filename,
                resume_r2_path=resume_r2_path
            )
            
        else:
            logging.info(" Both JD and Resume cached")
            
            job_id = existing_job['id']
            normalized_jd = ValidateJd(data={
                "job_title": existing_job["job_title"],
                "required_skills": existing_job["required_skills"],
                "preferred_skills": existing_job["preferred_skills"],
                "min_experience_months": existing_job["min_experience_months"],
                "required_education": existing_job["required_education"],
                "keywords": existing_job["keywords"]
            }).data
            
            candidate_id = existing_candidate['id']
            resume_r2_path = existing_candidate['resume_r2_path']
            normalized_resume = ValidateResume(data=existing_candidate['full_parsed_data']).data
            
            # Check for duplicate application
            duplicate_application = ApplicationOperations.check_duplicate_application(
                candidate_id, job_id
            )
            
            if duplicate_application:
                logging.info(f"Duplicate application found: {duplicate_application}")
                return {
                    "status": "duplicate",
                    "message": "This candidate has already applied to this job",
                    "application_id": duplicate_application['id'],
                    "job_id": job_id,
                    "candidate_id": candidate_id,
                    "previous_score": float(duplicate_application['total_score']) if duplicate_application['total_score'] else None,
                    "classification": duplicate_application['classification']
                }
            
            application_id = str(uuid.uuid4())
    

        scorer = Candidate_Score(resume_data=normalized_resume, jd_data=normalized_jd)
        current_points = scorer.education_score()
        
        fail_fast = Fail_Fast(current_points=current_points)
        rejection = fail_fast.hard_fail_candidate()
        
        processing_duration = (datetime.now()-start_time).total_seconds()
        
        if rejection is not None:
            
            ApplicationOperations.create_application(
                application_id=application_id,
                candidate_id=candidate_id,
                job_id=job_id,
                total_score=rejection.get("details", {}).get("candidate_score", 0.0),
                score_breakdown=current_points,
                resume_r2_path=resume_r2_path,
                classification=rejection.get('classification', "unknown"),
                processing_duration=round(processing_duration, 2)
            )
            
            return {
                **rejection,
                "application_id": application_id,
                "candidate_id": candidate_id,
                "job_id": job_id,
                "resume_r2_path": resume_r2_path,
                "classification": rejection.get('classification', "unknown")
            }
                                                            
        current_points, total_points = scorer.candidate_total_score(points=current_points)

        # 6 Classification
        classifier = Classify(current_points=current_points, total_points=total_points)
        result = classifier.classified_candidate()
        
        processing_duration = (datetime.now()-start_time).total_seconds()
        
        ApplicationOperations.create_application(
                application_id=application_id,
                candidate_id=candidate_id,
                job_id=job_id,
                total_score=result.get('final_score', 0.0),
                score_breakdown=result.get('details', {}),
                resume_r2_path=resume_r2_path,
                classification=result.get("classification", "unknown"),
                processing_duration=round(processing_duration, 2)
            )
        
        
        if EmailService.should_notify(float(result.get('final_score') or 0.0)): # why is it giving str value
            background_tasks.add_task(
                EmailService.notify_high_score,
                candidate_info={
                    "name": normalized_resume.name,
                    "email": normalized_resume.emails[0] if normalized_resume.emails else None,
                    "phone": normalized_resume.phone_numbers[0] if normalized_resume.phone_numbers else None
                },
                application_data={
                    "application_id": application_id,
                    "total_score": result.get('final_score', 0.0),
                    "classification": result.get('classification')
                },
                job_info={
                    "job_id": job_id,
                    "job_title": normalized_jd.job_title
                }
            )
            
            logging.info(f" Email notification queued for high-scoring candidate (score: {result.get('final_score', 0.0)})")
        
        return {
            **result,
            "application_id": application_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "resume_r2_path": resume_r2_path,
            "candidate_info": {
                "name": normalized_resume.name,
                "email": normalized_resume.emails[0] if normalized_resume.emails else None,
                "phone": normalized_resume.phone_numbers[0] if normalized_resume.phone_numbers else None,
            },
            "metadata": {
                "processing_duration_seconds": processing_duration,
                "resume_hash": resume_hash[:16] + "...",
                "jd_hash": jd_hash[:16] + "...",
                "original_filename": file_obj.filename
            },
            "status": "processed"
        }
    
    except HTTPException:
        raise 
     
    except Exception as e:
        logging.error("Pipeline failed")
        raise CustomException(e, sys)
    