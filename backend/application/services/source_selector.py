"""
Source Selector Service
Intelligently selects the best data source for a query
"""

import logging
from typing import List, Optional
from core.interfaces.data_source import IDataSource
from core.models.query import Query

logger = logging.getLogger(__name__)


class SourceSelector:
    """
    Selects the best data source for a query
    
    Following SOLID:
    - SRP: Single responsibility - source selection logic
    - OCP: Works with any IDataSource implementations
    - DIP: Depends on IDataSource interface
    
    Strategy:
    1. Check query preference (if specified)
    2. Ask each source if it can handle the query
    3. Return first capable source or None
    """
    
    def __init__(self):
        """Initialize source selector"""
        logger.info("Source Selector initialized")
    
    async def select_source(
        self,
        query: Query,
        available_sources: List[IDataSource]
    ) -> Optional[IDataSource]:
        """
        Select the best data source for a query
        
        Args:
            query: User query
            available_sources: List of available data sources
            
        Returns:
            Selected data source or None
            
        Strategy:
            1. If query has source preference (documents/database), use that
            2. Otherwise, ask each source if it can handle the query
            3. Return first source that can handle it
        """
        try:
            # Check if user specified a source preference
            if query.source_preference and query.source_preference != "auto":
                for source in available_sources:
                    if source.get_source_type() == query.source_preference:
                        logger.info(f"Using preferred source: {source.get_source_type()}")
                        return source
                
                logger.warning(f"Preferred source '{query.source_preference}' not available")
            
            # Auto-select: ask each source if it can handle the query
            for source in available_sources:
                try:
                    can_handle = await source.can_handle(query)
                    if can_handle:
                        logger.info(f"Selected source: {source.get_source_type()}")
                        return source
                except Exception as e:
                    logger.warning(f"Source {source.get_source_type()} check failed: {e}")
                    continue
            
            logger.warning("No suitable data source found for query")
            return None
            
        except Exception as e:
            logger.error(f"Source selection failed: {e}")
            return None
    
    async def select_all_capable_sources(
        self,
        query: Query,
        available_sources: List[IDataSource]
    ) -> List[IDataSource]:
        """
        Get all data sources that can handle the query
        
        Args:
            query: User query
            available_sources: List of available data sources
            
        Returns:
            List of capable data sources
            
        Use case: For fallback strategy or parallel search
        """
        capable_sources = []
        
        for source in available_sources:
            try:
                can_handle = await source.can_handle(query)
                if can_handle:
                    capable_sources.append(source)
            except Exception as e:
                logger.warning(f"Source {source.get_source_type()} check failed: {e}")
                continue
        
        logger.info(f"Found {len(capable_sources)} capable sources")
        return capable_sources

