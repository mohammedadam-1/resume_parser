import sys 
from src.exception import CustomException 
from src.logger import logging 
from models.schemas import ClassificationResult, CurrentPoints, ScoreBreakdown
from pydantic import BaseModel, Field

class Fail_Fast(BaseModel):
    current_points: CurrentPoints
    minimum_education_points: float = 3.0
    minimum_required_skills_points: float = 10.0
        
    def hard_fail_candidate(self):
        """
        Returns:
        - None if candidate passes hard-fail checks
        - dict rejection report if candidate fails
        """
        try:
            candidate_required_skills_score = self.current_points.required_skills
            candidate_education_score = self.current_points.education_required

            if candidate_required_skills_score < self.minimum_required_skills_points:
                return self.rejected_candidate_report(
                    failed_gate="required_skills",
                    candidate_score=candidate_required_skills_score,
                    minimum_points=self.minimum_required_skills_points
                )

            if candidate_education_score < self.minimum_education_points:
                return self.rejected_candidate_report(
                    failed_gate="education",
                    candidate_score=candidate_education_score,
                    minimum_points=self.minimum_education_points
                )

            logging.info("Candidate passed hard-fail checks")
            return None

        except Exception as e:
            logging.info("Issue in hard_fail_candidate func")
            raise CustomException(e, sys)
  
        
    def rejected_candidate_report(self, failed_gate:str, candidate_score:float, minimum_points:float):
        """Details of rejected candidate"""    

        try:
            logging.info("Candidate Rejected - Return candidate report")
            return {
                "status": "rejected",
                "hard_fail": True,
                "failed_gate": failed_gate,
                "details": {
                    "candidate_score": candidate_score,
                    "minimum_required": minimum_points} 
            }
        
        except Exception as e:
            logging.info("Unable to report the rejected candidate") 
            raise CustomException(e, sys) 
        

        
            