#!/usr/bin/env python3
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.kg_builder import KGBuilder

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", help="文本文件路径")
    parser.add_argument("--sample", action="store_true", help="导入示例数据")
    args = parser.parse_args()

    builder = KGBuilder()
    if args.sample:
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_knowledge.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for text in data["texts"]:
            result = builder.ingest_text(text)
            print(f"  抽取 {result['triples_unique']} 个三元组")
        print(f"\n完成! 图谱: {builder.store.stats()}")
    elif args.file:
        result = builder.ingest_file(args.file)
        print(f"完成! {result['triples_unique']} 个三元组")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
