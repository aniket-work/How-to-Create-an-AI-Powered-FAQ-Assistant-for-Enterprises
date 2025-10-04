import sys
import importlib

# List of required packages
required_packages = [
    "langchain_groq",
    "langchain_huggingface",
    "chromadb",
    "sentence_transformers",
    "python_dotenv"
]

print("Checking dependencies...")
for package in required_packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package} - OK")
    except ImportError as e:
        print(f"❌ {package} - MISSING ({e})")

print("Dependency check completed.")