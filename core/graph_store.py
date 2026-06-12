"""知识图谱存储 - 基于NetworkX"""
import json
import os
import networkx as nx
from typing import List, Dict, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
GRAPH_PATH = os.path.join(DATA_DIR, "graph.json")


class GraphStore:
    def __init__(self, path: str = GRAPH_PATH):
        self.path = path
        self.graph = nx.DiGraph()
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for node in data.get("nodes", []):
                self.graph.add_node(node["id"], **node.get("attrs", {}))
            for edge in data.get("edges", []):
                self.graph.add_edge(edge["source"], edge["target"],
                                    relation=edge["relation"], **edge.get("attrs", {}))

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        data = {
            "nodes": [{"id": n, "attrs": dict(self.graph.nodes[n])} for n in self.graph.nodes],
            "edges": [{"source": u, "target": v, "relation": d.get("relation", ""),
                        "attrs": {k: v2 for k, v2 in d.items() if k != "relation"}}
                       for u, v, d in self.graph.edges(data=True)]
        }
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_triple(self, subject: str, relation: str, obj: str, **attrs):
        self.graph.add_node(subject, type="entity")
        self.graph.add_node(obj, type="entity")
        self.graph.add_edge(subject, obj, relation=relation, **attrs)
        self.save()

    def add_triples(self, triples: List[Dict]):
        for t in triples:
            s, r, o = t.get("subject", ""), t.get("relation", ""), t.get("object", "")
            if s and r and o:
                self.graph.add_node(s, type="entity")
                self.graph.add_node(o, type="entity")
                self.graph.add_edge(s, o, relation=r)
        self.save()

    def get_neighbors(self, entity: str, depth: int = 1) -> List[Dict]:
        results = []
        visited = set()
        def _dfs(node, d):
            if d > depth or node in visited:
                return
            visited.add(node)
            for _, target, data in self.graph.out_edges(node, data=True):
                results.append({"source": node, "relation": data.get("relation", ""), "target": target})
                _dfs(target, d + 1)
            for source, _, data in self.graph.in_edges(node, data=True):
                results.append({"source": source, "relation": data.get("relation", ""), "target": node})
                _dfs(source, d + 1)
        _dfs(entity, 0)
        return results

    def find_path(self, start: str, end: str) -> Optional[List[Dict]]:
        try:
            path = nx.shortest_path(self.graph.to_undirected(), start, end)
            result = []
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = self.graph.get_edge_data(u, v) or self.graph.get_edge_data(v, u) or {}
                result.append({"source": u, "relation": edge_data.get("relation", ""), "target": v})
            return result
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def search_entities(self, keyword: str) -> List[str]:
        return [n for n in self.graph.nodes if keyword.lower() in n.lower()]

    def get_all_triples(self) -> List[Dict]:
        return [{"source": u, "relation": d.get("relation", ""), "target": v}
                for u, v, d in self.graph.edges(data=True)]

    def get_graph_data(self) -> Dict:
        nodes = [{"id": n, "label": n, "group": self.graph.nodes[n].get("type", "entity")}
                 for n in self.graph.nodes]
        edges = [{"from": u, "to": v, "label": d.get("relation", ""), "arrows": "to"}
                 for u, v, d in self.graph.edges(data=True)]
        return {"nodes": nodes, "edges": edges}

    def stats(self) -> Dict:
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "triples": self.graph.number_of_edges(),
            "connected_components": nx.number_weakly_connected_components(self.graph)
        }
