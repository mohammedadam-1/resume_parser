from fastapi import APIRouter, UploadFile, File, HTTPException, status
from src.core.pipeline import run_pipeline
from models.schemas import ClassificationResult
from src.logger import logging
from src.utils import check_file_extension, check_file_size

router = APIRouter(prefix="/score", tags=["Scoring"])


@router.post("/resume")
async def score_uploaded_resume(
    resume: UploadFile = File(...),
    jd_text: str = ""   # optional for now
):
    
    try:
        check_file_extension(resume.filename)
        check_file_size(resume.size)

        resume_bytes = await resume.read() 
        logging.info("Read bytes from resume file")
        result = run_pipeline(
            resume_bytes=resume_bytes,
            jd_text=jd_text
        )
        
        return result
    except HTTPException:
        raise
   
    
    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during processing")

