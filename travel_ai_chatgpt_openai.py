# importing langchain chat models and langchain messages modules
from langchain.chat_models import ChatOpenAI
from langchain.schema import(
    SystemMessage,
    HumanMessage,
    AIMessage
)

# importing streamlit chat module
import streamlit as st
from streamlit_chat import message

# loading the OpenAI api key from .env (OPENAI_API_KEY="sk-********")
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

#  configuring the default settings of the chatbot page.
st.set_page_config(
    page_title='Air Travel Assistant',
    page_icon=''
)

# displaing text in subheader formatting.
st.subheader('Air Travel Chatbot')

# defining gpt-3.5-turb model for OpenAI Chat large language models 
chat = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.5)

# creating the messages (chat history) in the Streamlit session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# creating the sidebar
with st.sidebar:
    # streamlit text input widget for the system message (role)
    system_message = st.text_input(label='System role')
    # streamlit text input widget for the user message
    user_prompt = st.text_input(label='Send a message')

    if system_message:
        if not any(isinstance(x, SystemMessage) for x in st.session_state.messages):
            st.session_state.messages.append(
                SystemMessage(content=system_message)
                )

    # st.write(st.session_state.messages)

    # if the user entered a question
    if user_prompt:
        st.session_state.messages.append(
            HumanMessage(content=user_prompt)
        )

        with st.spinner('Working on your request ...'):
            # creating the ChatGPT response
            response = chat(st.session_state.messages)

        # adding the response's content to the session state
        st.session_state.messages.append(AIMessage(content=response.content))

# adding a default SystemMessage if the user didn't entered one
if len(st.session_state.messages) >= 1:
    if not isinstance(st.session_state.messages[0], SystemMessage):
        st.session_state.messages.insert(0, SystemMessage(content='You are a helpful assistant.'))

# displaying the messages (chat history)
for i, msg in enumerate(st.session_state.messages[1:]):
    if i % 2 == 0:
        message(msg.content, is_user=True, key=f'{i} + 🤓') # user's question
    else:
        message(msg.content, is_user=False, key=f'{i} +  🤖') # ChatGPT response

