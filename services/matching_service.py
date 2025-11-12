from typing import List, Dict, Any
import logging
import pandas as pd

from core.database import DatabaseHandler
from core.matcher import EntityMatcher
from core.models import ProcessingResult, MatchResult
from utils.file_handlers import FileHandler

class MatchingService:
    def __init__(self, db_path: str = None):
        self.db_handler = DatabaseHandler(db_path) if db_path else DatabaseHandler()
        self.matcher = EntityMatcher(self.db_handler.get_all_entities())
        self.logger = logging.getLogger(__name__)
        self.file_handler = FileHandler()
    
    def process_input_list(self, input_entities: List[str]) -> ProcessingResult:
        """Process a list of input entities"""
        matched_entities = []
        unmatched_entities = []
        
        for entity in input_entities:
            result = self.matcher.match_entity(entity)
            
            if result.is_match_found():
                matched_entities.append(result)
            else:
                unmatched_entities.append(result)
        
        return ProcessingResult(
            matched_entities=matched_entities,
            unmatched_entities=unmatched_entities
        )
    
    def process_uploaded_file(self, uploaded_file) -> ProcessingResult:
        """Process uploaded file with entities"""
        try:
            input_entities = self.file_handler.read_input_file(uploaded_file)
            return self.process_input_list(input_entities)
        except Exception as e:
            self.logger.error(f"Error processing uploaded file: {str(e)}")
            raise
    
    def refresh_database(self) -> None:
        """Refresh the database and update matcher"""
        self.db_handler.refresh_database()
        self.matcher = EntityMatcher(self.db_handler.get_all_entities())
        self.logger.info("Database refreshed successfully")
    
    def get_matched_results_df(self, processing_result: ProcessingResult) -> pd.DataFrame:
        """Convert matched results to DataFrame for display"""
        results = []
        
        for match in processing_result.matched_entities:
            entity_dict = match.matched_entity.to_dict()
            entity_dict.update({
                'Input Entity': match.input_entity,
                'Match Confidence': f"{match.match_confidence:.1f}%"
            })
            results.append(entity_dict)
        
        return pd.DataFrame(results)
    
    def get_unmatched_results_df(self, processing_result: ProcessingResult) -> pd.DataFrame:
        """Convert unmatched results to DataFrame for display - FIXED confidence"""
        results = []
        
        for unmatched in processing_result.unmatched_entities:
            results.append({
                'Input Entity': unmatched.input_entity,
                'Best Match Confidence': f"{unmatched.match_confidence:.1f}%"  # Show actual confidence
            })
        
        return pd.DataFrame(results)