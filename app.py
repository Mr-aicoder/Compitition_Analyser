# app.py

import streamlit as st
import json
from dotenv import load_dotenv
from graph import build_graph, CompetitorAnalysisState
import asyncio  # <-- Import asyncio

# RAG Imports
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==============================================================================
# === FIX: Set up an asyncio event loop for the current thread. ===
# This is required by the underlying gRPC-aio library used by Google's client.
# ==============================================================================
try:
    asyncio.get_running_loop()
except RuntimeError:  # 'There is no current event loop...'
    # If there is no current event loop, create one and set it
    asyncio.set_event_loop(asyncio.new_event_loop())

load_dotenv()

st.set_page_config(page_title="Strategic Competitor Bot", page_icon="📈", layout="wide")

st.title("📈 Strategic Competitor Monitoring Bot")
st.markdown("This bot uses RAG to analyze competitor actions based on **your** strategic priorities.")

# --- RAG Helper Function ---
def create_rag_retriever(strategy_text: str):
    if not strategy_text:
        return None
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.create_documents([strategy_text])
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    try:
        vectorstore = FAISS.from_documents(docs, embeddings)
        return vectorstore.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        st.error(f"Failed to create RAG retriever: {e}")
        return None

# --- UI Definition ---
with st.sidebar:
    st.header("Configuration")
    competitor_input = st.text_area(
        "Enter Competitor Names (one per line)",
        "OpenAI\nGoogle\nAnthropic",
        height=100
    )
    
    st.header("Your Strategic Context (RAG)")
    strategy_input = st.text_area(
        "Paste your company's goals, product roadmap, or strategic priorities here.",
        "Our key strategic pillars for this year are: \n1. Expanding into the European market. \n2. Launching a new AI-powered data analytics suite for enterprise customers. \n3. Focusing on improving user retention through community-building features.",
        height=250,
        help="The agent will use this text to determine if a competitor's action is relevant to you."
    )

    if st.button("🚀 Run Analysis", use_container_width=True):
        competitors = [c.strip() for c in competitor_input.strip().split('\n') if c.strip()]
        if not competitors:
            st.error("Please enter at least one competitor name.")
        else:
            st.session_state.competitors = [{"name": name} for name in competitors]
            st.session_state.strategy = strategy_input
            st.session_state.running = True
            st.session_state.result = None

# --- Main App Logic ---
if "running" in st.session_state and st.session_state.running:
    with st.spinner("🤖 Agents at work... Creating RAG context, gathering intel, and analyzing significance..."):
        graph = build_graph()
        
        retriever = create_rag_retriever(st.session_state.strategy)
        
        initial_state: CompetitorAnalysisState = {
            "competitors": st.session_state.competitors,
            "intel_docs": [],
            "retriever": retriever,
            "significant_findings": [],
            "digest": ""
        }
        
        final_state = graph.invoke(initial_state)
        
        st.session_state.result = final_state
        st.session_state.running = False
        st.rerun()

if "result" in st.session_state and st.session_state.result:
    st.subheader("Intelligence Digest")
    st.markdown(st.session_state.result['digest'])
    
    with st.expander("🔬 View Raw Agent Output (for debugging)"):
        def custom_serializer(obj):
            if hasattr(obj, '__class__'):
                return f"<<non-serializable: {obj.__class__.__name__}>>"
            return obj
        # Use st.json directly which is better for complex objects
        st.json(json.loads(json.dumps(st.session_state.result, default=custom_serializer, indent=2)))
else:
    st.info("Configure your competitors and strategic priorities in the sidebar, then click 'Run Analysis'.")
