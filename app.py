import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

# 🎨 Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    /* Setup card */
    .setup-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin: 2rem 0;
    }
    
    .setup-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Status indicators */
    .status-badge {
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.5rem;
        display: inline-block;
        animation: fadeIn 0.5s ease-in;
    }
    
    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    /* Chat container */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        min-height: 400px;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        text-align: center;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Database selection */
    .db-option {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .db-option:hover {
        border-color: #667eea;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.15);
    }
    
    .db-option.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page Configuration
st.set_page_config(
    page_title="SQL Chat Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎯 Main Header
st.markdown("""
<div class="main-header fade-in">
    <div class="main-title"> SQL Chat Intelligence</div>
    <div class="main-subtitle">Chat with your databases using natural language</div>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# 🔧 Setup Section (Always visible until complete)
if not st.session_state.setup_complete:
    
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔑 API Configuration")
        api_key = st.text_input(
            "Groq API Key",
            type="password",
            placeholder="Enter your Groq API key here...",
            help="Get your free API key from console.groq.com"
        )
        
        if api_key:
            st.markdown('<span class="status-badge status-success">✅ API Key Set</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">⚠️ API Key Required</span>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🗄️ Database Selection")
        db_choice = st.radio(
            "",
            ["SQLite (Local student.db)", "MySQL (Remote)"],
            help="Choose your database type"
        )
        
        if db_choice == "SQLite (Local student.db)":
            db_path = Path(__file__).parent / "student.db"
            if db_path.exists():
                st.markdown('<span class="status-badge status-success">✅ Database Found</span>', unsafe_allow_html=True)
                db_ready = True
            else:
                st.markdown('<span class="status-badge status-error">❌ student.db not found</span>', unsafe_allow_html=True)
                db_ready = False
        else:
            st.markdown("##### MySQL Connection")
            mysql_host = st.text_input("Host", placeholder="localhost")
            mysql_user = st.text_input("Username", placeholder="root")
            mysql_password = st.text_input("Password", type="password")
            mysql_db = st.text_input("Database", placeholder="database_name")
            
            if all([mysql_host, mysql_user, mysql_password, mysql_db]):
                st.markdown('<span class="status-badge status-success">✅ Configuration Complete</span>', unsafe_allow_html=True)
                db_ready = True
            else:
                st.markdown('<span class="status-badge status-warning">⚠️ Fill all fields</span>', unsafe_allow_html=True)
                db_ready = False
    
    # Setup completion
    if api_key and db_ready:
        if st.button("🚀 Start Chatting", type="primary"):
            st.session_state.setup_complete = True
            st.session_state.api_key = api_key
            st.session_state.db_choice = db_choice
            if db_choice == "MySQL (Remote)":
                st.session_state.mysql_config = {
                    'host': mysql_host,
                    'user': mysql_user, 
                    'password': mysql_password,
                    'database': mysql_db
                }
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your SQL assistant. I'm ready to help you explore your database. What would you like to know? 🚀"}
            ]
            st.rerun()
    else:
        st.markdown("""
        <div class="info-box">
            📋 Please complete the setup above to start chatting with your database
        </div>
        """, unsafe_allow_html=True)

# 💬 Chat Section (Only show when setup is complete)
else:
    # Show success message
    st.markdown("""
    <div class="success-box fade-in">
        ✅ Setup Complete! You can now chat with your database
    </div>
    """, unsafe_allow_html=True)
    
    # Settings in sidebar for advanced users
    with st.sidebar:
        st.markdown("### ⚙️ Advanced Settings")
        model_options = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
        selected_model = st.selectbox("🤖 AI Model", model_options)
        temperature = st.slider("🌡️ Creativity", 0.0, 1.0, 0.1)
        
        st.markdown("---")
        if st.button("🔄 Reset Setup"):
            st.session_state.setup_complete = False
            st.session_state.messages = []
            st.rerun()
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm your SQL assistant. What would you like to know? 🚀"}
            ]
            st.rerun()
    
    # Initialize LLM
    try:
        llm = ChatGroq(
            groq_api_key=st.session_state.api_key,
            model_name=selected_model,
            streaming=True,
            temperature=temperature
        )
    except Exception as e:
        st.error(f"❌ Error initializing AI: {str(e)}")
        st.stop()
    
    # Configure database
    @st.cache_resource(ttl="2h")
    def configure_db(db_choice, mysql_config=None):
        if db_choice == "SQLite (Local student.db)":
            dbfilepath = (Path(__file__).parent / "student.db").absolute()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        else:
            return SQLDatabase(create_engine(
                f"mysql+mysqlconnector://{mysql_config['user']}:{mysql_config['password']}@{mysql_config['host']}/{mysql_config['database']}"
            ))
    
    try:
        if st.session_state.db_choice == "SQLite (Local student.db)":
            db = configure_db(st.session_state.db_choice)
        else:
            db = configure_db(st.session_state.db_choice, st.session_state.mysql_config)
        
        # Create agent
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )
        
    except Exception as e:
        st.error(f"❌ Database connection error: {str(e)}")
        st.stop()
    
    # Chat interface
    st.markdown('<div class="chat-container fade-in">', unsafe_allow_html=True)
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input
    if user_query := st.chat_input("💬 Ask me anything about your database..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Analyzing your query..."):
                try:
                    streamlit_callback = StreamlitCallbackHandler(st.container())
                    response = agent.run(user_query, callbacks=[streamlit_callback])
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)
                except Exception as e:
                    error_message = f"❌ Sorry, I encountered an error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    st.markdown('</div>', unsafe_allow_html=True)

# 🎨 Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem; font-weight: 500;">
   BY AKSHIT CHAUDHARY
</div>
""", unsafe_allow_html=True)