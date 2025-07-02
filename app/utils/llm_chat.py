import ollama
import config
# pass in which jdon format the response should we expect
def ask_llm(query : str,context : str,response_format : dict={"response" : "example content response"}) -> dict:
    prompt = f"""
    Use the following context to answer the question in proper response format of dictionary provided:
    \n\n
    Context:{context}
    \n\n
    Question: {query}
    \n\n
    Response : {response_format}
    """
    
    response = ollama.chat(
        model=config.MODEL,  # Or your preferred model like 'llama3.2:1b'
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return response['message']['content']


res=ask_llm("give 4 very important keywords and a summary in one sentence from the context","""
 
Cricket is the most popular sport in India, often considered a national passion. Introduced during British rule, it has grown into a cultural phenomenon, uniting people across regions and languages. The Indian cricket team has achieved global success, winning World Cups and producing legends like Sachin Tendulkar, MS Dhoni, and Virat Kohli. The Indian Premier League (IPL) further boosted the sport’s popularity, blending entertainment with high-quality cricket. Streets, parks, and open fields across the country often host informal matches, reflecting cricket's deep-rooted presence in everyday life. For many Indians, cricket is more than a sport — it’s a shared emotion.

""",{
   
"keywords" : ["k1","k2"],
"summary" : "summary here"

})
print(type(res))
print(res)