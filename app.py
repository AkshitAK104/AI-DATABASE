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
import time
import pandas as pd

# 🎨 Custom CSS for modern styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        opacity: 0.9;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Database connection cards */
    .db-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .db-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    .db-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
    }
    
    .db-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    /* Status badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
        display: inline-block;
    }
    
    .status-connected {
        background: #10b981;
        color: white;
    }
    
    .status-disconnected {
        background: #ef4444;
        color: white;
    }
    
    .status-warning {
        background: #f59e0b;
        color: white;
    }
    
    /* Chat styling */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Animation for loading */
    .loading-animation {
        display: inline-block;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 🚀 Page Configuration
st.set_page_config(
    page_title="SQL Chat Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎯 Main Header
st.markdown("""
<div class="main-header">
    <div class="main-title">🧠 SQL Chat Intelligence</div>
    <div class="main-subtitle">Powered by LangChain & Groq AI • Chat with your databases naturally</div>
</div>
""", unsafe_allow_html=True)

# 🔧 Constants
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

# 🎨 Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration Panel")
    st.markdown("---")
    
    # Database Selection
    st.markdown("### 🗄️ Database Selection")
    
    # SQLite Option
    sqlite_selected = st.radio(
        "",
        ["SQLite Database (student.db)", "MySQL Database"],
        key="db_type",
        format_func=lambda x: x
    )
    
    db_type = LOCALDB if sqlite_selected == "SQLite Database (student.db)" else MYSQL
    
    # Show database status
    if db_type == LOCALDB:
        st.markdown("""
        <div class="db-card selected">
            <div class="db-icon">🗃️</div>
            <strong>SQLite Database</strong><br>
            <small>Local student.db file</small><br>
            <span class="status-badge status-connected">Ready to Connect</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if file exists
        db_path = Path(__file__).parent / "student.db"
        if not db_path.exists():
            st.warning("⚠️ student.db not found in current directory")
    else:
        st.markdown("""
        <div class="db-card selected">
            <div class="db-icon">🌐</div>
            <strong>MySQL Database</strong><br>
            <small>Remote connection</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 🔐 MySQL Connection Details")
        mysql_host = st.text_input("🏠 MySQL Host", placeholder="localhost or IP address")
        mysql_user = st.text_input("👤 MySQL User", placeholder="username")
        mysql_password = st.text_input("🔑 MySQL Password", type="password")
        mysql_db = st.text_input("🗄️ Database Name", placeholder="database_name")
        
        # Connection status
        if all([mysql_host, mysql_user, mysql_password, mysql_db]):
            st.markdown('<span class="status-badge status-connected">Configuration Complete</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-warning">Configuration Incomplete</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # API Key Section
    st.markdown("### 🔑 API Configuration")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="Enter your Groq API key",
        help="Get your API key from https://groq.com"
    )
    
    if api_key:
        st.markdown('<span class="status-badge status-connected">API Key Set</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-disconnected">API Key Required</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Additional Options
    st.markdown("### 🎛️ Advanced Options")
    model_options = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
    selected_model = st.selectbox("🤖 AI Model", model_options)
    
    temperature = st.slider("🌡️ Temperature", 0.0, 1.0, 0.1, help="Controls response creativity")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", type="secondary"):
        st.session_state["messages"] = [{"role": "assistant", "content": "Hello! I'm your SQL assistant. How can I help you explore your database today? 🚀"}]
        st.rerun()

# 🔍 Main Content Area
col1, col2 = st.columns([3, 1])

with col2:
    # Quick Stats/Info Panel
    st.markdown("### 📊 Quick Info")
    
    if api_key and (db_type == LOCALDB or all([mysql_host, mysql_user, mysql_password, mysql_db])):
        st.markdown('<div class="success-box">✅ System Ready</div>', unsafe_allow_html=True)
        
        # Show some quick metrics
        st.markdown("""
        <div class="metric-card">
            <strong>🤖 Model:</strong> {}<br>
            <strong>🌡️ Temperature:</strong> {}<br>
            <strong>🗄️ Database:</strong> {}
        </div>
        """.format(
            selected_model,
            temperature,
            "SQLite" if db_type == LOCALDB else "MySQL"
        ), unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">⚙️ Complete setup in sidebar</div>', unsafe_allow_html=True)

with col1:
    # Validation
    if not api_key:
        st.markdown("""
        <div class="info-box">
            🔑 Please enter your Groq API key in the sidebar to get started
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    if db_type == MYSQL and not all([mysql_host, mysql_user, mysql_password, mysql_db]):
        st.markdown("""
        <div class="info-box">
            🗄️ Please complete your MySQL connection details in the sidebar
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Initialize LLM
    try:
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name=selected_model,
            streaming=True,
            temperature=temperature
        )
    except Exception as e:
        st.error(f"❌ Error initializing AI model: {str(e)}")
        st.stop()
    
    # Database Configuration
    @st.cache_resource(ttl="2h")
    def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
        if db_uri == LOCALDB:
            dbfilepath = (Path(__file__).parent / "student.db").absolute()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        elif db_uri == MYSQL:
            return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
    
    # Configure database
    try:
        if db_type == MYSQL:
            db = configure_db(db_type, mysql_host, mysql_user, mysql_password, mysql_db)
        else:
            db = configure_db(db_type)
        
        # Create toolkit and agent
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
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I'm your SQL assistant. How can I help you explore your database today? 🚀"}
        ]
    
    # Display chat history
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input
    if user_query := st.chat_input("💬 Ask me anything about your database..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking..."):
                try:
                    streamlit_callback = StreamlitCallbackHandler(st.container())
                    response = agent.run(user_query, callbacks=[streamlit_callback])
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.write(response)
                except Exception as e:
                    error_message = f"❌ Sorry, I encountered an error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})

# 🎨 Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 1rem;">
    Built with ❤️ using Streamlit & LangChain • Powered by Groq AI
</div>
""", unsafe_allow_html=True)