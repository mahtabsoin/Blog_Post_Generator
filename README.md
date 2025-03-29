This is a Langgraph-based application that automates blog post generation using multiple AI agents powered by Groq's LLM models.

## Architecture

The application uses four specialized agents working together in a workflow:

1. **Topic Researcher**: Gathers and synthesizes information about the given topic
2. **Outline Generator**: Creates a structured outline based on research
3. **Content Writer**: Writes the blog post following the outline
4. **Reviewer/Editor**: Reviews and provides feedback on the draft

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Groq API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

## Usage

```python
from blog_generator import generate_blog

# Generate a blog post
topic = "The Impact of Artificial Intelligence on Modern Healthcare"
result = generate_blog(topic)

# Print the final blog post
print(result['final'])
```

## Workflow

1. The Researcher agent conducts initial research on the topic
2. The Outline Generator creates a structured outline
3. The Content Writer produces the first draft
4. The Reviewer provides feedback
5. If revisions are needed, the process loops back to the Content Writer
6. Once approved, the post is finalized

## Requirements

- Python 3.8+
- Groq API key
- Required packages listed in requirements.txt
