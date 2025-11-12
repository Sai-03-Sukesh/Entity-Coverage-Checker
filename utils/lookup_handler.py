import logging
from typing import Optional, Dict, Any
from core.models import Entity, MatchResult

class LookupHandler:
    def __init__(self, matching_service):
        self.matching_service = matching_service
        self.logger = logging.getLogger(__name__)
    
    def lookup_single_entity(self, search_type: str, search_value: str) -> Dict[str, Any]:
        """
        Lookup a single entity by specific field
        """
        try:
            if not search_value or not search_value.strip():
                return {
                    'success': False,
                    'error': 'Search value cannot be empty',
                    'match_found': False
                }
            
            # Normalize search value
            search_value = search_value.strip()
            
            # Perform targeted search based on type
            if search_type == 'entity_name':
                result = self._lookup_by_name(search_value)
            else:
                result = self._lookup_by_identifier(search_type, search_value)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in single entity lookup: {str(e)}")
            return {
                'success': False,
                'error': f'Search failed: {str(e)}',
                'match_found': False
            }
    
    def _lookup_by_identifier(self, identifier_type: str, value: str) -> Dict[str, Any]:
        """Lookup by specific identifier (exact match)"""
        entities = self.matching_service.db_handler.get_all_entities()
        
        for entity in entities:
            identifier_field = getattr(entity, identifier_type, None)
            if identifier_field and str(identifier_field).strip().upper() == value.upper():
                return {
                    'success': True,
                    'match_found': True,
                    'entity': entity,
                    'confidence': 100.0
                }
        
        return {
            'success': True,
            'match_found': False,
            'search_type': identifier_type,
            'search_value': value,
            'confidence': 0.0
        }
    
    def _lookup_by_name(self, name: str) -> Dict[str, Any]:
        """Lookup by company name (fuzzy match) with preprocessing"""
        # Use the existing matcher for name lookup
        match_result = self.matching_service.matcher.match_entity(name)
        
        if match_result.is_match_found():
            return {
                'success': True,
                'match_found': True,
                'entity': match_result.matched_entity,
                'confidence': match_result.match_confidence
            }
        else:
            return {
                'success': True,
                'match_found': False,
                'search_type': 'entity_name',
                'search_value': name,
                'confidence': match_result.match_confidence  # Include confidence for no match
            }
    
    def get_available_search_types(self) -> list:
        """Get list of available search types"""
        return [
            {'value': 'entity_name', 'label': 'Company Name', 'description': 'Fuzzy match on company names'},
            {'value': 'ticker', 'label': 'Ticker Symbol', 'description': 'Exact match on ticker symbols'},
            {'value': 'isin', 'label': 'ISIN', 'description': 'Exact match on ISIN codes'},
            {'value': 'lei', 'label': 'LEI', 'description': 'Exact match on LEI codes'},
            {'value': 'entity_id', 'label': 'Entity ID', 'description': 'Exact match on entity IDs'}
        ]