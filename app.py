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
from dotenv import load_dotenv


st.set_page_config(page_title="Enhanced SQL Chat Assistant", page_icon="🤖", layout="wide")

## Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .chat-container {
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .error-message {
        color: red;
        padding: 10px;
        border-radius: 5px;
        background-color: #ffe6e6;
        margin: 10px 0;
    }
    .success-message {
        color: green;
        padding: 10px;
        border-radius: 5px;
        background-color: #e6ffe6;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar with enhanced configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Database Selection with custom styling
    st.subheader("Database Connection")
    db_type = st.selectbox(
        "Select Database Type",
        ["SQLite", "MySQL"],
        help="Choose your database type"
    )
    
    # Database Configuration
    with st.expander("Database Settings", expanded=True):
        if db_type == "MySQL":
            mysql_config = {
                "host": st.text_input("MySQL Host", placeholder="localhost"),
                "user": st.text_input("MySQL User", placeholder="username"),
                "password": st.text_input("MySQL Password", type="password"),
                "database": st.text_input("Database Name", placeholder="mydb"),
                "port": st.text_input("Port (optional)", placeholder="3306", value="3306")
            }
            
            # Test connection button
            if st.button("Test Connection"):
                try:
                    import mysql.connector
                    conn = mysql.connector.connect(**mysql_config)
                    conn.close()
                    st.success("Successfully connected to MySQL!")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
        else:
            st.info("Using SQLite database: student.db")
            
        # Model Configuration
        st.subheader("Model Settings")
        model_name = st.selectbox(
            "Select Model",
            ["Llama3-8b-8192", "Other available models..."]
        )
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            help="Controls creativity of responses"
        )
        
        api_key = st.text_input("Groq API Key", type="password")
        if not api_key:
            st.warning("Please enter your Groq API key")

# Main chat interface
st.title("🤖 Enhanced SQL Chat Assistant")

# Initialize session state for storing conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.last_query = None
    st.session_state.last_sql = None

# Function to configure database
@st.cache_resource(ttl="2h")
def configure_db(db_type, config=None):
    try:
        if db_type == "SQLite":
            dbfilepath = (Path(__file__).parent/"student.db").absolute()
            if not dbfilepath.exists():
                st.error("SQLite database file not found. Please run sqlite.py first to create the database.")
                st.stop()
            creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
            return SQLDatabase(create_engine("sqlite:///", creator=creator))
        elif db_type == "MySQL":
            if not all([config['host'], config['user'], config['password'], config['database']]):
                st.error("Please provide all required MySQL connection details.")
                st.stop()
            connection_string = f"mysql+mysqlconnector://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
            return SQLDatabase(create_engine(connection_string))
    except Exception as e:
        st.error(f"Database configuration error: {str(e)}")
        st.stop()

# Initialize LLM and agent
if api_key:
    try:
        llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model_name,
            temperature=temperature,
            streaming=True
        )
        
        db = configure_db(db_type, mysql_config if db_type == "MySQL" else None)
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
        )

        # Chat interface with enhanced features
        st.markdown("### Chat History")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Show SQL query if available
                    if "sql_query" in message:
                        with st.expander("View SQL Query"):
                            st.code(message["sql_query"], language="sql")

        # Query input with suggestions
        query = st.chat_input(
            placeholder="Ask me anything about your data...",
            key="chat_input"
        )

        if query:
            st.session_state.messages.append({"role": "user", "content": query})
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Execute query and capture SQL
                        response = agent.run(query)
                        
                        # Extract SQL query if present in response
                        sql_query = None
                        if "SQL Query:" in response:
                            sql_query = response.split("SQL Query:")[1].split("\n")[0].strip()
                        
                        # Store response with metadata
                        message = {
                            "role": "assistant",
                            "content": response
                        }
                        
                        if sql_query:
                            message["sql_query"] = sql_query
                        
                        st.session_state.messages.append(message)
                        st.write(response)
                    except Exception as e:
                        st.error(f"Error processing query: {str(e)}")

    except Exception as e:
        st.error(f"Error initializing AI model: {str(e)}")
else:
    st.warning("Please configure your API key in the sidebar.")


with st.sidebar:
    with st.expander("Chat Options"):
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.experimental_rerun()
        
        # Export chat history
        if st.download_button(
            "Download Chat History",
            "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages]),
            "chat_history.txt",
            "text/plain"
        ):
            st.success("Chat history downloaded!")
            
        # Show table schema
        if st.button("Show Database Schema"):
            try:
                if db_type == "SQLite":
                    cursor = sqlite3.connect(str(Path(__file__).parent/"student.db")).cursor()
                    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                else:
                    import mysql.connector
                    conn = mysql.connector.connect(**mysql_config)
                    cursor = conn.cursor()
                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                
                st.write("### Database Schema")
                for table in tables:
                    st.write(f"**Table: {table[0]}**")
                    if db_type == "SQLite":
                        schema = cursor.execute(f"PRAGMA table_info({table[0]})").fetchall()
                        for col in schema:
                            st.write(f"- {col[1]} ({col[2]})")
                    else:
                        cursor.execute(f"DESCRIBE {table[0]}")
                        schema = cursor.fetchall()
                        for col in schema:
                            st.write(f"- {col[0]} ({col[1]})")
            except Exception as e:
                st.error(f"Error fetching schema: {str(e)}")
