
import sys
try:
    import openai
    import httpx
    print(f"openai: {openai.__version__}")
    print(f"httpx: {httpx.__version__}")
    
    from openai import OpenAI
    try:
        client = OpenAI(api_key="test", base_url="https://openrouter.ai/api/v1")
        print("OpenAI client initialized successfully")
    except Exception as e:
        print(f"OpenAI client init failed: {e}")
        
except ImportError as e:
    print(f"ImportError: {e}")
