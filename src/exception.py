import sys 


def custom_error_message(error, error_details:sys):
    _,_,exc_tb = error_details.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = "error occured in [{0}] file, lineno [{1}], error: [{2}]".format(
        file_name, exc_tb.tb_lineno, str(error)
    )
    
    return error_message
    
    
class CustomException(Exception):
    def __init__(self, error, error_details:sys):
        super().__init__(error)
        self.error = custom_error_message(error, error_details)
        
    def __str__(self):
        return self.error
    

    
      
            
    