import streamlit as st
import os
import time
from blog_generator import generate_blog

# Set page configuration
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1 {
        color: #2c3e50;
        margin-bottom: 1.5rem;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 5px;
    }
    .stButton button:hover {
        background-color: #2980b9;
    }
    .blog-content {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
        margin-top: 1rem;
    }
    .status-container {
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .agent-status {
        margin-bottom: 0.5rem;
        padding: 0.5rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 Multi-Agent Blog Generator")
st.markdown("Generate high-quality blog posts using a team of specialized AI agents powered by Groq's llama3-70b-8192 model.")

# Sidebar with workflow explanation
with st.sidebar:
    st.header("How It Works")
    st.markdown("""
    This application uses a multi-agent system to generate blog posts:
    
    1. **Researcher Agent** gathers information on the topic
    2. **Outline Generator** creates a structured outline
    3. **Content Writer** produces the blog draft
    4. **Reviewer** evaluates and provides feedback
    
    If revisions are needed, the Content Writer will refine the draft until approved.
    """)
    
    st.header("About")
    st.markdown("""
    Built with:
    - Langgraph for workflow orchestration
    - Groq's llama3-70b-8192 LLM
    - Streamlit for the user interface
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Input form
    st.header("Generate a Blog Post")
    topic = st.text_input("Enter a blog topic:", placeholder="e.g., The Future of Quantum Computing")
    
    # Advanced options
    with st.expander("Advanced Options"):
        save_to_file = st.checkbox("Save output to file", value=True)
        file_name = st.text_input("File name:", value="generated_blog.md")

    # Generate button
    generate_button = st.button("Generate Blog Post", type="primary", use_container_width=True)

with col2:
    # Workflow visualization
    st.header("Workflow")
    st.markdown("""
    ```mermaid
    graph TD
        A[Researcher] --> B[Outline Generator]
        B --> C[Content Writer]
        C --> D[Reviewer]
        D -->|Needs Revision| C
        D -->|Approved| E[Final Blog]
    ```
    """)

# Process status
if 'status' not in st.session_state:
    st.session_state.status = None
    st.session_state.blog_content = None
    st.session_state.current_step = None

# Handle generation
if generate_button and topic:
    st.session_state.status = "generating"
    st.session_state.current_step = "started"
    st.session_state.blog_content = None
    
    # Create a status container
    status_container = st.empty()
    
    # Display initial status
    with status_container.container():
        st.markdown("### Generation Status")
        st.markdown(f"**Current Step:** Starting process...")
        
        researcher_status = st.empty()
        outline_status = st.empty()
        writer_status = st.empty()
        reviewer_status = st.empty()
        
        researcher_status.markdown("⏳ **Researcher:** Gathering information...")
    
    try:
        # Start the blog generation process
        result = generate_blog(topic)
        
        # Update status based on result
        with status_container.container():
            st.markdown("### Generation Status")
            st.markdown(f"**Current Step:** {result['current_step']}")
            
            researcher_status.markdown("✅ **Researcher:** Completed")
            outline_status.markdown("✅ **Outline Generator:** Completed")
            writer_status.markdown("✅ **Content Writer:** Completed")
            reviewer_status.markdown("✅ **Reviewer:** Completed")
            
            st.success("Blog post generated successfully!")
        
        # Save the blog content
        st.session_state.blog_content = result['final']
        
        # Save to file if requested
        if save_to_file:
            with open(file_name, 'w') as f:
                f.write(result['final'])
            st.success(f"Blog saved to {file_name}")
            
    except Exception as e:
        with status_container.container():
            st.error(f"An error occurred: {str(e)}")
        st.session_state.status = "error"

# Display the generated blog
if st.session_state.blog_content:
    st.header("Generated Blog Post")
    st.markdown("<div class='blog-content'>" + st.session_state.blog_content + "</div>", unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="Download Blog Post",
        data=st.session_state.blog_content,
        file_name="blog_post.md",
        mime="text/markdown"
    )

# Show a message if no topic is entered
if not topic and generate_button:
    st.warning("Please enter a topic for your blog post.")

# Footer
st.markdown("---")
st.markdown("Powered by Langgraph and Groq | Created with ❤️ using Streamlit")
