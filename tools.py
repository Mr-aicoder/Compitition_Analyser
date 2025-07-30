# tools.py

import os
import json
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from typing import List, Literal, Optional
from prompts import ANALYST_PROMPT
from dotenv import load_dotenv
from tavily import TavilyClient
# RAG Imports
from langchain_core.vectorstores import VectorStoreRetriever

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# --- UPDATED Pydantic Model ---
class AnalysisResult(BaseModel):
    is_significant: bool = Field(description="Set to true if the update is strategically significant, otherwise false.")
    summary: str = Field(description="A very brief, one-sentence headline summary of the update. If not significant, state 'No significant update.'")
    detailed_summary: str = Field(description="A more detailed paragraph (2-4 sentences) explaining the update, its context, and its potential implications. If not significant, this can be an empty string.")
    category: Literal[
        "Product Launch", "Pricing Change", "Partnership", "Funding/Acquisition",
        "Key Hire/Layoffs", "PR/News", "No Significance"
    ] = Field(description="Categorize the update.")
    source_url: Optional[str] = Field(None, description="The source URL of the information.")
    relevance_to_my_strategy: Optional[str] = Field(None, description="Explanation of why this finding is relevant to the user's provided strategic context. Will be populated if RAG context is found.")

# <<< FIX: THE MISSING DOCSTRING HAS BEEN RESTORED HERE. >>>
@tool
def gather_competitor_intel(competitor_name: str) -> List[dict]:
    """
    Gathers intelligence on a competitor by performing a web search for recent news
    and scraping their homepage. Returns a list of documents to be analyzed.
    """
    print(f"--- 🕵️ Gathering intelligence for {competitor_name} ---")
    all_intel = []
    try:
        news_query = f'latest news, press releases, and major updates for "{competitor_name}"'
        print(f"Searching for news with query: {news_query}")
        search_results = tavily_client.search(query=news_query, search_depth="advanced", max_results=7)
        news_intel = [{"source": result['source'], "url": result['url'], "content": result['content']} for result in search_results.get('results', [])]
        if news_intel:
            print(f"Found {len(news_intel)} news articles.")
            all_intel.extend(news_intel)
        else:
            print("No news articles found.")
    except Exception as e:
        print(f"Error during Tavily news search for {competitor_name}: {e}")
    try:
        homepage_url = f"https://www.{competitor_name.lower()}.com"
        print(f"Scraping homepage: {homepage_url}")
        scrape_result = tavily_client.search(query=homepage_url, search_depth="basic")
        if scrape_result.get('results'):
            first_result = scrape_result['results'][0]
            website_intel = {"source": "Website Homepage", "url": first_result['url'], "content": first_result['content']}
            print("Successfully scraped homepage content.")
            all_intel.append(website_intel)
        else:
            print("Could not scrape homepage.")
    except Exception as e:
        print(f"Error during Tavily homepage scrape for {competitor_name}: {e}")
    return all_intel


@tool
def analyze_significance(
    text_content: str,
    source_url: str,
    retriever: Optional[VectorStoreRetriever] = None
) -> dict:
    """
    Uses Google's Gemini model to analyze text for strategic significance.
    If a RAG retriever is provided, it also assesses relevance against that context.
    """
    print(f"Analyzing text from {source_url} with Google Gemini...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, convert_system_message_to_human=True)
    structured_llm = llm.with_structured_output(AnalysisResult)
    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYST_PROMPT),
        ("human", "Here is the text to analyze:\n\n---\n\n{text_content}\n\n---\nSource URL: {source_url}")
    ])
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({"text_content": text_content, "source_url": source_url})
        result_dict = result.dict()
        result_dict['source_url'] = source_url

        if result.is_significant and retriever:
            print(f"--- RAG: Checking relevance for '{result.summary}' ---")
            relevant_docs = retriever.invoke(result.detailed_summary)
            if relevant_docs:
                context = "\n".join([doc.page_content for doc in relevant_docs])
                result_dict['relevance_to_my_strategy'] = f"This is highly relevant because it relates to our strategic focus on: '{context[:300]}...'"
                print("--- RAG: Found relevant strategic context! ---")
            else:
                result_dict['relevance_to_my_strategy'] = "No direct relevance found to our stated strategic priorities."

        return result_dict
    except Exception as e:
        print(f"Error during Gemini analysis for {source_url}: {e}")
        return AnalysisResult(is_significant=False, summary="Analysis failed.", reason=str(e), detailed_summary="", category="No Significance", source_url=source_url).dict()
