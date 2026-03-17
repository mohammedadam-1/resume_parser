import sys 
import os
from src.exception import CustomException 
from src.logger import logging 
from models.schemas import CurrentPoints
from pydantic import BaseModel
import json

class Fail_Fast(BaseModel):
    current_points: CurrentPoints
    minimum_education_points: float = 3.0
    minimum_required_skills_points: float = 15.0
        
    def hard_fail_candidate(self):
        """
        Returns:
        - None if candidate passes hard-fail checks
        - dict rejection report if candidate fails
        """
        try:
            logging.info("Initialized hard fail candidate method")
            candidate_required_skills_score = self.current_points.required_skills
            candidate_education_score = self.current_points.education_required
            logging.info("Loaded current_points of candidate's required_skills and education")

            if candidate_required_skills_score < self.minimum_required_skills_points:
                logging.info(f"Candidate failed at required_skills gate: {candidate_required_skills_score}")
                report = self.rejected_candidate_report(
                    failed_gate="required_skills",
                    candidate_score=candidate_required_skills_score,
                    minimum_points=self.minimum_required_skills_points
                )
                str_report = json.dumps(report)
                
                os.makedirs("Classified_Candidates/Failed", exist_ok=True)
                
                with open("Classified_Candidates/Failed/hard_fail.txt", "a") as f:
                    f.write(str_report + "\n")
                logging.info("logged failed candidate details in 'hard_fail.txt'")
                    
                return self.rejected_candidate_report(
                    failed_gate="required_skills",
                    candidate_score=candidate_required_skills_score,
                    minimum_points=self.minimum_required_skills_points
                )    

            if candidate_education_score < self.minimum_education_points:
                logging.info(f"Candidate failed at education gate: {candidate_education_score}")
                
                report = self.rejected_candidate_report(
                    failed_gate="education",
                    candidate_score=candidate_education_score,
                    minimum_points=self.minimum_education_points
                )
                str_report = json.dumps(report)
                
                os.makedirs("Classified_Candidates/Failed", exist_ok=True)
                
                with open("Classified_Candidates/Failed/hard_fail.txt", "a") as f:
                    f.write(str_report + "\n")
                logging.info("logged failed candidate details in 'hard_fail.txt'")
                
                return self.rejected_candidate_report(
                    failed_gate="education",
                    candidate_score=candidate_education_score,
                    minimum_points=self.minimum_education_points
                )

            logging.info("Candidate passed hard-fail checks")
            return None

        except Exception as e:
            logging.info("Issue in hard_fail_candidate method")
            raise CustomException(e, sys)
  
        
    def rejected_candidate_report(self, failed_gate:str, candidate_score:float, minimum_points:float):
        """Details of rejected candidate"""    

        try:
            logging.info("Return candidate report")
            return {
                "classification": f"rejected for {failed_gate}",
                "hard_fail": True,
                "failed_gate": failed_gate,
                "details": {
                    "candidate_score": candidate_score,
                    "minimum_required": minimum_points} 
            }
        
        except Exception as e:
            logging.info("Unable to report the rejected candidate") 
            raise CustomException(e, sys) 
        

        
            