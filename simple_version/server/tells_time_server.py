#### tells_time_server

# ---------------------------------------------------------
# Import required classes from FastAPI and other libraries
# ---------------------------------------------------------

# FastAPI is a modern, high-performance web framework for building APIs in Python.
# It provides built-in support for async programming, validation, and auto-generated docs.
from fastapi import FastAPI, HTTPException

# Pydantic is used by FastAPI for data validation and parsing.
# It ensures incoming request data matches expected schema.
from pydantic import BaseModel

# Import datetime to fetch current system time.
from datetime import datetime

# Typing utilities for defining structured request/response models.
from typing import List

# ---------------------------------------------------------
# Create FastAPI application instance
# ---------------------------------------------------------

# This initializes the FastAPI app.
# Equivalent to Flask(app), but with more built-in capabilities.
app = FastAPI()

# ---------------------------------------------------------
# Define Data Models (A2A Schema)
# ---------------------------------------------------------

# In A2A protocol, messages are made of "parts".
# Each part can represent text, file, or structured data.
# Here we define a simple text part.

class Part(BaseModel):
    text: str  # The textual content of the message part


# A message represents a communication turn between user and agent.
# It contains:
# - role: who sent it (user / agent)
# - parts: list of content parts

class Message(BaseModel):
    role: str
    parts: List[Part]


# A Task is the core unit of work in A2A.
# It contains:
# - id: unique identifier
# - message: the user input

class Task(BaseModel):
    id: str
    message: Message


# ---------------------------------------------------------
# Endpoint: Agent Card (Discovery Phase)
# ---------------------------------------------------------

# Define a GET endpoint for agent discovery.
# Clients call this endpoint to understand:
# - what this agent does
# - how to interact with it
# - what capabilities it supports

# NOTE:
# Recommended standard path is:
# /.well-known/agent-card.json

@app.get("/.well-known/agent-card.json")
async def agent_card():
    """
    Returns the Agent Card metadata.

    This is used in the DISCOVERY phase of A2A:
    - Clients fetch this before sending tasks
    - Helps in dynamic capability understanding
    """
    return {
        "name": "TellTimeAgent",  # Human-readable name
        "description": "Tells the current time when asked.",  # Agent purpose
        "url": "http://localhost:8000",  # Base URL of this agent
        "version": "1.0",  # Versioning for compatibility
        "capabilities": {
            "streaming": False,           # No real-time streaming support
            "pushNotifications": False    # No async push updates
        }
    }


# ---------------------------------------------------------
# Endpoint: Task Handling (Execution Phase)
# ---------------------------------------------------------

# This endpoint handles incoming tasks from A2A clients.
# Equivalent to Flask's /tasks/send

@app.post("/tasks/send")
async def handle_task(task: Task):
    """
    Handles incoming A2A task.

    Steps:
    1. Validate request using Pydantic model
    2. Extract user message
    3. Process logic
    4. Return structured response
    """

    try:
        # Extract user message from the first part
        user_message = task.message.parts[0].text

    except Exception:
        # If request structure is invalid, return HTTP 400
        raise HTTPException(status_code=400, detail="Invalid task format")

    # ---------------------------------------------------------
    # Business Logic: Generate response
    # ---------------------------------------------------------

    # Fetch current system time
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare response text
    reply_text = f"The current time is: {current_time}"

    # ---------------------------------------------------------
    # Construct A2A-compliant response
    # ---------------------------------------------------------

    return {
        "id": task.id,  # Maintain same task ID
        "status": {
            "state": "completed"  # Mark task as completed
        },
        "messages": [
            task.message.dict(),  # Include original user message
            {
                "role": "agent",  # Response from agent
                "parts": [
                    {"text": reply_text}  # Response content
                ]
            }
        ]
    }


# ---------------------------------------------------------
# Run the FastAPI Server
# ---------------------------------------------------------

# Unlike Flask, FastAPI is typically run using ASGI servers like Uvicorn.

# To run this app:
# uvicorn main:app --reload

# - main: filename (tell_time_server)
# - app: FastAPI instance
# - --reload: auto-restart on code changes
