import ollama
import config
import json

def ask_llm(question: str, context: str, response_format: dict) -> dict:
    """
    General-purpose function to query LLM and get structured response.

    Parameters:
    - question: The question or instruction.
    - context: Context string (chunk or concatenated text).
    - response_format: A dict template indicating the expected format of response.

    Returns:
    - A dictionary parsed from the LLM response in the given format.
    """

    # Create system prompt to instruct model to output response in JSON matching the format
    system_prompt = (
        "You are a helpful assistant. Use the provided context to answer the question. "
        "Return your response strictly as valid JSON in this format:\n"
        f"{json.dumps(response_format, indent=2)}"
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    response = ollama.chat(
        model=config.MODEL,
        messages=[
            {
                "role": "user",
                "content": full_prompt
            }
        ]
    )

    raw = response["message"]["content"]

    try:
        # Try to parse response as JSON
        return json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract and correct malformed JSON if needed
        try:
            json_str = raw[raw.index("{"):raw.rindex("}")+1]
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"LLM returned invalid JSON: {raw}") from e


# response_answer1=ask_llm(
#     question="Generate exactly 5 keywords and a summary.",
#     context="""Artificial Intelligence (AI) is a technique in which machines are trained to think and make decisions like humans. AI is being used in every field today—healthcare, finance, education, and even entertainment. Tools like Siri, Alexa, and ChatGPT are examples of AI. AI algorithms analyze data and make smart decisions. It can automate repetitive tasks efficiently. However, there are also challenges associated with AI, such as bias and privacy concerns. Still, the future of AI is quite promising and it continues to evolve rapidly, transforming the way we live and work.""",
#     response_format={
#         "keywords": ["k1", "k2", "k3"],
#         "summary": "example sentence"
#     }
# )

# response_answer2=ask_llm(
#     question="Generate exactly 3 to 5 keywords from the given question only. Do not add something else other than the words in the question.",
#     context="""How is Artificial Intelligence (AI) being used in various fields, and what are some challenges associated with it?""",
#     response_format={
#         "keywords": ["k1","k2","k3"]
#     }
# )

# response_answer3=ask_llm(
#     question="""How is Artificial Intelligence (AI) being used in various fields, and what are some challenges associated with it?""",
#     context="""AI stands for Artificial Intelligence. It means creating machines that can think and act like humans. AI is used in voice assistants like Siri and Alexa, helping users with tasks using voice commands. AI helps doctors detect diseases early by analyzing medical reports and scans. Smart learning apps use AI to personalize study plans based on student performance. AI can sometimes be biased or make wrong decisions if trained on bad data.""",
#     response_format={
#         "answer": "The document approval process involves..."
#     }
# )


# print(response_answer1)
# print(response_answer2)
# print(response_answer3)

