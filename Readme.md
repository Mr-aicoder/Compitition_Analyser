# 📈 Competitor Monitoring Bot
An AI-powered multi-agent system to automate competitive intelligence and deliver strategic insights tailored to your business.

This project implements a sophisticated multi-agent system using LangGraph and Google Gemini. It automates the tedious process of tracking competitor websites, news, and press releases. By leveraging a Retrieval-Augmented Generation (RAG) system, it analyzes findings not in a vacuum, but in the context of your company's specific strategic goals.

## The Problem
In any competitive market, staying on top of what your rivals are doing is critical but incredibly time-consuming. Marketing and product teams spend hours manually checking competitor websites, social media, and news feeds. It's easy to miss a key announcement, misinterpret a strategic shift, or fail to see how a competitor's move impacts your own strategy.

## The Solution
This system acts as a dedicated, automated competitive intelligence analyst that works on-demand. It gathers the latest information, uses a Large Language Model (LLM) to filter signal from noise, and leverages RAG to contextualize every finding against your own business priorities, delivering a concise and relevant briefing.

## Key Features
🤖 Automated Intelligence Gathering: Employs the Tavily Search API to perform real-time web searches for news and to reliably scrape competitor homepages for updates.
🧠 Context-Aware RAG Analysis: The system's "killer feature." It analyzes competitor actions against a knowledge base of your company's strategic priorities, telling you why a certain finding is relevant to you.
✨ AI-Powered Significance Filtering: Uses Google's powerful Gemini model to assess each piece of information, discarding trivial updates and focusing only on strategically important events like product launches, funding rounds, or pricing changes.
📄 Dynamic Digest Generation: Compiles all significant, context-aware findings into a clean, skimmable digest in a web-based dashboard.
🖥️ Interactive Web UI: A user-friendly Streamlit dashboard serves as the control panel for configuring competitors, inputting strategic context, and viewing the results.

## Agentic Architecture
The system is orchestrated by LangGraph, managing a flow between specialized AI agents:

🔍 Gather Intel Agent: This agent is responsible for all external data collection. It uses its gather_competitor_intel tool (powered by Tavily) to search for news and scrape websites for each specified competitor.

🧐 Significance Analyst Agent: This is the core "brain" of the operation. It receives all the raw data from the Gatherer. For each piece of information, it uses the analyze_significance tool to:

Assess if the information is strategically important.
Generate a detailed summary.
If a RAG context is provided, check the finding's relevance against your strategy.
📝 Digest & Alert Agent: The final agent in the workflow. It takes the filtered, analyzed, and contextualized findings from the Analyst Agent and compiles them into a clean, formatted markdown report for display in the Streamlit UI.

## Technology Stack
Orchestration: LangGraph
LLM & Embeddings: Google Gemini & Google AI Platform
Web UI: Streamlit
Real-Time Search & Scraping: Tavily AI
RAG Vector Store: Facebook AI Similarity Search (FAISS)
Core AI Framework: LangChain


## Setup and Installation
Follow these steps to get the project running on your local machine.

1. Clone the Repository (or create files)

bash
git clone <your-repository-url>
cd <your-repository-folder>
2. Create a Virtual Environment (Recommended)

bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. Install Dependencies

bash
pip install -r requirements.txt
4. Set Up API Keys

Create a file named .env in the root of your project directory. You will need API keys from Google and Tavily.

env
# Get from Google AI Studio
GOOGLE_API_KEY="YourSecretGoogleApiKeyGoesHere"

# Get from tavily.com
TAVILY_API_KEY="tvly-YourSecretTavilyApiKeyGoesHere"
How to Run
Once the setup is complete, run the Streamlit application from your terminal:

bash
streamlit run app.py
Your web browser should automatically open with the application running.

## How to Use
Configure Competitors: In the sidebar, enter the names of the companies you want to track, with each name on a new line.
Provide Your Strategy: In the "Your Strategic Context (RAG)" text area, paste information about your company's goals, product roadmap, or current priorities. This is crucial for the context-aware analysis.
Run Analysis: Click the "🚀 Run Analysis" button.
View Results: The agents will begin their work. Once complete, a formatted digest will appear on the main page, detailing all significant findings and their relevance to your strategy.


## Future Roadmap
This project provides a solid foundation. Here are some potential features for future development:

 Automated Scheduling: Integrate with a scheduler (like apscheduler or a cron job) to run the analysis automatically every day.
 Real-Time Alerts: Enhance the Digest & Alert Agent to send critical findings to Slack or Email.
 Historical Database & Trend Analysis: Store findings in a database (e.g., SQLite) to track competitor activity over time and visualize trends on the dashboard.
 Deep Website Monitoring: Expand the scraping capability beyond the homepage to specific pages like /blog, /pricing, or /careers.
 Export to PDF: Add a button to download the final digest as a formatted PDF report.
