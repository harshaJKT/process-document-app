import httpx
import os
import re

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
TOGETHER_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    raise RuntimeError("Missing Together API Key. Set TOGETHER_API_KEY environment variable.")

async def send_request_to_together(prompt: str, temperature: float = 0.3) -> str:
    """Send a request to Together AI and return response content."""
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
        "temperature": temperature,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(TOGETHER_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            raise RuntimeError(f"Together AI call failed: {e}")

async def generate_keywords_and_summary(text: str) -> tuple[str, str]:
    """Call Together AI to get keywords and summary from a chunk."""
    prompt = f"""
Extract 5 to 10 keywords from this text and summarize it in one sentence.
Give the keywords in a comma-separated format and the summary as a single sentence.
eg:
Keywords: keyword1, keyword2, keyword3  
Summary: This is a summarized sentence.

TEXT:
{text}
"""
    output = await send_request_to_together(prompt)
    keywords, summary = parse_keywords_and_summary(output)
    return keywords, summary

def parse_keywords_and_summary(output: str) -> tuple[str, str]:
    """Parse Together AI response to extract keywords and summary."""
    output = output.replace("\n", " ").strip()

    # extract keywords
    keyword_match = re.search(r"Keywords:\s*(.+?)(?:\n|Summary|$)", output, re.IGNORECASE)
    keywords = keyword_match.group(1).strip() if keyword_match else ""

    # extract summary
    summary_match = re.search(r"(Summary|Summarized sentence):\s*(.+)", output, re.IGNORECASE)
    summary = summary_match.group(2).strip() if summary_match else ""

    return keywords, summary

async def query_together_ai(context: str, query: str) -> str:
    """Ask Together AI a question based on context and return the answer only."""
    prompt = f"""
Given the following document content:
{context}

Answer this question based on the content only and just return the answer related to the question:
{query}
"""
    return await send_request_to_together(prompt, temperature=0.2)
