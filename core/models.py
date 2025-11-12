from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Entity:
    entity_id: str
    entity_name: str
    ticker: Optional[str] = None
    isin: Optional[str] = None
    lei: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "Entity ID": self.entity_id,
            "Entity Name": self.entity_name,
            "Ticker": self.ticker,
            "ISIN": self.isin,
            "LEI": self.lei
        }

@dataclass
class MatchResult:
    input_entity: str
    matched_entity: Optional[Entity]
    match_confidence: float
    # match_type: str  # 'exact', 'fuzzy', 'none'
    # matched_field: str
    
    def is_match_found(self) -> bool:
        return self.matched_entity is not None

@dataclass
class ProcessingResult:
    matched_entities: list[MatchResult]
    unmatched_entities: list[MatchResult]
    
    def get_summary(self) -> Dict[str, int]:
        return {
            "total_processed": len(self.matched_entities) + len(self.unmatched_entities),
            "matched": len(self.matched_entities),
            "unmatched": len(self.unmatched_entities)
        }