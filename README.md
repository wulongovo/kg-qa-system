# 🧠 知识图谱问答系统 (KG-QA System)

基于大模型的知识图谱构建与智能问答系统。自动从文本中抽取实体关系，构建知识图谱，支持自然语言问答和多跳推理。

## 架构

```
用户输入文本/问题
      ↓
┌─────────────────────────┐
│    FastAPI 后端          │
├─────────────────────────┤
│  ┌───────────┐ ┌──────┐ │     ┌──────────┐
│  │ KG Builder│ │ QA   │ │────→│ Ollama   │
│  │ (LLM抽取) │ │Engine│ │     │ qwen2.5  │
│  └─────┬─────┘ └──┬───┘ │     └──────────┘
│  ┌─────▼──────────▼───┐ │
│  │   Graph Store      │ │
│  │   (NetworkX + JSON)│ │
│  └────────────────────┘ │
├─────────────────────────┤
│  前端 (vis.js 可视化)    │
└─────────────────────────┘
```

## 技术栈
- **LLM**: Ollama + qwen2.5（本地推理）
- **后端**: FastAPI + Uvicorn
- **图谱**: NetworkX（JSON持久化）
- **可视化**: vis.js

## 使用

```bash
pip install -r requirements.txt
python main.py serve           # Web服务 http://localhost:8000
python scripts/ingest.py --sample  # 导入示例数据
python main.py ask "LangChain是什么？"
```

## 面试话术

> "我用LangChain + NetworkX构建了知识图谱问答系统。LLM自动从文本中抽取实体关系三元组，存入NetworkX有向图。问答时先解析意图提取实体，再图谱检索相关事实，最后LLM生成回答。前端用vis.js做交互式图谱可视化。全部本地推理，零API依赖。"
