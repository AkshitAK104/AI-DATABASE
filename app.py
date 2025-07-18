import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq

# Streamlit UI config
st.set_page_config(page_title="AI + SQL")
st.title("🧠 Chat with SQL Database")

# Database options
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLite3 database - Student.db",
    "Connect to a MySQL Database"
]
selected_opt = st.sidebar.radio("Choose the DB you want to chat with", options=radio_opt)

# Sidebar input fields based on DB type
if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host", placeholder="localhost")
    mysql_user = st.sidebar.text_input("MySQL User", placeholder="root")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database Name", placeholder="student")
else:
    db_uri = LOCALDB
    mysql_host = mysql_user = mysql_password = mysql_db = None

# Groq API key
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Validation
if not api_key:
    st.info("Please enter your Groq API key to continue.")
    st.stop()

# Initialize Groq LLM
llm = ChatGroq(api_key=api_key, model="Llama3-8b-8192", streaming=True)

# Cache DB connection
@st.cache_resource(ttl="2h")
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LOCALDB:
        db_path = Path("Student.db")
        if not db_path.exists():
            st.error("Student.db not found in this folder. Please place it in the working directory.")
            st.stop()
        conn_str = f"sqlite:///{db_path}"
    elif db_uri == MYSQL:
        if not all([mysql_host, mysql_user, mysql_password, mysql_db]):
            st.error("Please provide all required MySQL credentials.")
            st.stop()
        conn_str = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"
    else:
        st.error("Unknown database option selected.")
        st.stop()

    engine = create_engine(conn_str)
    return SQLDatabase(engine)

# Connect to DB
db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)

# Initialize SQL agent
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Chat interface
prompt = st.chat_input("Ask your SQL database a question:")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container())
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})
        st.write(response["output"])
