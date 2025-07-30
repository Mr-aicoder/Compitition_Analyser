# graph.py

from typing import TypedDict, List, Any
from langgraph.graph import StateGraph, END
from tools import gather_competitor_intel, analyze_significance
from langchain_core.vectorstores import VectorStoreRetriever

# --- UPDATED Graph State ---
class CompetitorAnalysisState(TypedDict):
    competitors: List[dict]
    intel_docs: List[dict]
    # This will now hold our RAG retriever object
    retriever: VectorStoreRetriever
    significant_findings: List[dict]
    digest: str

# --- UPDATED Agent Nodes ---
def gather_intel_agent(state: CompetitorAnalysisState) -> dict:
    all_intel_for_all_competitors = []
    for comp in state['competitors']:
        intel = gather_competitor_intel.invoke(comp['name'])
        if intel:
            all_intel_for_all_competitors.extend(intel)
    return {"intel_docs": all_intel_for_all_competitors}

def significance_analyst_agent(state: CompetitorAnalysisState) -> dict:
    print("--- 🧐 Running Significance Analyst Agent (with RAG context)---")
    significant_findings = []
    retriever = state.get('retriever') # Get the retriever from the state
    
    for doc in state.get('intel_docs', []):
        # Pass the retriever to the analysis tool
        analysis_result = analyze_significance.invoke({
            "text_content": doc['content'],
            "source_url": doc['url'],
            "retriever": retriever
        })
        if analysis_result and analysis_result.get('is_significant'):
            significant_findings.append(analysis_result)
            
    return {"significant_findings": significant_findings}

def digest_and_alert_agent(state: CompetitorAnalysisState) -> dict:
    print("--- 📝 Running Digest & Alert Agent ---")
    findings = state.get('significant_findings', [])
    
    if not findings:
        return {"digest": "## Competitor Intelligence Digest\n\n**No significant updates found in this run.**"}

    digest_parts = ["## 🚀 Competitor Intelligence Digest 🚀\n"]
    for finding in findings:
        digest_parts.append(f"### {finding['category']}: {finding['summary']}")
        # Display the new detailed summary and relevance fields
        digest_parts.append(f"**Details:** {finding['detailed_summary']}")
        if finding.get('relevance_to_my_strategy'):
             digest_parts.append(f"**Relevance to You:** {finding['relevance_to_my_strategy']}")
        digest_parts.append(f"**Source:** [{finding['source_url']}]({finding['source_url']})")
        digest_parts.append("---")
        
    return {"digest": "\n\n".join(digest_parts)}

# --- Graph Definition (Unchanged) ---
def build_graph():
    workflow = StateGraph(CompetitorAnalysisState)
    workflow.add_node("gather_intel", gather_intel_agent)
    workflow.add_node("significance_analyst", significance_analyst_agent)
    workflow.add_node("digest_agent", digest_and_alert_agent)
    workflow.set_entry_point("gather_intel")
    workflow.add_edge("gather_intel", "significance_analyst")
    workflow.add_edge("significance_analyst", "digest_agent")
    workflow.add_edge("digest_agent", END)
    return workflow.compile()