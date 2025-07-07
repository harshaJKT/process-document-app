import httpx
import os
import re

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    raise RuntimeError("Missing Together API Key. Please set TOGETHER_API_KEY environment variable.")

async def generate_keywords_and_summary(text: str) -> tuple[str, str]:
    """Call Together AI to get keywords and summary from a chunk."""
    prompt = f"""
Extract 5 keywords from this text and summarize it in one sentence.
TEXT:
{text}
"""
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(TOGETHER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise RuntimeError(f"Together API call failed: {e}")

        output = data['choices'][0]['message']['content'].strip()
        keywords, summary = parse_keywords_and_summary(output)
        return keywords, summary

def parse_keywords_and_summary(output: str) -> tuple[str, str]:
    """Robust parser for Together AI output."""
    keywords = ""
    summary = ""

    output = output.replace("\n", " ").strip()

    # Extract keywords
    keyword_match = re.search(r"Keywords:\s*(.+?)\.", output)
    if keyword_match:
        keywords = keyword_match.group(1).strip()

    # Extract summary
    summary_match = re.search(r"(Summary|Summarized sentence):\s*(.+)", output)
    if summary_match:
        summary = summary_match.group(2).strip()

    if not keywords:
        keywords = "Not Provided"
    if not summary:
        summary = output

    return keywords, summary

async def query_together_ai(context: str, query: str) -> str:
    """Ask Together AI a question based on context."""
    prompt = f"""
Given the following document content:
{context}

Answer this question based on the content only:
{query}
"""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": TOGETHER_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1024,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(TOGETHER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise RuntimeError(f"Together AI Query Failed: {e}")
