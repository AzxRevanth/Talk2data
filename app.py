import streamlit as st
import os
import plotly


st.set_page_config(page_title="Talk2Data", page_icon=":robot")

st.markdown(
    "<h1 style='text-align: center;'>Talk2Data</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<h3 style='text-align: center;'>Your Enterprise AI Assistant</h3>",
    unsafe_allow_html=True,
)

mode = st.sidebar.radio(
    "LLM Mode",
    options=["Local (Ollama)", "OpenAI"],
    index=0
)

# Set environment variables before importing main
if mode == "OpenAI":
    os.environ["USE_LOCAL_LLM"] = "false"

    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password"
    )

    if not openai_api_key or not openai_api_key.startswith("sk-"):
        st.warning("Please enter a valid OpenAI API key to continue.")
        st.stop()

    os.environ["OPENAI_API_KEY"] = openai_api_key

else:
    os.environ["USE_LOCAL_LLM"] = "true"
    st.sidebar.success("Running in local mode using Ollama")

# Import after setting environment variables
try:
    from main import answer_query
except Exception as e:
    st.error(f"Error loading application: {e}")
    st.stop()

if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
if 'agent_response' not in st.session_state:
    st.session_state['agent_response'] = []

for user_msg, agent_msg in zip(
    st.session_state.user_input,
    st.session_state.agent_response
):
    with st.chat_message("user"):
        st.write(user_msg)
    with st.chat_message("assistant"):
        st.write(agent_msg)

def get_text():
    input_text = st.chat_input("You: ", key="input")
    return input_text

query = get_text()

if query:
    st.session_state.user_input.append(query)

    with st.chat_message("user"):
        st.write(query)
    
    with st.spinner("Thinking..."):
        try:
            response = answer_query(query)
        except Exception as e:
            response = f"Error processing query: {e}"
    
    st.session_state.agent_response.append(response)
    with st.chat_message("assistant"):
        if isinstance(response, dict):
            if response.get("type") == "image":
                st.image(response["path"], use_column_width=True)
            
            elif response.get("type") == "plot":
                st.plotly_chart(response["figure"], use_container_width=True)
        
        elif isinstance(response, dict):
            st.write(response["content"])
        else:
            st.write(response)