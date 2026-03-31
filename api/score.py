from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, BackgroundTasks, Request, Depends
from src.core.pipeline import run_pipeline
from src.logger import logging
from src.utils import check_file_extension, check_file_size
from src.db.dependencies import get_current_user
import time
from main import limiter
router = APIRouter(prefix="/score", tags=["Scoring"])

@router.post("/resume")
@limiter.limit("3/minute")
async def score_uploaded_resume(
    request: Request,
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
    user=Depends(get_current_user)      # jwt
):
    try:
        check_file_extension(resume.filename)
        check_file_size(resume.size)
    
        resume_bytes = await resume.read() 
        logging.info(f"Read bytes from resume file for user: {user.user.id}")   # <-- logging user
        
        await resume.seek(0)
        
        start_time = time.perf_counter()
        result = await run_pipeline(
            resume_bytes=resume_bytes,
            jd_text=jd_text,
            file_obj=resume,
            background_tasks=background_tasks
        )
        
        end_time = time.perf_counter()
        logging.info(f"Pipeline executed in {end_time - start_time:.4f} seconds")
        
        return result
    
    except HTTPException:
        raise
    
    except Exception as e:
        logging.error(f"Pipeline failed for user {user.user.id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during processing")