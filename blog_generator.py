import os
from typing import TypedDict, Annotated, Sequence
from typing_extensions import TypedDict
from dotenv import load_dotenv
from groq import Groq
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import Graph, StateGraph
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

# Define the state schema
class BlogState(TypedDict):
    topic: str
    research: str
    outline: str
    draft: str
    feedback: str
    final: str
    current_step: str

# Agent definitions
def create_researcher_agent():
    template = """You are a research agent. Given a topic, conduct thorough research and provide key points.
    
    Topic: {topic}
    
    Provide a comprehensive research summary including key points, statistics, and main arguments."""
    
    prompt = PromptTemplate(template=template, input_variables=["topic"])
    model = ChatGroq(model_name="llama3-70b-8192", temperature=0.7)
    chain = prompt | model | StrOutputParser()
    
    return chain

def create_outline_generator():
    template = """You are an outline generator. Based on the research provided, create a structured outline for a blog post.
    
    Research: {research}
    
    Create a detailed outline with main sections and subsections."""
    
    prompt = PromptTemplate(template=template, input_variables=["research"])
    model = ChatGroq(model_name="llama3-70b-8192", temperature=0.7)
    chain = prompt | model | StrOutputParser()
    
    return chain

def create_content_writer():
    template = """You are a content writer. Using the outline and research provided, write a comprehensive blog post.
    
    Outline: {outline}
    Research: {research}
    
    Write an engaging and informative blog post following the outline."""
    
    prompt = PromptTemplate(template=template, input_variables=["outline", "research"])
    model = ChatGroq(model_name="llama3-70b-8192", temperature=0.7)
    chain = prompt | model | StrOutputParser()
    
    return chain

def create_reviewer():
    template = """You are an editor reviewing a blog post draft. Provide feedback and suggestions for improvement.
    If the post is ready for publication, indicate 'APPROVED'. Otherwise, provide specific feedback.
    
    Draft: {draft}
    
    Provide your review and feedback:"""
    
    prompt = PromptTemplate(template=template, input_variables=["draft"])
    model = ChatGroq(model_name="llama3-70b-8192", temperature=0.7)
    chain = prompt | model | StrOutputParser()
    
    return chain

# Node functions
def research(state: BlogState) -> BlogState:
    researcher = create_researcher_agent()
    research_results = researcher.invoke({"topic": state["topic"]})
    state["research"] = research_results
    state["current_step"] = "research_completed"
    return state

def create_outline(state: BlogState) -> BlogState:
    outline_generator = create_outline_generator()
    outline = outline_generator.invoke({"research": state["research"]})
    state["outline"] = outline
    state["current_step"] = "outline_completed"
    return state

def write_content(state: BlogState) -> BlogState:
    writer = create_content_writer()
    draft = writer.invoke({"outline": state["outline"], "research": state["research"]})
    state["draft"] = draft
    state["current_step"] = "draft_completed"
    return state

def review_content(state: BlogState) -> BlogState:
    reviewer = create_reviewer()
    feedback = reviewer.invoke({"draft": state["draft"]})
    state["feedback"] = feedback
    state["current_step"] = "review_completed"
    return state

# Conditional edge function
def needs_revision(state: BlogState) -> bool:
    return "APPROVED" not in state["feedback"]

def finalize_post(state: BlogState) -> BlogState:
    state["final"] = state["draft"]
    state["current_step"] = "completed"
    return state

# Create the graph
def create_blog_workflow() -> Graph:
    # Initialize the graph
    workflow = StateGraph(BlogState)
    
    # Add nodes
    workflow.add_node("researcher", research)
    workflow.add_node("create_outline", create_outline)
    workflow.add_node("write_content", write_content)
    workflow.add_node("review_content", review_content)
    workflow.add_node("finalize_post", finalize_post)
    
    # Add edges
    workflow.add_edge("researcher", "create_outline")
    workflow.add_edge("create_outline", "write_content")
    workflow.add_edge("write_content", "review_content")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "review_content",
        needs_revision,
        {
            True: "write_content",
            False: "finalize_post"
        }
    )
    
    # Set entry and end nodes
    workflow.set_entry_point("researcher")
    workflow.set_finish_point("finalize_post")
    
    return workflow.compile()

# Function to run the blog generation process
def generate_blog(topic: str) -> dict:
    # Initialize the workflow
    workflow = create_blog_workflow()
    
    # Create initial state
    initial_state = {
        "topic": topic,
        "research": "",
        "outline": "",
        "draft": "",
        "feedback": "",
        "final": "",
        "current_step": "started"
    }
    
    # Execute the workflow
    result = workflow.invoke(initial_state)
    return result

if __name__ == "__main__":
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Generate a blog post using AI agents')
    parser.add_argument('--topic', type=str, default="The Impact of Artificial Intelligence on Modern Healthcare",
                        help='Topic for the blog post')
    parser.add_argument('--output', type=str, default=None,
                        help='Output file to save the blog post (optional)')
    
    args = parser.parse_args()
    
    print(f"Generating blog post on topic: {args.topic}")
    print("This may take a few minutes...")
    
    # Generate the blog
    result = generate_blog(args.topic)
    
    # Print the final blog post
    print("\n" + "="*50)
    print("FINAL BLOG POST:")
    print("="*50 + "\n")
    print(result['final'])
    
    # Save to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result['final'])
        print(f"\nBlog post saved to {args.output}")
