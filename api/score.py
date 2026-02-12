from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from src.core.pipeline import run_pipeline
from src.logger import logging
from src.utils import check_file_extension, check_file_size

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("/resume")
async def score_uploaded_resume(
    resume: UploadFile = File(...),
    jd_text: str = Form(...)   
):
    
    try:
        check_file_extension(resume.filename)
        check_file_size(resume.size)

        resume_bytes = await resume.read() 
        logging.info("Read bytes from resume file")
        result = await run_pipeline(
            resume_bytes=resume_bytes,
            jd_text=jd_text
        )
        
        return result
    except HTTPException:
        raise
   
    
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during processing")

