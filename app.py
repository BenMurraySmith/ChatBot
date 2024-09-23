import streamlit as st
from langchain_ollama import OllamaLLM
import llm
from time import sleep

#initialize model
@st.cache_resource
def llm_model(name:str):
    model = llm.get_model(name)
    return model



#generater function returns each word after a short delay to simulate conversation rather 
#than returning a block of text all at once
def typewriting_display(model_response:str):
    for word in model_response.split():
        yield word + " "
        sleep(0.05)
        

#display historical messages at app rerun
def render_history(session_state_key:str):
    
    #keep chat displayed
    if session_state_key in st.session_state:
        for message in st.session_state[session_state_key]:
            with st.chat_message(message["role"]):
                message["message"]
                

def fetch_conversation(session_state_key:str) -> bool:
    if session_state_key in st.session_state:
        return True
    return False


def main():
    
    ## State managers:
    
    #to keep track of how many conversations are on going
    if "conversation_count" not in st.session_state:
        st.session_state.conversation_count = 1
        
    #we want to render some chat buttons to keep track of previous chats
    if "chat_buttons_to_render" not in st.session_state:
        st.session_state.chat_buttons_to_render = []
        
        
    # Initialize key value for the first conversation
    if "current_key" not in st.session_state:
    
        session_state_key = f"convo_{st.session_state.conversation_count}"
        
        #what chat are we currently on
        st.session_state.current_key = session_state_key
        
        #initialize chat history with empty list
        st.session_state[session_state_key] = []
        
        #initialize model. First time this is called, it is cached
        model = llm_model("llama3.1")
        
        
    if "first_prompt" not in st.session_state:
        st.session_state.first_prompt = [{"key":st.session_state.current_key, "is_first":True}]
    
    
    #create chat navigation
    with st.sidebar:
        
        st.title("Let's Chat!")
        """"""
       
        st.info("This chatbot runs on Meta's LLama3.1 8B model, and has a size of 4.7GB. Information about other open-sourced LLM's can be found here https://github.com/ollama/ollama:", icon="ℹ️")
        """"""
        """""" 
        #if button is clicked, run below code
        if st.button("New chat :material/add_Circle:", key="create_new_chat", use_container_width=True):

            #increment count
            st.session_state.conversation_count+=1
            
            # Generate new session key for the new conversation
            session_state_key = f"convo_{st.session_state.conversation_count}"
        
            # Update current key in session state
            st.session_state.current_key = session_state_key
            
            # Create a new list to hold the new conversation data
            st.session_state[session_state_key] = []
            
            #update first prompt session state. when we send the first prompt to this conversation, is_first => False
            st.session_state.first_prompt.append({"key":session_state_key, "is_first":True})
            
        
        if st.session_state.chat_buttons_to_render:
            for chat in st.session_state.chat_buttons_to_render:
                key = chat["chat_to_display"]
                
                #highlights current chat
                button_type= "primary" if key == st.session_state.current_key else "secondary"
                
                
                #render button. If clicked, display that conversations history
                if st.button(key,use_container_width=True,type=button_type, key=f"chat_button_{key}"):
                    
                    #update the current key state to the conversation linked to "key"
                    st.session_state.current_key = key
                    
                    st.rerun()
                    
          
    #grab current key
    current = st.session_state.current_key
      
    #render the chat history
    render_history(current)      
    
    
    #user input bar at the bottom (:= is streamlit syntax - if st.chat_input is not none, store it in prompt). 
    if prompt:= st.chat_input("Enter your prompt", key="input_bar"):
        
        #FIRST PROMPT LOGIC
        
        all_first_prompts = [chat for chat in st.session_state.first_prompt]
        
        #very first prompt logic
        if len(all_first_prompts)==1:
            
            #if first prompt is still True, update state
            if st.session_state.first_prompt[0]["is_first"]:
                
                #render this new chat button
                st.session_state.chat_buttons_to_render.append({"chat_to_display":current})
                
                #update state
                st.session_state.first_prompt[0]["is_first"]=False
        else:
            for convo in st.session_state.first_prompt:
                
                # for any new conversations:
                if convo["is_first"]:
                    
                    #update the render buttons state to show the new button in the sidebar
                    st.session_state.chat_buttons_to_render.append({"chat_to_display":convo["key"]})
                    
                    #reset state
                    convo["is_first"]=False

    
        
        #CALLING LLAMA
        
        model = llm_model("llama3.1")

            
        #display users prompt
        with st.chat_message("user"):
            prompt
            
        #store user's messages in session state key 
        st.session_state[st.session_state.current_key].append({"role":"user", "message":prompt})
        
        #send prompt to LLM, including any context
        with st.spinner(""):
            model_response = llm.prompt_with_context(model, prompt, context=st.session_state[current])
    
        #display LLM response in app with a typewriter effect
        with st.chat_message("assistant"):
            st.write_stream(typewriting_display(model_response))
            
        #store model responses in the same session state key
        st.session_state[st.session_state.current_key].append({"role":"assistant", "message":model_response})
            
        
        st.rerun()
            
            

    
        
if __name__=="__main__":
    # st.session_state
    main()