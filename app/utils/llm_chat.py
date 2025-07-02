

# """

# // response for keywords in each chunk
# {
#  "keywords": ["k1","k2","k3"],
#  "summary" : "example sentence"
# }

# // response for keyword for query 
# {
#   "keywords" : ["q1","q2"]
# }

# // response for actual query

# string



# //
# response -> 

# ask_llm(question : gen 3 keywords ,context : chunk, response_format : {
#  "keywords": ["k1","k2","k3"],
#  "summary" : "example sentence"
# }
# )

# ask_llm(question : gen 3 keywords ,context : query, response_format : {
#  "keywords": ["k1","k2","k3"]
# }
# )

# ask_llm(question : input_query ,context : concatenated single string of chunks, response_format : {
 
# "answer" : "example answer"

# })


# // general format
# ask_llm(question : string,context : string,response_format : dict)  --> returns the response in mentioned response format

# // go through actual documentation of ollma.chat about how this can be achieved.


# """




