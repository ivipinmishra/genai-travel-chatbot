!pip install google-cloud-aiplatform --upgrade --user
!pip install langchain --upgrade
!pip install bs4
!pip install docarray
!pip install tiktoken
!pip install streamlit

# import libraries
import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.vectorstores import DocArrayInMemorySearch
import vertexai
from langchain.llms import VertexAI
from langchain.embeddings import VertexAIEmbeddings

PROJECT = "##"
LOCATION = "##"

vertexai.init(project=PROJECT, location=LOCATION)

llm = VertexAI(
    model_name="text-bison@001",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,)
    
embeddings = VertexAIEmbeddings()


def get_text(url):
    # Send a GET request to the URL
    response = requests.get(url)

    # Create a BeautifulSoup object with the HTML content
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the specific element or elements containing the text you want to scrape
    # Here, we'll find all <p> tags and extract their text
    paragraphs = soup.find_all("p")

    # Loop through the paragraphs and print their text
    with open("text\\temp.txt", "w", encoding='utf-8') as file:
        # Loop through the paragraphs and write their text to the file
        for paragraph in paragraphs:
            file.write(paragraph.get_text() + "\n")

@st.cache_resource
def create_langchain_index(input_text):
    print("--indexing---")
    get_text(input_text)
    loader = TextLoader("text\\temp.txt", encoding='utf-8')
    # data = loader.load()

    index = VectorstoreIndexCreator(vectorstore_cls=DocArrayInMemorySearch,embedding=embeddings).from_loaders([loader])
    return index

@st.cache_data
def get_response(input_text,query):
    print(f"--querying---{query}")
    response = index.query(query,llm=llm)
    return response

st.title('GCP Vertex AI based Question and Answering System')


input_text=st.text_input("Provide the link to the webpage...")

summary_response = ""
tweet_response = ""
ln_response = ""
if input_text:
    index = create_langchain_index(input_text)


st.session_state.input_text = ''    
question=st.text_input("Ask a question from the given links ..")
if st.button("Ask"):
        if question:
            index = create_langchain_index(input_text)
            response = get_response(input_text,question)
            st.write(response)
        else:
            st.warning("Please enter a question.")
    