"""
Setup script to create .env file for API key configuration
"""

import os
from pathlib import Path


def create_env_file():
    """Create .env file with API key configuration."""
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Check if .env already exists
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (yes/no): ").lower()
        if response != 'yes':
            print("Cancelled. Keeping existing .env file.")
            return
    
    print("\n🔑 Setting up .env file for OpenRouter API key configuration\n")
    print("=" * 60)
    print("\n💡 Get your free API key from: https://openrouter.ai")
    print("   OpenRouter provides access to GPT-4o, Claude, and other models\n")
    
    # Get API key from user
    api_key = input("Enter your OpenRouter API Key: ").strip()
    
    if not api_key:
        print("❌ API key cannot be empty!")
        return
    
    # Get model preference
    print("\nSelect model (via OpenRouter):")
    print("1. openai/gpt-4o (Recommended for Arabic invoices - best quality)")
    print("2. openai/gpt-4o-mini (Cost-effective option)")
    print("3. anthropic/claude-3-opus (Alternative high-quality option)")
    print("4. anthropic/claude-3-sonnet (Alternative cost-effective option)")
    
    model_choice = input("\nEnter choice (1-4, default: 1): ").strip()
    
    if model_choice == "2":
        model = "openai/gpt-4o-mini"
    elif model_choice == "3":
        model = "anthropic/claude-3-opus"
    elif model_choice == "4":
        model = "anthropic/claude-3-sonnet"
    else:
        model = "openai/gpt-4o"
    
    # Create .env file content
    env_content = f"""# OpenRouter API Key (required for Information Extraction Agent)
# Get your key from: https://openrouter.ai
# OpenRouter provides access to GPT-4o, Claude, and other models
OPENROUTER_API_KEY={api_key}

# Optional: Specify model (default: openai/gpt-4o-mini, recommended for Arabic: openai/gpt-4o)
# Format: provider/model-name (e.g., openai/gpt-4o, anthropic/claude-3-opus)
OPENROUTER_MODEL={model}
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print(f"   📝 API Key: {'*' * (len(api_key) - 4)}{api_key[-4:]}")
        print(f"   🤖 Model: {model}")
        print(f"\n📁 File location: {env_file.absolute()}")
        print("\n⚠️  Remember: .env file is in .gitignore and will NOT be committed to git.")
        print("\n💡 OpenRouter Dashboard: https://openrouter.ai/keys")
        
    except Exception as e:
        print(f"\n❌ Error creating .env file: {e}")


if __name__ == "__main__":
    create_env_file()
