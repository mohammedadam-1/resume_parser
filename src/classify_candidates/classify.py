import sys 
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
        "Not a Fit"
    ]:
        """Compare score and classify candidates"""   
        
        try:        
            
            if self.total_points >= 80.0:
                self.candidate_classification = "Strong Fit"
                logging.info("Classified candidate as 'Strong Fit'")
                
            elif 65.0 <= self.total_points <= 79.0:
                self.candidate_classification = "Good Fit"
                logging.info("Classified candidate as 'Good Fit'")
                
            elif 50.0 <= self.total_points <=64.0:
                self.candidate_classification = "Potential Fit"
                logging.info("Classified candidate as 'Potential Fit'")
                
            else:
                self.candidate_classification = "Not a Fit"    
                logging.info("Classified candidate as 'Not a Fit'")
             
            logging.info("Returning classified str and total points")    
            return self.candidate_classification   
                    
        except Exception as e:
            logging.info("Unable to compare score and classify candidate")
            raise CustomException(e, sys) 
        
    def classified_candidate(self) -> ClassificationResult:
        """Route candidate"""
        
        try:
            classified_candidate = self.classify_candidate()
            
            print(f"classified_candidate as: {classified_candidate} [points scored: {self.total_points}]")
            
            if classified_candidate == "Strong Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                with open("Classified_Candidates/Passed/strongFit_candidates.txt", "a") as f:
                    f.write(candidate_details)
                logging.info("logged passed candidate details in 'strongFit_candidates.txt'")
                
                return self.candidate_report(self.total_points, classified_candidate) 
                 
            elif classified_candidate == "Good Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                with open("Classified_Candidates/Passed/goodFit_candidates.txt", "a") as f:
                    f.write(candidate_details)
                logging.info("logged passed candidate details in 'goodFit_candidates.txt'")  
                
                return self.candidate_report(self.total_points, classified_candidate) 
                
            elif classified_candidate == "Potential Fit":
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()
                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                with open("Classified_Candidates/Passed/potentialFit_candidates.txt", "a") as f:
                    f.write(candidate_details)
                logging.info("logged passed candidate details in 'potentialFit_candidates.txt'")  
                
                return self.candidate_report(self.total_points, classified_candidate) 
                
            else:
                classified_candidate = "Not a Fit"  
                candidate_details: str = self.candidate_report(self.total_points, classified_candidate).model_dump_json()

                logging.info("loaded json obj into 'str' in Classify pipeline")
                
                with open("Classified_Candidates/Failed/NotaFit_candidates.txt", "a") as f:
                    f.write(candidate_details)
                logging.info("logged passed candidate details in 'NotaFit_candidates.txt'")       
                
                return self.candidate_report(self.total_points, classified_candidate) 

        except Exception as e:
            logging.info("Unable to compare score and classify candidate")
            raise CustomException(e, sys)   
        
    def candidate_report(self, total_points, classification) -> ClassificationResult:
        
        try:
            logging.info("Create candidate report")
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
                   
                
                # "top_keyword_matches": [
                #     ["recommendation systems", "recommender pipelines", 0.88],
                #     ["model deployment", "serving ml models", 0.84]
                # ]
            )
    
        except Exception as e:
            logging.info("Unable to create candidate report")
            raise CustomException(e, sys)
        
        
    
    