"""知识图谱构建器 - LLM抽取实体关系"""
import json
import re
from typing import List, Dict
from core.llm_client import generate
from core.graph_store import GraphStore

EXTRACT_SYSTEM = """你是知识图谱构建专家。从给定文本中抽取(主语, 关系, 宾语)三元组。
严格输出JSON数组格式，不要输出其他内容。
格式: [{"subject": "主语", "relation": "关系", "object": "宾语"}, ...]
要求:
1. 实体用完整名称，不要用代词
2. 关系用简洁的动词短语
3. 尽量抽取所有有意义的关系
4. 每个三元组必须完整，不能省略"""


class KGBuilder:
    def __init__(self, store: GraphStore = None):
        self.store = store or GraphStore()

    def extract_triples(self, text: str) -> List[Dict]:
        prompt = f"请从以下文本中抽取知识三元组：\n\n{text[:3000]}"
        result = generate(prompt, system=EXTRACT_SYSTEM, temperature=0.1)
        return self._parse_triples(result)

    def _parse_triples(self, text: str) -> List[Dict]:
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                triples = json.loads(match.group())
                return [t for t in triples if all(k in t for k in ["subject", "relation", "object"])]
            except json.JSONDecodeError:
                pass
        return []

    def ingest_text(self, text: str, chunk_size: int = 500) -> Dict:
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        all_triples = []
        for chunk in chunks:
            if len(chunk.strip()) < 20:
                continue
            triples = self.extract_triples(chunk)
            all_triples.extend(triples)
        seen = set()
        unique = []
        for t in all_triples:
            key = (t["subject"], t["relation"], t["object"])
            if key not in seen:
                seen.add(key)
                unique.append(t)
        self.store.add_triples(unique)
        return {
            "chunks_processed": len(chunks),
            "triples_extracted": len(all_triples),
            "triples_unique": len(unique),
            "graph_stats": self.store.stats()
        }

    def ingest_file(self, filepath: str) -> Dict:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        return self.ingest_text(text)

    def add_manual_triple(self, subject: str, relation: str, obj: str):
        self.store.add_triple(subject, relation, obj)
