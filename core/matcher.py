import re
from typing import List, Optional, Tuple
from rapidfuzz import fuzz, process
import logging

from .models import Entity, MatchResult
from config.settings import FUZZY_MATCH_THRESHOLD

class EntityMatcher:
    def __init__(self, entities: List[Entity]):
        self.entities = entities
        self.logger = logging.getLogger(__name__)
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for fuzzy matching"""
        if not isinstance(text, str):
            text = str(text)
        
        # Convert to lowercase and remove extra spaces
        text = text.lower().strip()
        
        # Remove common corporate suffixes and special characters
        suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co']
        text = re.sub(r'[^\w\s]', ' ', text)
        text = ' '.join([word for word in text.split() if word not in suffixes])
        
        return text
    
    def preprocess_entity_name(self, input_text: str) -> str:
        """Preprocess entity name by removing location and other noise"""
        if not isinstance(input_text, str):
            input_text = str(input_text)
        
        # Remove everything after comma
        input_text = input_text.split(',')[0].strip()
        
        # Remove common indicators in parentheses
        input_text = re.sub(r'\([^)]*\)', '', input_text).strip()
        
        return input_text
    
    def exact_match_identifiers(self, input_text: str) -> Optional[Tuple[Entity, str]]:
        """Check for exact matches in identifiers"""
        normalized_input = input_text.strip().upper()
        
        for entity in self.entities:
            # Check ISIN
            if entity.isin and entity.isin.upper() == normalized_input:
                return entity, 'isin'
            
            # Check Ticker
            if entity.ticker and entity.ticker.upper() == normalized_input:
                return entity, 'ticker'
            
            # Check LEI
            if entity.lei and entity.lei.upper() == normalized_input:
                return entity, 'lei'
            
            # Check Entity ID
            if entity.entity_id.upper() == normalized_input:
                return entity, 'entity_id'
        
        return None
    
    def fuzzy_match_name(self, input_text: str) -> Optional[Tuple[Entity, float]]:
        """Perform fuzzy matching on company names with preprocessing"""
        # Preprocess the input to remove locations, etc.
        processed_input = self.preprocess_entity_name(input_text)
        normalized_input = self.normalize_text(processed_input)
        
        best_match = None
        best_score = 0
        
        for entity in self.entities:
            # Exact name match (with original input first)
            if entity.entity_name.strip().lower() == input_text.strip().lower():
                return entity, 100.0
            
            # Exact name match with processed input
            if entity.entity_name.strip().lower() == processed_input.strip().lower():
                return entity, 100.0
            
            # Fuzzy matching with processed input
            normalized_entity_name = self.normalize_text(entity.entity_name)
            
            # Use multiple fuzzy matching strategies
            ratio_score = fuzz.ratio(normalized_input, normalized_entity_name)
            # partial_score = fuzz.partial_ratio(normalized_input, normalized_entity_name)
            token_score = fuzz.token_sort_ratio(normalized_input, normalized_entity_name)
            # token_set_ratio = fuzz.token_set_ratio(normalized_input, normalized_entity_name)
            
            # Take the maximum score from different strategies
            current_score = max(ratio_score, token_score)
            
            if current_score > best_score and current_score >= FUZZY_MATCH_THRESHOLD:
                best_score = current_score
                best_match = entity
        
        return (best_match, best_score) if best_match else None
    
    def get_best_partial_match(self, input_text: str) -> Tuple[Optional[Entity], float]:
        """Get the best partial match even if below threshold"""
        processed_input = self.preprocess_entity_name(input_text)
        normalized_input = self.normalize_text(processed_input)
        
        best_match = None
        best_score = 0
        
        for entity in self.entities:
            normalized_entity_name = self.normalize_text(entity.entity_name)
            
            # Use multiple fuzzy matching strategies
            ratio_score = fuzz.ratio(normalized_input, normalized_entity_name)
            # partial_score = fuzz.partial_ratio(normalized_input, normalized_entity_name)
            token_score = fuzz.token_sort_ratio(normalized_input, normalized_entity_name)
            # token_set_ratio = fuzz.token_set_ratio(normalized_input, normalized_entity_name)

            
            current_score = max(ratio_score ,token_score)
            
            if current_score > best_score:
                best_score = current_score
                best_match = entity
        
        return best_match, best_score
    
    def match_entity(self, input_text: str) -> MatchResult:
        """Main matching function for a single entity"""
        if not input_text or not input_text.strip():
            return MatchResult(
                input_entity=input_text,
                matched_entity=None,
                match_confidence=0.0
            )
        
        # First try exact matching for identifiers
        exact_match = self.exact_match_identifiers(input_text)
        if exact_match:
            entity, field = exact_match
            return MatchResult(
                input_entity=input_text,
                matched_entity=entity,
                match_confidence=100.0
            )
        
        # Then try fuzzy matching for company names
        fuzzy_match = self.fuzzy_match_name(input_text)
        if fuzzy_match:
            entity, confidence = fuzzy_match
            return MatchResult(
                input_entity=input_text,
                matched_entity=entity,
                match_confidence=confidence
            )
        
        # No match found, but get the best partial match for confidence score
        partial_match, partial_confidence = self.get_best_partial_match(input_text)
        
        return MatchResult(
            input_entity=input_text,
            matched_entity=None,
            match_confidence=partial_confidence  # Show actual confidence even for no match
        )