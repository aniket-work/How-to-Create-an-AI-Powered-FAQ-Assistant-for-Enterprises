# Google AI API Rate Limit Guide

## Understanding the Error

You're encountering a rate limit error from Google's AI API:

```
Error querying documents: Error embedding content: 429 You exceeded your current quota
```

This means you've hit the free tier limits for the embedding API.

## Rate Limits for Google AI API

### Free Tier Limits (as of current date):
- **Embedding requests**: Limited per day and per minute
- **Generative model requests**: Limited per day and per minute

### Common Rate Limit Metrics:
- `generativelanguage.googleapis.com/embed_content_free_tier_requests`
- `generativelanguage.googleapis.com/generate_content_free_tier_requests`

## Solutions

### 1. Wait for Quota Reset
- Daily quotas typically reset every 24 hours
- You can continue using the service after the reset

### 2. Upgrade to Paid Plan
- Visit [Google AI Studio](https://aistudio.google.com/) to upgrade
- Paid plans offer higher rate limits
- More consistent performance for production use

### 3. Optimize Usage
- Reduce the number of documents you're processing
- Process documents in smaller batches
- Cache embeddings when possible

### 4. Retry Logic
The application now includes retry logic with exponential backoff:
- Automatically waits and retries when rate limits are hit
- Maximum of 3 retry attempts
- Wait time increases with each retry (1s, 2s, 4s)

## Best Practices

### For Document Processing:
1. Process fewer documents at once
2. Use smaller chunk sizes
3. Avoid reprocessing the same documents repeatedly

### For Querying:
1. Limit the number of simultaneous queries
2. Use caching for common queries
3. Consider implementing a queue system for high-volume usage

## Monitoring Usage

To monitor your usage:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to APIs & Services > Dashboard
3. Select the Generative Language API
4. Check the quotas and usage metrics

## Getting Help

For more information on rate limits:
- Visit [Google's Rate Limits Documentation](https://ai.google.dev/gemini-api/docs/rate-limits)
- Contact Google Cloud support for quota increases