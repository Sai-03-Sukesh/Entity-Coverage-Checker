import pandas as pd
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from .models import Entity
from config.settings import MASTER_DB_PATH, COLUMN_MAPPINGS

class DatabaseHandler:
    def __init__(self, db_path: Path = MASTER_DB_PATH):
        self.db_path = db_path
        self.entities: List[Entity] = []
        self.logger = logging.getLogger(__name__)
        self._load_database()
    
    def _load_database(self) -> None:
        """Load entities from Excel file"""
        try:
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            df = pd.read_excel(self.db_path)
            self.logger.info(f"Loaded database with {len(df)} entities")
            
            # Map columns to standard names
            column_mapping = self._map_columns(df.columns)
            self.entities = self._parse_entities(df, column_mapping)
            
            self.logger.info(f"Successfully parsed {len(self.entities)} entities")
            
        except Exception as e:
            self.logger.error(f"Error loading database: {str(e)}")
            raise
    
    def _map_columns(self, columns: pd.Index) -> Dict[str, str]:
        """Map various column names to standard names"""
        mapping = {}
        for standard_name, possible_names in COLUMN_MAPPINGS.items():
            for col in columns:
                if col in possible_names:
                    mapping[standard_name] = col
                    break
        return mapping
    
    def _parse_entities(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[Entity]:
        """Parse DataFrame into Entity objects"""
        entities = []
        
        for _, row in df.iterrows():
            try:
                entity = Entity(
                    entity_id=str(row[column_mapping['entity_id']]),
                    entity_name=str(row[column_mapping['company_name']]),
                    ticker=str(row[column_mapping['ticker']]) if pd.notna(row[column_mapping['ticker']]) else None,
                    isin=str(row[column_mapping['isin']]) if pd.notna(row[column_mapping['isin']]) else None,
                    lei=str(row[column_mapping['lei']]) if pd.notna(row[column_mapping['lei']]) else None
                )
                entities.append(entity)
            except Exception as e:
                self.logger.warning(f"Error parsing entity row: {str(e)}")
                continue
        
        return entities
    
    def get_all_entities(self) -> List[Entity]:
        """Get all entities from database"""
        return self.entities.copy()
    
    def refresh_database(self) -> None:
        """Reload database from file"""
        self._load_database()
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity
        return None