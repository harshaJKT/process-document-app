import json, asyncio, ollama
from typing import Tuple, List

SUMMARY_PROMPT = """
You are a helpful assistant.
Provide a concise 20–30‑word summary of the following text.

<text>
{chunk}
"""

KEYWORDS_PROMPT = """
You are a helpful assistant.
Return 3‑6 concise keywords for the text below as a **single comma‑separated line**.

<text>
{chunk}
"""

def _sync_summary(chunk: str):
    """returns summary string."""
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": SUMMARY_PROMPT.format(chunk=chunk)}],
        stream=False,
    )
    return res["message"]["content"].strip()

def _sync_keywords(chunk: str):
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": KEYWORDS_PROMPT.format(chunk=chunk)}],
        stream=False,
    )
    return res["message"]["content"].strip()

async def generate_summary(chunk: str):
    return await asyncio.to_thread(_sync_summary, chunk)

async def generate_keywords(chunk: str):
    return await asyncio.to_thread(_sync_keywords, chunk)


async def extract_summary_keywords(chunk: str):
    summary_task   = asyncio.create_task(generate_summary(chunk))
    keywords_task  = asyncio.create_task(generate_keywords(chunk))

    summary  = await summary_task
    keywords = await keywords_task
    return summary, keywords



async def extract_query_keywords(query: str) -> List[str]:
    prompt = f"""
    You are a helpful assistant.
    Return 3‑6 keywords for this query as a single comma‑separated line.

    Query: {query}
    """
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    raw = res["message"]["content"].strip()
    
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [k.strip() for k in data]
    except json.JSONDecodeError:
        pass
    return [k.strip() for k in raw.split(",") if k.strip()]


async def query_ollama(*, query: str, context: str) -> str:
    prompt = f"""
    You are an assistant. Use the context below to answer the question.

    Context:
    {context}

    Question: {query}

    Answer in a concise paragraph:
    """
    res = ollama.chat(
        model="llama3.2:1b",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
    )
    return res["message"]["content"].strip()