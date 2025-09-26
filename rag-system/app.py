import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables
load_dotenv()

app = FastAPI()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.get("/")
def read_root():
    return {
        "message": "RAG System Running",
        "api_key_loaded": bool(GROQ_API_KEY)
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print(f"API Key Loaded: {bool(GROQ_API_KEY)}")
    print("Starting server at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
