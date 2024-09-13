import os
import streamlit as st
from streamlit_feedback import streamlit_feedback
import boto3
import botocore
from langchain.llms import Bedrock
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import uuid
import bedrock

# Load environment variables
load_dotenv()

# Configure Bedrock client
profile = os.getenv('profile_name')
config = botocore.config.Config(connect_timeout=120, read_timeout=120)
bedrock_runtime = boto3.client('bedrock-runtime', 'us-east-1', endpoint_url='https://bedrock-runtime.us-east-1.amazonaws.com', config=config)

chat_llm = Bedrock(model_id="anthropic.claude-v2", client=bedrock_runtime, credentials_profile_name=profile)
chat_llm.model_kwargs = {"temperature": 0.5}


# Define the prompt template
prompt_template = """System: You are a knowledgeable and helpful assistant providing detailed responses based on TravelAirline content available on TravelAirline.com. Your responses should be friendly, informative, and conversational. Please ensure that the information is accurate and relevant to the user's query. Additionally, at the end of each response, include at least 3 references in the "References" section, with the reference titles and URLs where the information was sourced.

Current conversation:
{history}

User: {input}
Bot:"""

# Initialize the prompt
PROMPT = PromptTemplate(
    input_variables=["history", "input"],
    template=prompt_template
)

USER_ICON = "user-icon.png"
AI_ICON = "ai-icon.png"

def bedrock_chain():
    memory = ConversationBufferMemory(human_prefix="User", ai_prefix="Bot")
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=chat_llm,
        verbose=True,
        memory=memory,
    )

    return conversation

def run_chain(chain, prompt):
    num_tokens = chain.llm.get_num_tokens(prompt)
    return chain({"input": prompt}), num_tokens


def clear_memory(chain):
    return chain.memory.clear()


def get_kb_chatbot_response(query, kbresponse):
    try:
        # Initialize the prompt
        PROMPT = PromptTemplate(
        input_variables=["history", "input"],
        template=kbresponse
        )
        prompt = PROMPT.format(history=kbresponse, input=query)
        response = chat_llm(prompt=prompt)
        st.write("🤖 AI Response:", response)  # Debug log with AI icon

        # Check if response has completions and if it contains valid data
        if response and isinstance(response, dict) and 'completions' in response:
            completions = response['completions']
            if completions and len(completions) > 0:
                completion_data = completions[0]
                if 'data' in completion_data and 'text' in completion_data['data']:
                    return completion_data['data']['text']
        
        return "No response received from the model."
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "An error occurred while fetching the response."

# Function to get chatbot response
def get_chatbot_response(history, query):
    try:
        prompt = PROMPT.format(history=history, input=query)
        response = chat_llm(prompt=prompt)
        st.write("Response:", response)  # Debug log with AI icon

        # Check if response has completions and if it contains valid data
        if response and isinstance(response, dict) and 'completions' in response:
            completions = response['completions']
            if completions and len(completions) > 0:
                completion_data = completions[0]
                if 'data' in completion_data and 'text' in completion_data['data']:
                    return completion_data['data']['text']
        
        return ""
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return "An error occurred while fetching the response."

# Function to simulate search results
def get_simulated_search_results(query):
    search_query = f"List the top 20 URLs with descriptions where similar answers can be found for the query: {query}"
    return get_chatbot_response("", search_query)  # No history needed for search results

# Function to display feedback buttons
def feedback_buttons():
    container = st.container()
    with container:
        col1, col2 , col3= st.columns([1, 1, 8])
        with col1:
            st.button("👍", key="thumbs_up")
        with col2:
            st.button("👎", key="thumbs_down")
        with col3:
            st.write("")


