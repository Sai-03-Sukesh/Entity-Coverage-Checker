import pandas as pd
from typing import List
import logging
from io import BytesIO

class FileHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_input_file(self, uploaded_file) -> List[str]:
        """Read input file and extract entities"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError("Unsupported file format")
            
            # Extract entities from first column
            entities = df.iloc[:, 0].dropna().astype(str).tolist()
            
            self.logger.info(f"Read {len(entities)} entities from uploaded file")
            return entities
            
        except Exception as e:
            self.logger.error(f"Error reading input file: {str(e)}")
            raise
    
    def create_results_excel(self, processing_result, matching_service) -> BytesIO:
        """Create Excel file with matching results"""
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Matched entities sheet
            matched_df = matching_service.get_matched_results_df(processing_result)
            if not matched_df.empty:
                matched_df.to_excel(writer, sheet_name='Matched Entities', index=False)
            
            # Unmatched entities sheet
            unmatched_df = matching_service.get_unmatched_results_df(processing_result)
            if not unmatched_df.empty:
                unmatched_df.to_excel(writer, sheet_name='Unmatched Entities', index=False)
            
            # Summary sheet
            summary_data = {
                'Metric': ['Total Processed', 'Matched', 'Unmatched', 'Success Rate'],
                'Value': [
                    processing_result.get_summary()['total_processed'],
                    processing_result.get_summary()['matched'],
                    processing_result.get_summary()['unmatched'],
                    f"{(processing_result.get_summary()['matched']/processing_result.get_summary()['total_processed']*100):.1f}%"
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        return output