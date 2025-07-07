import ollama
import ast

def get_question(prompt,question):
    return prompt.format(question = question)


def get_summary_from_ollama(paragraph:str,model='llama3.2:1b')->str:
    prompt = """
            Summarize the following paragraph as briefly as possible :

            "{question}"
    """
    question = get_question(prompt,question = paragraph)
    response = ollama.chat(
        model = model,
        messages=[
            {'role':'user' , 'content':question}
        ]
    )


    return response["message"]["content"]

def get_keywords_from_ollama(paragraph:str,model='llama3.2:1b')->str:
    prompt = """
        Extract the keywords from the following paragraph. Do not leave out anything important.

        Return only a JSON array of strings.
        Do not include any explanation, code block, or extra text.
        Example: ["keyword1", "keyword2", "another keyword"]

        Text:
        "{question}"
        """
    question = get_question(prompt,question = paragraph)
    response = ollama.chat(
        model = model,
        messages=[
            {'role':'user' , 'content':question}
        ]
    )

    return ast.literal_eval(response["message"]["content"])

def get_answer_from_para(paragraph:str,question:str,model = 'llama3.2:1b')->str:

    prompt = """
        You are a helpful AI assistant. Read the paragraph below and answer the following question based only on the information in the paragraph and dont include anything form outside the para.

        Paragraph:
        {paragraph}

        Question:
        {question}

        Answer:"""

    response = ollama.chat(
        model = 'llama3.2:1b',
        messages=[
            {
                'role':'user',
                'content':prompt.format(paragraph = paragraph,question=question)
            }
        ]
    )

    return response['message']['content']