# Migration from OpenAI to Google Gemini

This document summarizes the changes made to migrate the project from using OpenAI APIs to Google Gemini APIs.

## Environment Variables

Updated `.env` file:
- Replaced `OPENAI_API_KEY` with `GOOGLE_GEMINI_API_KEY`

## Dependencies

Updated requirements files to use Google Generative AI libraries:
- Added `google-generativeai>=0.7.0` to auto_audit requirements
- Replaced `langchain-openai` with `langchain-google-genai` in enterprise RAG platform
- Added `google-generativeai>=0.7.0` and `langchain-google-genai>=2.0.0` to main requirements
- Removed `openai` dependencies
- Updated Config Companion dependencies to use Google Generative AI

## Code Changes

### Auto Audit Project
- Replaced OpenAI client with Google Generative AI client
- Updated all agent functions to use `model.generate_content()` instead of `client.chat.completions.create()`
- Changed model from `gpt-4` to `gemini-pro`

### Pipeline Monitor Project
- Replaced OpenAI client with Google Generative AI client
- Updated SummarizerAgent to use `model.generate_content()` instead of `openai.chat.completions.create()`
- Changed model from `gpt-4` to `gemini-pro`

### Enterprise RAG Platform
- Replaced `OpenAIEmbeddings` with `GoogleGenerativeAIEmbeddings`
- Replaced `ChatOpenAI` with `ChatGoogleGenerativeAI`
- Updated embedding model from `text-embedding-3-large` to `models/embedding-001`
- Updated chat model from `gpt-4o-mini` to `gemini-pro`
- Updated chat model from `gpt-3.5-turbo` to `gemini-pro`

### Config Companion Project
- Replaced `ChatOpenAI` with `ChatGoogleGenerativeAI`
- Updated chat model from `gpt-4o-mini` to `gemini-pro`

## Documentation Updates

- Updated README.md files to reference Google Gemini API key instead of OpenAI API key
- Updated setup instructions to reflect the new API requirements

## Models Used

- **Chat Model**: `gemini-pro`
- **Embedding Model**: `models/embedding-001`

## Next Steps

1. Obtain a Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)
2. Add your API key to the `.env` file
3. Install the updated dependencies with `pip install -r requirements.txt`
4. Test the applications to ensure they work with the new API