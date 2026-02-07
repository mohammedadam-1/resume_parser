import sys 
from src.exception import CustomException 
from src.logger import logging 
from src.llm_pipeline.data_validation_normalization import (
    ResumeSchema,
    JdSchema
)
from sentence_transformers import SentenceTransformer, util
import torch
from typing import Tuple
from pydantic import BaseModel, PrivateAttr, Field
  
# Load model once when the server starts  
SHARED_MODEL = SentenceTransformer('all-MiniLM-L6-v2')

class Candidate_Score(BaseModel):
    resume_data: ResumeSchema
    jd_data: JdSchema 
    _model: SentenceTransformer = PrivateAttr()
    current_points: dict[str, float] = Field(default_factory=lambda: {
            "required_skills": 0.0,
            "preferred_skills": 0.0,
            "min_experience_months": 0.0,
            "education_required": 0.0,
            "keywords": 0.0
        }) 
    def model_post_init(self, _):
        self._model = SHARED_MODEL
        
           
    
    def skills_score(self) -> dict[str, float]:
        """Calculate the Score for candidate's skills and assign points accordingly"""
        try:
            logging.info("Initialized skills scoring")
    
            candidate_skills = set(self.resume_data.skills)
            logging.info("Loaded candidate skills for scoring")
            
            required_skills = set(self.jd_data.required_skills)
            preferred_skills = set(self.jd_data.preferred_skills)
            logging.info("Loaded required skills and preferred skills for scoring")
            
            matched_required_skills = candidate_skills & required_skills
            # print(f"matched_required_skills: {matched_required_skills}")
            logging.info("Matched candidate skills & required skills")
            if len(required_skills) > 0:
                ratio_req = len(matched_required_skills) / len(required_skills)
                # print("matched required skills: ",matched_required_skills)
                score_req = ratio_req * 50.0
                logging.info("Calculated the score for matched_required_skills")
                # print(f"score_required_skills: {round(score_req,1)}")
            else:
                score_req = 0.0
                logging.info("Assigned score = 0.0 as len of required_skills is 0")
               
            
            matched_preferred_skills = candidate_skills & preferred_skills
            logging.info("Matched candidate skills & preferred skills")
            
            if len(preferred_skills) > 0:
                ratio_pref = len(matched_preferred_skills) / len(preferred_skills)
                # print("matched preferred skills: ",matched_preferred_skills)
                score_pref = ratio_pref * 15.0
                logging.info("Calculated the score for matched_preferred_skills")
                
                # print(f"score_preferred_skills: {round(score_pref, 1)}")
            else:
                score_pref = 0.0
                logging.info("Assigned score = 0.0 as len of preferred_skills is 0")
                
            
            self.current_points["required_skills"] = round(score_req,2)
            self.current_points["preferred_skills"] = round(score_pref,2)
            
            logging.info("Scored and returned candidate skills") 
            return self.current_points             
        
        except Exception as e:
            logging.info("Unable to score candidate experience") 
            raise CustomException(e, sys)

    def experience_score(self) -> dict[str, float]:
        """Calculate the Score for candidate's total experience(months) and assign points accordingly"""
        try: 
            
            current_points = self.education_score()
            
            required_months = self.jd_data.min_experience_months or 0
            half_req = required_months / 2 # Half months required of total required months in JD
            
            candidate_experience = self.resume_data.total_experience_months or 0
            
            if candidate_experience >= required_months:
                score = 15.0
                current_points["min_experience_months"] = score
                
            elif candidate_experience >= half_req:
                score = 10.0
                current_points["min_experience_months"] = score
                
            elif candidate_experience > 0 and candidate_experience < half_req:
                score = 5.0
                current_points["min_experience_months"] = score
                       
            else:
                score = 0.0
                current_points["min_experience_months"] = score
             
            logging.info("Scored and returned candidate experience")    
            return current_points    
            
           
        except Exception as e:
            logging.info("Unable to calculate and score candidate experience")
            raise CustomException(e, sys)
        
    def education_score(self) -> dict[str, float]:
        """Calculate the score for candidate's education and assign points accordingly"""  
        
        try:
            
            current_points = self.skills_score()
            
            try:
                candidate_qualification = self.resume_data.education[0].degree_level   
            except (TypeError, KeyError, IndexError):
                candidate_qualification = None    
                
            try:    
                required_qualification = self.jd_data.required_education[0].degree_level
            except (TypeError, KeyError, IndexError):
                required_qualification = None  
                  
            logging.info(f"loaded candidate_qualification & required_qualification ")
            
            try:
                candidate_education_field = self.resume_data.education[0].field
            except (TypeError, KeyError, IndexError):
                candidate_education_field = None    
            # print(f"candidate_education_field: {candidate_education_field}")
            try:
                required_education_field = self.jd_data.required_education[0].field
            except (TypeError, KeyError, IndexError):
                required_education_field = None    
            # print(f"required_education_field: {required_education_field}")
            logging.info(f"loaded candidate_education_field & required_education_field")
            
            if required_qualification is None:
                current_points["education_required"] = 10.0
                logging.info("10.0 points assigned to candidate for education as required_qualification is None")
                return current_points
            
            elif candidate_qualification is None:
                current_points["education_required"] = 0.0
                logging.info("0.0 points assigned to candidate for education as required_qualification matched is None")
                return current_points
            
            elif required_qualification: 
   
                if required_qualification <= candidate_qualification:
                    current_points["education_required"] = 3.0
                    logging.info("3.0 points assigned to candidate for education as required_qualification matched")
                
                else:
                    current_points["education_required"] = 0.0
                    logging.info("0.0 points assigned to candidate for education as required_qualification matched is None")
                    return current_points
                    
                
                if required_education_field is None:
                    current_points["education_required"] += 7.0
                    logging.info("7.0 points assigned to candidate for required_education_field as its None")
                    return current_points
                
                elif candidate_education_field is None:
                    current_points["education_required"] += 0.0
                    logging.info("0.0 points assigned to candidate for candidate_education_field as its None")
                    return current_points
                
                else:
                    embed_required_field = [required_education_field]
                    embed_candidate_field = [candidate_education_field]
                    
                    required_field_embeddings = self._model.encode(embed_required_field, convert_to_tensor=True)
                    candidate_field_embeddings = self._model.encode(embed_candidate_field, convert_to_tensor=True)
                    logging.info("Converted education fields to vectors")
                    cosine_scores = util.cos_sim(required_field_embeddings, candidate_field_embeddings)
                    logging.info("Calculated cosine score using cosine_similariy")
                    # print(f"required_field_embeddings: {required_field_embeddings}")
                    # print(f"candidate_field_embeddings: {candidate_field_embeddings}")
                    # print(f"cosine_scores: {(cosine_scores[0][0])}")
                    
                    if cosine_scores >= 0.90:
                        current_points["education_required"] += 7.0
                        logging.info(f"7.0 points assigned to candidate's education_field")
                    elif cosine_scores >= 0.80:
                        current_points["education_required"] += 5.0
                        logging.info(f"5.0 points assigned to candidate's education_field")
                    elif cosine_scores >= 0.70:
                        current_points["education_required"] += 4.0
                        logging.info(f"4.0 points assigned to candidate's education_field")
                    elif cosine_scores >= 0.60:
                        current_points["education_required"] += 3.0 
                        logging.info(f"3.0 points assigned to candidate's education_field")  
                    elif cosine_scores >= 0.50:
                        current_points["education_required"] += 2.0 
                        logging.info(f"2.0 points assigned to candidate's education_field")      
                    else:
                        current_points["education_required"] += 1.5
                        logging.info(f"1.5 points assigned to candidate's education_field")     
             
            logging.info("Semantically calculated the education field and returned score")   
            # print(f"self.current_points: {self.current_points}")         
            return current_points            

                
        except Exception as e:
            logging.info("Unable to compare and score candidate education")
            raise CustomException(e, sys)
        
    def keywords_score(self) -> dict[str, float]:
        """Calculate the score for keywords present in candidate's resume and JD, assign points accordingly"""  
        
        try:
            
            current_points = self.experience_score()
            
            logging.info("Initialized keywords matching and scoring")
            
            candidate_keywords = self.resume_data.keywords
            job_desc_keywords = self.jd_data.keywords
            # print(f"candidate_keywords: {candidate_keywords}")
            # print(f"job_desc_keywords: {job_desc_keywords}")
            logging.info("retrieved candidate_keywords and job_desc_keywords for matching")
            
            if not job_desc_keywords:
                current_points["keywords"] = 10.0
                logging.info("10.0 points assigned to candidate's keyword as job_desc_keywords is None")
                
            elif not candidate_keywords:
                current_points["keywords"] = 0.0
                logging.info("0.0 points assigned to candidate's keyword as candidate_keywords is None")
                
            else:
                embed_candidate_keywords = candidate_keywords
                embed_job_desc_keywords = job_desc_keywords
                # convert keywords into vector embeddings
                candidate_keywords_embedding = self._model.encode(embed_candidate_keywords, convert_to_tensor=True) 
                job_desc_embedding = self._model.encode(embed_job_desc_keywords, convert_to_tensor=True)
                logging.info("candidate_keywords and job_desc_keywords embeded")
                # print(f"candidate_keywords_embedding: {candidate_keywords_embedding}")
                # print(f"\njob_desc_embedding: {job_desc_embedding}")
                cosine_scores = util.cos_sim(candidate_keywords_embedding, job_desc_embedding)
                
                # pick the most matching keywords
                best_matches_per_keyword, _ = torch.max(cosine_scores, dim=1)
                logging.info("found the best matched keywords")
                # print(f"best_matches_per_keyword: {best_matches_per_keyword}")
                final_similarity = torch.mean(best_matches_per_keyword).item() 
                logging.info("Averaged the score by dividing final_similarity by the len of best_matches_per_keyword") 
                # print(f"final_similarity: {final_similarity * 10}")
                current_points["keywords"] = round(final_similarity * 10, 2)
                
                logging.info("Assigned points to candidate's keywors and returned self.current_points")
            return current_points
        
        except Exception as e:
            logging.info("Unable to compare and score keywords")
            raise CustomException(e, sys)
        
    def candidate_total_score(self) -> Tuple[dict[str, float], float]:
        """Return current points and the sum of points assigned to candidate"""
        
        try:
            current_points = self.keywords_score()
            logging.info("Initialize to sum the points assigned to candidat")
            
            total_score = sum(current_points.values())
            candidate_total_score = round(total_score, 2)
            
            logging.info("Retured sum of all points")
            return current_points, candidate_total_score
             
        except Exception as e:
            logging.info("Unable to sum the candidate score")
            raise CustomException(e, sys)
        
        