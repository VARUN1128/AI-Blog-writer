from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Cache for available model
_available_model = None

def get_available_model():
    """Get an available Gemini model"""
    global _available_model
    if _available_model:
        return _available_model
    
    # Try to list available models
    try:
        models = genai.list_models()
        # Priority order: gemini-2.0-flash first (user preference), then other stable models
        preferred_models = [
            'gemini-2.0-flash',
           
            'gemini-2.5-flash-lite'
        ]
        
        # First, try to find preferred stable models
        for preferred in preferred_models:
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    model_name = model.name.replace('models/', '')
                    if model_name == preferred:
                        _available_model = model_name
                        print(f"Using model: {model_name}")
                        return _available_model
        
        # If no preferred model found, use first available flash or pro model
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                # Skip preview/experimental models if possible
                if 'preview' not in model_name.lower() and 'exp' not in model_name.lower():
                    if 'flash' in model_name.lower() or 'pro' in model_name.lower():
                        _available_model = model_name
                        print(f"Using model: {model_name}")
                        return _available_model
        
        # Last resort: use any available model
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name.replace('models/', '')
                _available_model = model_name
                print(f"Using model: {model_name}")
                return _available_model
    except Exception as e:
        print(f"Error listing models: {e}")
    
    # Fallback: use gemini-2.0-flash first, then other stable models
    fallback_models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-pro-latest', 'gemini-flash-latest']
    fallback = fallback_models[0]
    print(f"Using fallback model: {fallback}")
    return fallback

# Storage for blogs (in-memory, with JSON backup)
BLOGS_FILE = "blogs.json"
blogs = []

# Load existing blogs from JSON file if it exists
def load_blogs():
    global blogs
    if Path(BLOGS_FILE).exists():
        try:
            with open(BLOGS_FILE, 'r', encoding='utf-8') as f:
                all_blogs = json.load(f)
                # Filter out error messages
                blogs = [blog for blog in all_blogs if not blog.get('content', '').startswith('Error generating blog content')]
                # Save cleaned blogs back if there were errors
                if len(blogs) != len(all_blogs):
                    save_blogs()
        except:
            blogs = []

# Save blogs to JSON file
def save_blogs():
    with open(BLOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(blogs, f, ensure_ascii=False, indent=2)


load_blogs()

def generate_blog_content(title: str) -> str:
    """Generate blog content using Gemini API"""
    global _available_model
    
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY not configured"
    
    prompt = f"""Write a comprehensive, engaging blog post about: {title}

Requirements:
- Write at least 500 words
- Use clear headings and subheadings
- Include an introduction and conclusion
- Make it informative and well-structured
- Use a professional but engaging tone"""
    
    # Get available model
    model_name = get_available_model()
    if not model_name:
        return "Error: No available Gemini model found. Please check your API key and quota."
    
    # Try the cached model first
    models_to_try = [model_name]
    # Add fallback models if primary fails (gemini-2.0-flash first)
    fallback_models = ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-pro-latest', 'gemini-flash-latest']
    for fallback in fallback_models:
        if fallback not in models_to_try:
            models_to_try.append(fallback)
    
    last_error = None
    for model_name_to_try in models_to_try:
        try:
            model = genai.GenerativeModel(model_name_to_try)
            response = model.generate_content(prompt)
            # If successful, cache this model
            _available_model = model_name_to_try
            return response.text
        except Exception as e:
            last_error = str(e)
            # Continue to next model
            continue
    
    # All models failed, reset cache
    _available_model = None
    return f"Error generating blog content: {last_error}. Tried models: {', '.join(models_to_try)}"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Homepage with blog title input"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_blogs(request: Request, titles: str = Form(...)):
    """Generate blogs from titles"""
    if not GEMINI_API_KEY:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": "GEMINI_API_KEY not found in .env file"
        })
    
    # Parse titles (one per line)
    title_list = [title.strip() for title in titles.split('\n') if title.strip()]
    
    # Get existing titles to avoid duplicates
    existing_titles = {blog.get('title', '').strip().lower() for blog in blogs}
    
    # Generate blog for each title
    for title in title_list:
        # Skip if blog with this title already exists
        if title.lower() in existing_titles:
            continue
            
        content = generate_blog_content(title)
        # Only save if content was generated successfully (not an error)
        if not content.startswith('Error generating blog content'):
            blog_entry = {
                "title": title,
                "content": content
            }
            blogs.append(blog_entry)
            # Add to existing titles set to prevent duplicates in the same batch
            existing_titles.add(title.lower())
    
    # Save to JSON file
    save_blogs()
    
    # Redirect to blog page
    return RedirectResponse(url="/blog", status_code=303)

@app.get("/blog", response_class=HTMLResponse)
async def blog_page(request: Request):
    """Display all generated blogs"""
    return templates.TemplateResponse("blog.html", {
        "request": request,
        "blogs": blogs
    })

@app.post("/clear-blogs")
async def clear_blogs():
    """Clear all blogs"""
    global blogs
    blogs = []
    save_blogs()
    return RedirectResponse(url="/blog", status_code=303)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

