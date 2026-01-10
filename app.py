import streamlit as st
import os 

st.set_page_config(page_title="Talk2Data", page_icon=":robot")

st.markdown(
    "<h1 style='text-align: center;'>Talk2Data</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<h3 style='text-align: center;'>Your Enterprise AI Assistant</h3>",
    unsafe_allow_html=True,
)

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
st.sidebar.caption("Please enter your OpenAI API key to proceed.")
if not openai_api_key or not openai_api_key.startswith("sk-"):
    st.warning("Please enter a valid OpenAI API key to proceed.")
    st.stop()

os.environ["OPENAI_API_KEY"] = openai_api_key

from main import answer_query

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
if 'agent_response' not in st.session_state:
    st.session_state['agent_response'] = []

for i in range(len(st.session_state.user_input)):
    with st.chat_message("user"):
        st.write(st.session_state.user_input[i])
    with st.chat_message("agent"):
        st.write(st.session_state.agent_response[i])

def get_text():
    input_text = st.chat_input("You: ", key="input")
    return input_text

query = get_text()

if query:
    st.session_state.query.append(query)

    with st.chat_message("user"):
        st.write(query)
    with st.spinner("Thinking..."):
        response = answer_query(query)
    
    st.session_state.agent_response.append(response)
    with st.chat_message("agent"):
        st.write(response)