# SQL Chat Assistant 🤖

An interactive SQL database chat application built with Streamlit and LangChain that allows users to query databases using natural language. The application supports both SQLite and MySQL databases and features interactive visualizations of query results.

## 🌟 Features

- **Natural Language Queries**: Convert plain English questions into SQL queries
- **Multiple Database Support**: 
  - SQLite
  - MySQL
- **Database Schema Viewer**
- **Chat History Management**
- **Export Functionality**
- **Real-time Query Processing**

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sql-chat-assistant
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install streamlit langchain langchain-groq python-dotenv sqlalchemy plotly pandas mysql-connector-python
```

3. Set up your environment variables:
Create a `.env` file in the project root and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## 🚀 Usage

1. First, create the sample SQLite database (if using SQLite):
```bash
python sqlite.py
```

2. Run the application:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## 📁 Project Structure

```
sql-chat-assistant/
├── app.py              # Main application file
├── sqlite.py           # SQLite database setup script
├── requirements.txt    # Project dependencies
├── student.db         # SQLite database (created by sqlite.py)
└── README.md          # Project documentation
```

## 🔧 Configuration

### SQLite Configuration
- No additional configuration needed
- Sample database will be created automatically by running `sqlite.py`

### MySQL Configuration
Required fields in the application:
- Host
- Username
- Password
- Database name
- Port (optional, defaults to 3306)

## 🛡️ Security Notes

- Database credentials are handled securely
- API keys are stored in environment variables
- Passwords are masked in the interface
- Read-only database connections are used by default


## 🙏 Acknowledgments

- Streamlit for the awesome web framework
- LangChain for the language model integration
- Groq for providing the language model API
- Plotly for interactive visualizations

## 📫 Support

For support and questions:
- Create an issue in the repository
- Check the [Streamlit documentation](https://docs.streamlit.io/)
- Refer to the [LangChain documentation](https://python.langchain.com/docs/get_started/introduction)