import os
import streamlit as st
import traceback
from dotenv import load_dotenv, find_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain 

load_dotenv(find_dotenv())

DB_FAISS_PATH = "knowledge_base/db_faiss"

@st.cache_resource
def load_vectorstore():
    embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)
    return db

def set_prompt(custom_prompt_template):
    return PromptTemplate(template=custom_prompt_template, input_variables=["chat_history", "context", "question"])

def main():
    st.set_page_config(
        page_title='Jupiter Chatbot',
        page_icon='assets\Frame-10-1.png',
    )

    st.markdown("<h1 style='text-align: center; color: #FC7A69; font-size: 3em;'>Welcome to Jupiter!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5em;'>1-app for everything money</p>", unsafe_allow_html=True)
    st.write("-----")
    st.markdown("<p style='text-align: center;'>The future of financial wellness starts here</p>", unsafe_allow_html=True)


    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True      
        )

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    prompt = st.chat_input("Ask your question here...")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        CUSTOM_PROMPT_TEMPLATE = """
        You are a smart, friendly, and highly reliable AI Assistant for Jupiter — a fintech company that helps users manage their money.
        Your task is to answer customer queries strictly and only related to Jupiter’s official products, services, features, and policies.
        Provide comprehensive, detailed, and helpful answers. Explain concepts clearly and thoroughly.
        Instructions:
        Do NOT mention, refer to, or compare any other company, website, product, service, book, or tool.
        Do NOT hallucinate or make up any information. Only respond with facts supported by the provided context or user input.
        If you don’t know the answer, respond with: "I'm not sure about that. Please contact our customer support team at +080-44353535."
        Do NOT make assumptions about the user's intent. If unclear, ask them to clarify.
        Do NOT introduce topics the user did not ask about.
        Include links to relevant resources from the official Jupiter website.
        Only include working links and resources from the official Jupiter website. Never include incorrect or placeholder links.
        If you are mentioning organisation names, use "Jupiter" instead of "Jupiter Money" or "Jupiter.Money".
        Tone:
        Be warm, helpful, respectful, informative, detailed, comprehensive and explain properly every information.
        Thank the user for using Jupiter.Money.
        Promote Jupiter's value and reliability whenever relevant.
        If the user just greets or introduces themselves, greet back politely and ask how you can help — offer him some information to check.
        Do not greet again and again.

        Chat History: 
        {chat_history}
        Context: {context}  
        Question: {question}
        """

        GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


        try:
            vectorstore = load_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")
                return
            
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=ChatGroq(
                    model_name="meta-llama/llama-4-maverick-17b-128e-instruct",
                    temperature=0.5,
                    groq_api_key=GROQ_API_KEY
                ),
                retriever=vectorstore.as_retriever(search_kwargs={'k': 4}),
                memory=st.session_state.memory, 
                chain_type="stuff",
                combine_docs_chain_kwargs={"prompt": set_prompt(CUSTOM_PROMPT_TEMPLATE)}
            )

            with st.spinner("Thinking..."):
                response = qa_chain.invoke({"question": prompt})

            result = response["answer"] 
            st.chat_message('assistant').markdown(result)
            st.session_state.messages.append({'role': 'assistant', 'content': result})

        except Exception as e:
            st.error("An error occurred:")
            st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
