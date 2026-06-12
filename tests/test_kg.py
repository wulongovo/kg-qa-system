import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from core.graph_store import GraphStore

def test_graph_store():
    store = GraphStore(path="/tmp/test_graph.json")
    store.add_triple("LangChain", "是", "LLM应用框架")
    store.add_triple("LangGraph", "基于", "LangChain")
    store.add_triple("LangChain", "创始人", "Harrison Chase")
    assert store.stats()["nodes"] >= 4
    assert store.stats()["edges"] >= 3
    neighbors = store.get_neighbors("LangChain")
    assert len(neighbors) >= 2
    results = store.search_entities("Lang")
    assert "LangChain" in results
    path = store.find_path("LangGraph", "Harrison Chase")
    assert path is not None
    os.remove("/tmp/test_graph.json")
    print("✓ 所有测试通过")

if __name__ == "__main__":
    test_graph_store()
