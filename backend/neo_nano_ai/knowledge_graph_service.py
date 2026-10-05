
from .medical_data_loader import load_master_records

def build_global_graph():
    records = load_master_records()
    nodes = {}
    edges = []

    for record in records:
        disease_id = record["id"]
        nodes[disease_id] = {"type": "Disease", "name": record.get("name")}

        kg = record.get("knowledge_graph", {})
        for relation in kg.get("relationships", []):
            target_type = relation.get("target_type", "Entity")
            target_name = relation.get("target_name", "")
            if not target_name:
                continue
            target_id = f"{target_type}:{target_name}".casefold()
            nodes.setdefault(target_id, {"type": target_type, "name": target_name})
            edges.append({
                "source": disease_id,
                "relation": relation.get("relation"),
                "target": target_id
            })

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges
    }
