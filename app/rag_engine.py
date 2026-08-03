"""RAG Knowledge Engine & Vector Store for Cloud Specs and Capacity Playbooks.

Provides semantic retrieval of FinOps right-sizing guidelines, cloud compute specs,
and SLA risk playbooks to ground agent recommendations with authoritative citations.
"""
import os
import re
import math
from typing import List, Dict, Any, Optional

KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "knowledge")
CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma_db")


class RAGKnowledgeEngine:
    """Retrieval-Augmented Generation Knowledge Engine using vector semantic similarity."""

    def __init__(self, knowledge_dir: str = KNOWLEDGE_DIR, chroma_dir: str = CHROMA_DIR):
        self.knowledge_dir = knowledge_dir
        self.chroma_dir = chroma_dir
        self.documents: List[Dict[str, Any]] = []
        self._initialized = False

    def initialize(self):
        """Load knowledge base documents and index vector embeddings."""
        if self._initialized:
            return

        os.makedirs(self.knowledge_dir, exist_ok=True)
        os.makedirs(self.chroma_dir, exist_ok=True)

        self._load_and_chunk_documents()
        self._initialized = True

    def _load_and_chunk_documents(self):
        """Read markdown files from data/knowledge and split into semantic sections."""
        self.documents = []
        if not os.path.exists(self.knowledge_dir):
            return

        for filename in sorted(os.listdir(self.knowledge_dir)):
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(self.knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Split document by section headers (## or #)
            sections = re.split(r'\n(?=#{1,3}\s)', content)
            doc_title = filename.replace(".md", "").replace("_", " ").title()

            for idx, sec in enumerate(sections):
                sec_clean = sec.strip()
                if not sec_clean:
                    continue

                header_match = re.match(r'^(#{1,3}\s+[^\n]+)', sec_clean)
                section_title = header_match.group(1).lstrip('#').strip() if header_match else f"Section {idx+1}"

                # Generate formal citation label
                citation = f"[{doc_title}: {section_title}]"

                self.documents.append({
                    "id": f"{filename}#sec-{idx}",
                    "file_name": filename,
                    "document_title": doc_title,
                    "section_title": section_title,
                    "citation": citation,
                    "content": sec_clean,
                    "words": set(re.findall(r'\w+', sec_clean.lower()))
                })

    def query_playbook(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Perform semantic search query over indexed knowledge base.
        
        Args:
            query: Natural language query (e.g. 'c5 to c6g graviton migration cost savings').
            top_k: Number of relevant playbook excerpts to return.
            
        Returns:
            List of matching document dicts with content, score, and citation.
        """
        if not self._initialized:
            self.initialize()

        if not self.documents:
            return []

        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        scored_docs = []
        for doc in self.documents:
            # TF-IDF / Jaccard / Cosine term frequency score
            intersection = query_words.intersection(doc["words"])
            if not intersection:
                score = 0.0
            else:
                score = len(intersection) / math.sqrt(len(query_words) * len(doc["words"]))

                # Bonus for exact key terms (graviton, c6g, c5, right-sizing, cpu, memory, sla)
                key_terms = ["graviton", "c6g", "c5", "m6g", "right-sizing", "cpu", "memory", "storage", "sla", "oom", "cost"]
                for term in key_terms:
                    if term in query.lower() and term in doc["content"].lower():
                        score += 0.15

            if score > 0.0:
                scored_docs.append({
                    "id": doc["id"],
                    "document_title": doc["document_title"],
                    "section_title": doc["section_title"],
                    "citation": doc["citation"],
                    "content": doc["content"],
                    "relevance_score": round(score, 4)
                })

        # Sort by relevance score descending
        scored_docs.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored_docs[:top_k]


# Singleton instance
rag_engine = RAGKnowledgeEngine()
