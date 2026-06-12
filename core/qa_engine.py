"""问答引擎 - 图谱检索 + LLM生成"""
import json
import re
from typing import Dict, List
from core.llm_client import generate
from core.graph_store import GraphStore

QA_SYSTEM = """你是知识图谱问答专家。基于提供的图谱数据回答用户问题。
要求:
1. 只根据提供的图谱事实回答，不要编造
2. 如果图谱中没有相关信息，明确说"图谱中暂无相关信息"
3. 回答要简洁准确
4. 如果涉及多跳推理，列出推理路径"""

PARSE_SYSTEM = """你是意图识别专家。从用户问题中提取关键实体和意图。
输出JSON格式: {"entities": ["实体1", "实体2"], "intent": "查询类型", "hops": 跳数}
意图类型: entity_query, relation_query, path_query, count_query"""


class QAEngine:
    def __init__(self, store: GraphStore = None):
        self.store = store or GraphStore()

    def ask(self, question: str) -> Dict:
        intent = self._parse_intent(question)
        context = self._retrieve(intent)
        answer = self._generate_answer(question, context)
        return {"question": question, "intent": intent, "context": context, "answer": answer}

    def _parse_intent(self, question: str) -> Dict:
        prompt = f"分析以下问题：\n{question}"
        result = generate(prompt, system=PARSE_SYSTEM, temperature=0.1)
        try:
            match = re.search(r'\{.*\}', result, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {"entities": [question], "intent": "relation_query", "hops": 1}

    def _retrieve(self, intent: Dict) -> List[Dict]:
        entities = intent.get("entities", [])
        hops = intent.get("hops", 1)
        all_facts = []
        for entity in entities:
            matched = self.store.search_entities(entity)
            if not matched:
                matched = [entity]
            for m in matched:
                neighbors = self.store.get_neighbors(m, depth=hops)
                all_facts.extend(neighbors)
        seen = set()
        unique = []
        for f in all_facts:
            key = (f["source"], f["relation"], f["target"])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique[:20]

    def _generate_answer(self, question: str, facts: List[Dict]) -> str:
        if not facts:
            return "图谱中暂无相关信息，请先导入相关知识。"
        facts_text = "\n".join([f"- {f['source']} --[{f['relation']}]--> {f['target']}" for f in facts])
        prompt = f"基于以下知识图谱事实回答问题。\n\n图谱事实:\n{facts_text}\n\n问题: {question}\n\n请给出准确的回答:"
        return generate(prompt, system=QA_SYSTEM, temperature=0.3)
