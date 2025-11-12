import streamlit as st
import pandas as pd
from typing import Dict, Any

class LookupComponent:
    def __init__(self, lookup_handler):
        self.lookup_handler = lookup_handler
    
    def render_lookup_interface(self):
        """Render the single entity lookup interface"""
        st.header("🔍 Single Entity")
        st.markdown("Search for individual entities without uploading a file")
        
        # Create two columns for layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            search_types = self.lookup_handler.get_available_search_types()
            
            # Create dropdown for search type
            search_type_options = {st['label']: st['value'] for st in search_types}
            selected_label = st.selectbox(
                "Search By",
                options=list(search_type_options.keys()),
                help="Select the field to search by"
            )
            
            search_type = search_type_options[selected_label]
            
            # Show description for selected search type
            selected_type_info = next(st for st in search_types if st['value'] == search_type)
            st.caption(f"💡 {selected_type_info['description']}")
        
        with col2:
            search_value = st.text_input(
                "Search Value",
                placeholder="Enter value to search...",
                help=f"Enter the {selected_label.lower()} to search for"
            )
        
        # Search button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            search_clicked = st.button(
                "🔍 Search Entity",
                type="primary",
                use_container_width=True
            )
        
        return search_clicked, search_type, search_value
    
    def display_lookup_results(self, result: Dict[str, Any]):
        """Display the results of single entity lookup"""
        if not result['success']:
            st.error(f"❌ {result['error']}")
            return
        
        if result['match_found']:
            self._display_entity_found(result)
        else:
            self._display_entity_not_found(result)
    
    def _display_entity_found(self, result: Dict[str, Any]):
        """Display when entity is found"""
        entity = result['entity']
        
        st.success("✅ Entity Found!")
        
        # Display entity details in a nice format
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Entity Details")
            details_data = {
                'Field': ['Entity Name', 'Entity ID', 'Ticker', 'ISIN', 'LEI'],
                'Value': [
                    entity.entity_name,
                    entity.entity_id,
                    entity.ticker or 'N/A',
                    entity.isin or 'N/A',
                    entity.lei or 'N/A'
                ]
            }
            details_df = pd.DataFrame(details_data)
            st.dataframe(details_df, use_container_width=True, hide_index=True)
    
    def _display_entity_not_found(self, result: Dict[str, Any]):
        """Display when entity is not found"""
        st.error("❌ Entity Not Found")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Search Details:**")
            st.write(f"**Type:** {result['search_type'].replace('_', ' ').title()}")
            st.write(f"**Value:** {result['search_value']}")
        
        with col2:
            st.write("**Suggestions:**")
            st.write("• Check for typos or spelling errors")
            st.write("• Try searching by a different field")
            st.write("• Use company name for fuzzy matching")
            
            if result['search_type'] != 'entity_name':
                st.write("• Try searching by Company Name instead")