# Streamlit UI
def main():
    # Page configuration
    st.set_page_config(page_title="TravelAirline Search Engine", page_icon="🤖", layout="wide")

    if "llm_chain" not in st.session_state:
        st.session_state["llm_app"] = bedrock
        st.session_state["llm_chain"] = bedrock.bedrock_chain()

    if "questions" not in st.session_state:
        st.session_state.questions = []

    if "answers" not in st.session_state:
        st.session_state.answers = []

    if "input" not in st.session_state:
        st.session_state.input = ""

    # Session state to store questions and conversation history
    if 'questions' not in st.session_state:
        st.session_state['questions'] = []
    if 'history' not in st.session_state:
        st.session_state['history'] = ""

    # Custom CSS for styling
    st.markdown("""
        <style>
            body {
                background-color: #f5f5f5;
                color: #333;
                font-family: 'Arial', sans-serif;
            }
            .main {
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
            }
            .stTextInput input {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                width: 100%;
                font-size: 16px;
            }
            .stButton button {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                cursor: pointer;
                font-size: 16px;
                margin-top: 20px;
                float: right;
            }
            .stButton button:hover {
                background-color: #45a049;
            }
            .stSpinner {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                text-align: center;
                color: #333;
            }
            .stSidebar .css-1d391kg {
                background-color: #1f3b73 !important;
                border: .0625rem solid #282f43;
                color: white;
            }
            .stSidebar .css-1d391kg .css-1d391kg {
                background-color: #1f3b73 !important;
            }
            .response-box {
                background-color: #e8f4f8;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.05);
                font-size: 16px;
                line-height: 1.6;
                border: 1px solid #ccc;
            }
            
            .search-box {
                background-color: #e8f4f8;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.05);
                border: 1px solid #ccc;
            }
            #chatbot-response {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
                font-size: 16px;
                line-height: 1.6;
}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>TravelAirline Search Bot</h1>", unsafe_allow_html=True)
    st.markdown("<h3>I am your travel chatbot</h3>", unsafe_allow_html=True)

    # Input and button in a centered layout
    user_query = st.text_input("Enter your question:", placeholder="Type your question here..." )

    # Sidebar for displaying previously asked questions
    st.sidebar.title("Previously Asked Questions")
    st.sidebar.write("<div class='sidebar-content'>", unsafe_allow_html=True)
    for question in st.session_state['questions']:
        st.sidebar.write(question)
    st.sidebar.write("</div>", unsafe_allow_html=True)

    if st.button("Submit"):
        if user_query:
            with st.spinner("Fetching response..."):
                try:
                    # Save the question to session state
                    st.image(AI_ICON)
                    st.session_state.questions.append(user_query)
                    st.session_state.history += f"\nUser: {user_query}\nBot:"

                    # Get chatbot response
                    #st.markdown("<h2>Chatbot Response</h2>", unsafe_allow_html=True)
                    #st.image(AI_ICON)
                    chatbot_response = get_chatbot_response(st.session_state.history, user_query)
                    try:
                        if chatbot_response and chatbot_response != "No response received from the model.":
                            #st.session_state.history += f" {chatbot_response}"
                            with st.container():
                                #st.markdown(f'<h1 style="color:#33ff33;font-size:24px;">Hello</h1>', unsafe_allow_html=True)
                                #st.info(chatbot_response)
                                st.chat_message("assistant", avatar="👾").write_stream( chatbot_response )
                                #st.write_stream(chatbot_response)
                                
                        else:
                            with st.container():
                                st.markdown("")
                    finally:
                        # Code in the finally block
                        streamlit_feedback(feedback_type="thumbs", align="flex-start", key="feedback")

                    # Get simulated search results
                    st.markdown("<h2 class='search-box'>Search Results</h2>", unsafe_allow_html=True)
                    search_results = get_simulated_search_results(user_query)
                    if search_results and search_results != "No response received from the model.":
                        col1, col2 = st.columns([1, 12])
                        with col1:
                            st.image(AI_ICON, use_column_width="always")
                        with col2:
                           st.info(search_results)
                        #st.info(search_results)
                    else:
                        st.markdown("")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.error("Please provide a query.")
            

if __name__ == "__main__":
    main()
