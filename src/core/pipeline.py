import shutil
import tempfile
from fastapi import HTTPException
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
import asyncio


async def run_pipeline(resume_bytes: bytes, jd_text: str):
    temp_dir = None

    try:
        temp_dir = tempfile.mkdtemp()
        resume_path = f"{temp_dir}/resume.pdf"  # OK for now

        # 1️ WRITE FILE FIRST
        with open(resume_path, "wb") as f:
            f.write(resume_bytes)

        # 2 Resume extraction
        extract_obj = Extract(file_path=resume_path)
        resume_text = extract_obj.extract_text()
        
        jd_obj = Jd_Parsing(data=jd_text)
        jd_raw = jd_obj.jd_data()  
        # 3 Resume LLM parsing
        llm_resume = ParseResumeData(data=resume_text)
        llm_jd = ParseJdData(data=jd_raw)
        
        resume_llm_output, jd_llm_output = await asyncio.gather(
            asyncio.to_thread(llm_resume.llm_resume_parser),
            asyncio.to_thread(llm_jd.llm_jd_parser)
        )

        validated_output = ValidateResume(data=resume_llm_output).data
        normalized_resume = NormalizeResume(data=validated_output).remove_duplicates()

        # 4 JD parsing
        
        validatedJd_output = ValidateJd(data=jd_llm_output).data
        normalized_jd = NormalizeJd(data=validatedJd_output).removejd_duplicates()

        # 5 Scoring + hard-fail
        scorer = Candidate_Score(resume_data=normalized_resume, jd_data=normalized_jd)
        current_points = scorer.education_score()
        
        fail_fast = Fail_Fast(current_points=current_points)
        rejection = fail_fast.hard_fail_candidate()
        if rejection is not None:
            return rejection
                                                            
        current_points, total_points = scorer.candidate_total_score(points=current_points)

        # 6 Classification
        classifier = Classify(current_points=current_points, total_points=total_points)
        result = classifier.classified_candidate()

        return result
    
    except HTTPException:
        raise 
     
    except Exception as e:
        logging.error("Pipeline failed")
        raise CustomException(e, sys)

    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)
