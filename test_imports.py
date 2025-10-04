import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

try:
    import langchain
    print(f"Langchain imported successfully. Version: {langchain.__version__}")
except ImportError as e:
    print(f"Failed to import langchain: {e}")

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    print("RecursiveCharacterTextSplitter imported successfully")
except ImportError as e:
    print(f"Failed to import RecursiveCharacterTextSplitter: {e}")

try:
    import chromadb
    print(f"Chromadb imported successfully. Version: {chromadb.__version__}")
except ImportError as e:
    print(f"Failed to import chromadb: {e}")