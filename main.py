#!/usr/bin/env python3
"""知识图谱问答系统 - 主入口"""
import argparse, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.graph_store import GraphStore
from core.kg_builder import KGBuilder
from core.qa_engine import QAEngine

def main():
    parser = argparse.ArgumentParser(description="知识图谱问答系统")
    sub = parser.add_subparsers(dest="cmd")

    p_ingest = sub.add_parser("ingest", help="导入文本构建知识图谱")
    p_ingest.add_argument("file", help="文本文件路径")
    p_ingest.add_argument("--chunk-size", type=int, default=500)

    p_ask = sub.add_parser("ask", help="知识图谱问答")
    p_ask.add_argument("question", help="问题")

    sub.add_parser("stats", help="图谱统计")
    sub.add_parser("triples", help="列出所有三元组")

    p_serve = sub.add_parser("serve", help="启动Web服务")
    p_serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.cmd == "ingest":
        builder = KGBuilder()
        result = builder.ingest_file(args.file)
        print(f"导入完成: {result['triples_unique']} 个三元组")
    elif args.cmd == "ask":
        engine = QAEngine()
        result = engine.ask(args.question)
        print(f"问题: {result['question']}")
        print(f"回答: {result['answer']}")
    elif args.cmd == "stats":
        store = GraphStore()
        s = store.stats()
        print(f"实体: {s['nodes']}, 关系: {s['edges']}, 连通分量: {s['connected_components']}")
    elif args.cmd == "triples":
        store = GraphStore()
        for t in store.get_all_triples():
            print(f"  ({t['source']}, {t['relation']}, {t['target']})")
    elif args.cmd == "serve":
        import uvicorn
        from api.main import app
        uvicorn.run(app, host="0.0.0.0", port=args.port)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
