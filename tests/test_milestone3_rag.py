"""Pytest Test Suite for Milestone 3: RAG Knowledge Engine & Vector Store."""
import pytest
from app.rag_engine import RAGKnowledgeEngine, rag_engine


@pytest.fixture
def engine():
    eng = RAGKnowledgeEngine()
    eng.initialize()
    return eng


def test_rag_knowledge_base_ingestion(engine):
    """Verify loading and section chunking of markdown knowledge playbooks."""
    assert len(engine.documents) > 0
    doc_titles = {d["document_title"] for d in engine.documents}
    assert "Cloud Instance Specs" in doc_titles
    assert "Finops Rightsizing Playbook" in doc_titles
    assert "Capacity Sla Risk Playbook" in doc_titles
    print(f"[SUCCESS] RAG Ingestion verified. Indexed {len(engine.documents)} knowledge sections.")


def test_rag_query_graviton_migration(engine):
    """Verify semantic retrieval for Graviton ARM migration cost savings query."""
    results = engine.query_playbook("c5 to c6g graviton migration cost savings", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["relevance_score"] > 0.0
    assert "c6g" in top_match["content"].lower() or "graviton" in top_match["content"].lower()
    assert top_match["citation"] != ""
    print(f"[SUCCESS] RAG Graviton query match: {top_match['citation']} (Score: {top_match['relevance_score']})")


def test_rag_query_memory_oom_sla_risk(engine):
    """Verify semantic retrieval for Memory OOM and SLA risk query."""
    results = engine.query_playbook("memory utilization 90% critical OOM SLA risk", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["relevance_score"] > 0.0
    assert "memory" in top_match["content"].lower() or "oom" in top_match["content"].lower()
    assert top_match["citation"] != ""
    print(f"[SUCCESS] RAG SLA Risk query match: {top_match['citation']} (Score: {top_match['relevance_score']})")


def test_rag_query_cpu_overprovisioned_rightsizing(engine):
    """Verify semantic retrieval for CPU over-provisioning right-sizing query."""
    results = engine.query_playbook("CPU over-provisioning low utilization downsize instance", top_k=2)
    assert len(results) > 0
    top_match = results[0]
    assert top_match["relevance_score"] > 0.0
    assert "citation" in top_match
    print(f"[SUCCESS] RAG Right-sizing query match: {top_match['citation']}")
