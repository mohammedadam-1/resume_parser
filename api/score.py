from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks, Request
from src.core.pipeline import run_pipeline
from src.logger import logging
from src.utils import check_file_extension, check_file_size
import time
from slowapi import Limiter
from slowapi.util import get_remote_address


router = APIRouter(prefix="/score", tags=["Scoring"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/resume")
@limiter.limit("3/minute")  # Max 5 uploads per minute per IP
async def score_uploaded_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    jd_text: str = Form(...)   
):
    
    try:
        check_file_extension(resume.filename)
        check_file_size(resume.size)
    
        resume_bytes = await resume.read() 
        logging.info("Read bytes from resume file")
        
        await resume.seek(0)
        
        start_time = time.perf_counter()
        result = await run_pipeline(
            resume_bytes=resume_bytes,
            jd_text=jd_text,
            file_obj=resume,
            background_tasks=background_tasks
        )
        
        end_time = time.perf_counter()
        scoring_execution_time = end_time - start_time
        
        logging.info(f"Pipeline executed in {scoring_execution_time:.4f} seconds")
    
        
        return result
    
    except HTTPException:
        raise
   
    
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during processing")

