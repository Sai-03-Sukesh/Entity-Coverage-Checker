import streamlit as st
import logging
from services.matching_service import MatchingService
from utils.lookup_handler import LookupHandler
from components.lookup_component import LookupComponent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntityMatchingApp:
    def __init__(self):
        self.matching_service = MatchingService()
        self.lookup_handler = LookupHandler(self.matching_service)
        self.lookup_component = LookupComponent(self.lookup_handler)
        self.setup_page()
    
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="Entity Matching System",
            # page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🔍 Entity Coverage Checker")
        st.markdown("""
        Upload a list of company names or identifiers to check coverage against our database,
        or search for individual entities using the lookup tool.
        """)
    
    def render_sidebar(self):
        """Render sidebar with information and controls"""
        with st.sidebar:
            st.header("About")
            st.info("""
            **Features:**
            - Entity matching via file upload
            - Single entity lookup
            - Exact matching for identifiers
            - Fuzzy matching for company names
            """)
            
            if st.button("🔄 Refresh Database"):
                try:
                    self.matching_service.refresh_database()
                    st.success("Database refreshed successfully!")
                except Exception as e:
                    st.error(f"Error refreshing database: {str(e)}")
    
    def render_main_interface(self):
        """Render the main interface with tabs"""
        tab1, tab2 = st.tabs(["📤 File Upload", "🔍 Single Entity"])
        
        with tab1:
            self.render_file_upload_section()
        
        with tab2:
            self.render_single_lookup_section()
    
    def render_file_upload_section(self):
        """Render the file upload section"""
        from utils.file_handlers import FileHandler
        from config.settings import SUPPORTED_FILE_TYPES
        
        st.header("📤 Entity Matching")
        st.markdown("Upload a file containing multiple entities for processing")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=SUPPORTED_FILE_TYPES,
            help="Upload CSV or Excel file with one entity per row in the first column",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("Processing your entities..."):
                    processing_result = self.matching_service.process_uploaded_file(uploaded_file)
                
                self.render_bulk_results(processing_result)
                
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
                logger.error(f"File processing error: {str(e)}")
    
    def render_single_lookup_section(self):
        """Render the single entity lookup section"""
        search_clicked, search_type, search_value = self.lookup_component.render_lookup_interface()
        
        if search_clicked:
            if not search_value:
                st.warning("⚠️ Please enter a search value")
                return
            
            with st.spinner("Searching..."):
                result = self.lookup_handler.lookup_single_entity(search_type, search_value)
            
            self.lookup_component.display_lookup_results(result)
    
    def render_bulk_results(self, processing_result):
        """Render bulk processing results (existing functionality)"""
        from utils.file_handlers import FileHandler
        
        st.header("📊 Results")
        
        # Summary statistics
        summary = processing_result.get_summary()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Processed", summary['total_processed'])
        with col2:
            st.metric("Matched", summary['matched'])
        with col3:
            st.metric("Unmatched", summary['unmatched'])
        with col4:
            success_rate = (summary['matched'] / summary['total_processed']) * 100
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        # Matched entities
        if processing_result.matched_entities:
            st.subheader("✅ Matched Entities")
            matched_df = self.matching_service.get_matched_results_df(processing_result)
            st.dataframe(matched_df, use_container_width=True)
        else:
            st.info("No entities were matched.")
        
        # Unmatched entities
        if processing_result.unmatched_entities:
            st.subheader("❌ Unmatched Entities")
            unmatched_df = self.matching_service.get_unmatched_results_df(processing_result)
            st.dataframe(unmatched_df, use_container_width=True)
        
        # Download results
        st.subheader("📥 Download Results")
        file_handler = FileHandler()
        excel_file = file_handler.create_results_excel(processing_result, self.matching_service)
        st.download_button(
            label="Download Results as Excel",
            data=excel_file,
            file_name="entity_matching_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    def run(self):
        """Main application loop"""
        self.render_sidebar()
        self.render_main_interface()

# Run the application
if __name__ == "__main__":
    app = EntityMatchingApp()
    app.run()