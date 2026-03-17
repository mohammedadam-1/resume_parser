import sys 
import os
from src.exception import CustomException
from src.logger import logging
from typing import Literal
from models.schemas import CurrentPoints, ScoreBreakdown, ClassificationResult
from pydantic import BaseModel


class Classify(BaseModel):
    current_points: CurrentPoints
    total_points: float
    candidate_classification: str | None = None
    
    required_skills_score: float = 0.0
    preferred_skills_score: float = 0.0
    experience_score: float = 0.0
    education_score: float = 0.0
    keywords_score: float = 0.0
    
    def model_post_init(self, _):
        self.required_skills_score = self.current_points.required_skills
        self.preferred_skills_score = self.current_points.preferred_skills
        self.experience_score = self.current_points.min_experience_months
        self.education_score = self.current_points.education_required
        self.keywords_score = self.current_points.keywords
    
        
    def classify_candidate(self) -> Literal[
        "Strong Fit",
        "Good Fit",
        "Potential Fit",
        "Not Fit"
    ]:
        """Compare score and classify candidates"""   
        
        try:        
            logging.info("Initialized classification of candidate")
            if self.total_points >= 80.0:
                self.candidate_classification = "Strong Fit"
                logging.info("Classified candidate as 'Strong Fit'")
                
            elif self.total_points >= 65.0:
                self.candidate_classification = "Good Fit"
                logging.info("Classified candidate as 'Good Fit'")
                
            elif self.total_points >= 50.0:
                self.candidate_classification = "Potential Fit"
                logging.info("Classified candidate as 'Potential Fit'")
                
            else:
                self.candidate_classification = "Not Fit"    
                logging.info("Classified candidate as 'Not Fit'")
             
            logging.info("Returned classified category and total points")    
            return self.candidate_classification   
                    
        except Exception as e:
            logging.info("Unable to compare score and classify candidate")
            raise CustomException(e, sys) 
        
    def classified_candidate(self) -> dict:
        """Route candidate - Returns dict instead of ClassificationResult"""
        
        try:
            classified_candidate = self.classify_candidate()
            
            if classified_candidate == "Strong Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                os.makedirs("Classified_Candidates/Passed", exist_ok=True)
                
                with open("Classified_Candidates/Passed/strongFit_candidates.txt", "a") as f:
                    f.write(candidate_details + "\n")
                logging.info("logged passed candidate details in 'StrongFit_candidates.txt'")
                
                return self.candidate_report_as_dict(self.total_points, classified_candidate)
                 
            elif classified_candidate == "Good Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                os.makedirs("Classified_Candidates/Passed", exist_ok=True)
                
                with open("Classified_Candidates/Passed/goodFit_candidates.txt", "a") as f:
                    f.write(candidate_details + "\n")
                logging.info("logged passed candidate details in 'goodFit_candidates.txt'")  
                
                return self.candidate_report_as_dict(self.total_points, classified_candidate)
                
            elif classified_candidate == "Potential Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                os.makedirs("Classified_Candidates/Passed", exist_ok=True)
                
                with open("Classified_Candidates/Passed/potentialFit_candidates.txt", "a") as f:
                    f.write(candidate_details + "\n")
                logging.info("logged passed candidate details in 'potentialFit_candidates.txt'")  
                
                return self.candidate_report_as_dict(self.total_points, classified_candidate)
                
            else:
                classified_candidate = "Not Fit"  
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()

                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                os.makedirs("Classified_Candidates/Failed", exist_ok=True)
                
                with open("Classified_Candidates/Failed/NotFit_candidates.txt", "a") as f:
                    f.write(candidate_details + "\n")
                logging.info("logged passed candidate details in 'NotFit_candidates.txt'")       
                
                return self.candidate_report_as_dict(self.total_points, classified_candidate)

        except Exception as e:
            logging.info("Unable to write candidate report in file")
            raise CustomException(e, sys)   
        
    def candidate_report(self, total_points, classification) -> ClassificationResult:
        """Create ClassificationResult for file logging"""
        try:
            logging.info("Create and return candidate's final report")
            return ClassificationResult(
                final_score = total_points,
                classification = classification,
                details = ScoreBreakdown(
                    required_skills = self.required_skills_score,
                    preferred_skills = self.preferred_skills_score,
                    experience = self.experience_score,
                    education = self.education_score,
                    keywords = self.keywords_score
                )
            )
    
        except Exception as e:
            logging.info("Unable to create candidate's final report")
            raise CustomException(e, sys)
    
    def candidate_report_as_dict(self, total_points, classification) -> dict:
        """
        Create dict response for API with hard_fail=False
        This matches the frontend's expected format
        """
        try:
            logging.info("Creating API response dict with hard_fail=False")
            return {
                "hard_fail": False,  
                "classification": classification,
                "final_score": f"{total_points:.1f}",  # Format as string
                "details": {
                    "required_skills": f"{self.required_skills_score:.1f}",
                    "preferred_skills": f"{self.preferred_skills_score:.1f}",
                    "experience": f"{self.experience_score:.1f}",
                    "education": f"{self.education_score:.1f}",
                    "keywords": f"{self.keywords_score:.1f}"
                }
            }
        except Exception as e:
            logging.info("Unable to create API response dict")
            raise CustomException(e, sys)