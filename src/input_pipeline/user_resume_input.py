# import os 
# import sys 
# from src.exception import CustomException
# from src.logger import logging
# import tempfile
# from src.utils import check_file_extension, check_file_size, parse_experience_from_resume
# from pathlib import Path 
# import shutil
# from src.extraction_pipeline.data_extraction import Extract
# from src.llm_pipeline.llm_semantic_parsing import Parse_Resume_Data
# from src.llm_pipeline.data_validation_normalization import Validate
# from src.llm_pipeline.data_validation_normalization import Normalize
# from src.llm_pipeline.llm_semantic_parsing import Parse_Jd_Data
# from src.input_pipeline.jd_input import Jd_Parsing
# from src.semantic_scoring.candidate_score import Candidate_Score
# from src.semantic_scoring.candidate_fail_fast import Fail_Fast
# from src.classify_candidates.classify import Classify
# from fastapi import FastAPI
 
# class FileInput():
#     def __init__(self, file_path):
#         self.file_path : str = file_path
        
        
        
#     def return_valid_file(self):
#         """User uploads a resume file. Based on the conditions the
#         file is uploaded successfully, else"""
        
#         try:
            
#             if os.path.exists(self.file_path):
#                 logging.info(f'the file {self.file_path} exists')
#                 file_type = check_file_extension(self.file_path)
                
#                 if file_type == self.file_path:
#                     logging.info('file extension is valid, return file path')
#                     file_size_type = check_file_size(self.file_path)
                    
#                     if file_size_type == self.file_path:
#                         logging.info('file size is valid, return file path')
                        
#                         temp_dir = tempfile.mkdtemp()
                        
#                         filename = os.path.basename(self.file_path)
#                         temp_file_path = os.path.join(temp_dir, filename)
                        
#                         # copying the file
#                         shutil.copy2(self.file_path, temp_file_path)

#                         return temp_dir, temp_file_path
                           
                        
#                     else:
#                         print(f"invalid file size, filesize supported till 100Mb")   
                        
#                 else:
#                     print(f"Please check and re-upload a valid file.")
                    
#             else:
#                 print("File does not exists") 
                   
#         except Exception as e:
#             logging.info('invalid file')
#             raise CustomException(e, sys)
    
    
    
    
# if __name__ == '__main__':
    
#     check_filepath = FileInput(r"data\Data_Scientist_Resume.pdf")  
#     temp_dir, file_path = check_filepath.return_valid_file()
    
#     file_obj = Extract(file_path)
#     file_content = file_obj.extract_text() 
#     # print(f"\nFile_Content: {file_content}\n\n")  
           
#     llm_obj = Parse_Resume_Data(file_content)
#     llm_response = llm_obj.llm_resume_parser()
#     validate_obj = Validate(llm_response)           
#     validated_resume_data = validate_obj.resume_data_validation()
    
#     normalize_obj = Normalize(validated_resume_data)
#     normalized_resume_data = normalize_obj.education_test()
#     # print(f"resume: {normalized_resume_data}\n")
    
#     jd_obj = Jd_Parsing("""
#     About the job
# Data Scientist – Bangalore

# No. of Position: 4
# Preferred to be in onshore, if not offshore India but candidate should be based out of Bangalore

# Interview Process: Single round, Face-to-Face only

# Experience: 5–6 years

# Profile Expectation: Strong hands-on, hardcore development-oriented candidates

# Required Skills:
# Strong proficiency in Python (Pandas, NumPy, Scikit-learn)
# Strong SQL skills for data extraction and analysis
# Hands-on experience in Machine Learning (regression, classification, clustering)
# Solid understanding of statistics and probability
# Experience in data cleaning, feature engineering, and model evaluation
# Knowledge of time series analysis and forecasting

# Tools & Platforms:
# Python libraries: Scikit-learn, TensorFlow / PyTorch (preferred)
# Data visualization: Power BI, Tableau, Matplotlib, Seaborn
# Big data exposure: Spark / PySpark (good to have)
# Version control: Git / GitHub
# Cloud exposure: AWS, Azure, or GCP
# Data platforms: Snowflake / BigQuery / Redshift (preferred)
# Understanding of ETL and data pipelines

# Business & Domain Exposure:
# Ability to convert business problems into data-driven solutions
# Experience working with large, real-world datasets
# Strong analytical, communication, and stakeholder management skills
# Domain exposure to Banking, Insurance, Retail, or Telecom is a plus
# Experience in risk modeling, customer analytics, or fraud detection is desirable
# Awareness of data privacy and compliance standards (POPIA knowledge is an advantage)

# """)
#     jd_data = jd_obj.jd_data()
    
#     llm_jd_obj = Parse_Jd_Data(jd_data)
#     llm_jd_response = llm_jd_obj.llm_jd_parser()
#     # print(f"llm_jd_response: {llm_jd_response}")
    
#     validate_jd_obj = Validate(llm_jd_response)
#     validated_jd_data = validate_jd_obj.jd_data_validation()

#     normalize_jd_obj = Normalize(validated_jd_data)
#     normalized_jd_data = normalize_jd_obj.normalize_jd()
#     # print(f"\njd data: {normalized_jd_data}\n")
    
#     score_obj = Candidate_Score(normalized_resume_data, normalized_jd_data)
#     candidate_score = score_obj.education_score()
#     fail_fast_candidate_obj = Fail_Fast(candidate_score)
#     rejected_candidate = fail_fast_candidate_obj.hard_fail_candidate()
#     if rejected_candidate is False:
#         current_score_points, total_score_points = score_obj.candidate_total_score()
#         classify_obj = Classify(current_score_points, total_score_points)
#         classified_candidate = classify_obj.route_candidate()
    
    
#     # print(f"classified_candidate: {classified_candidate}")
    
    
#     shutil.rmtree(temp_dir) 
            
#     # Next Task: order the degree rank and point each degree or figure out,
#     # exp dates calculation
#     # give 20Rs to Anifa