import json
import asyncio
import ollama
import config

import json
import re

def safe_json_parse(raw: str) -> dict:
    """
    Safely parse JSON from raw LLM response.
    Handles:
    - Direct JSON parsing
    - Extraction from first '{' to last '}'
    - Appends missing '}'
    - Removes trailing commas before '}' or ']'
    """
    def clean_trailing_commas(json_str: str) -> str:
        return re.sub(r',\s*(?=[}\]])', '', json_str)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1:
            raise ValueError(f"No JSON object found in response: {raw}")

        json_str = raw[start:end + 1] if end != -1 else raw[start:].strip() + "}"
        json_str = clean_trailing_commas(json_str)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse cleaned JSON: {json_str}") from e


async def ask_llm(question: str, context: str, response_format: dict) -> dict:
    """
    General-purpose function to query LLM and get structured response.

    Parameters:
    - question: query or instruction.
    - context: context text for the query.
    - response_format: Dict template describing expected JSON structure.

    Returns:
    - Dict parsed from the LLM response.
    """
    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer the question. "
        "Respond ONLY with a valid JSON matching this format:\n"
        f"{json.dumps(response_format, indent=2)}"
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    try:
        response = await asyncio.to_thread(lambda: ollama.chat(
            model=config.MODEL,
            messages=[{"role": "user", "content": full_prompt}]
        ))
        raw = response["message"]["content"]
        return safe_json_parse(raw)

    except Exception as e:
        raise RuntimeError(f"LLM call failed: {e}")


# async def main():
#     try:
#         response = await ask_llm(
#             question="Generate exactly 5 keywords and a summary.",
#             context=(
#                 "Artificial Intelligence (AI) is a technique in which machines are trained to think and make decisions "
#                 "like humans. AI is being used in every field today—healthcare, finance, education, and even entertainment. "
#                 "Tools like Siri, Alexa, and ChatGPT are examples of AI. AI algorithms analyze data and make smart decisions. "
#                 "It can automate repetitive tasks efficiently. However, there are also challenges such as bias and privacy concerns. "
#                 "Still, the future of AI is promising."
#             ),
#             response_format={
#                 "keywords": ["k1", "k2", "k3", "k4", "k5"],
#                 "summary": "Example summary"
#             }
#         )
#         print("LLM Response:", response)
#     except Exception as e:
#         print("Error:", e)


# if __name__ == "__main__":
#     asyncio.run(main())

