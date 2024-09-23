from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def get_model(model_name:str) -> OllamaLLM:
    return OllamaLLM(model=model_name)

#function for prompting with context
def prompt_with_context(model:OllamaLLM, message:str, context:list):
    
    template = """
    Please follow these steps:
    1. This is the conversations context: {context} .\n It is a list of previous messages between me (user) and you (assistant). 
    The first element in the list is the very first message in the conversation and the second is the response from you etc. Ignore the context
    if the list is empty.
    2. Respond to the following message: {message}.
    3. Do not mention the conversational context in your response. Thank you!
    """
    
    #create template
    prompt = ChatPromptTemplate.from_template(template)
    
    #langchain syntax: first complete the template, then send it to the model.
    chain = prompt | model
    
    #invoke the chain, passing in our prompt with the context (which in turn is passed to the template)
    result = chain.invoke({"message":message, "context":context})
    
    return result


if __name__=="__main__":
    model = get_model("llama3.1")
    print(prompt_with_context(model, "Hello world!", context=[]))