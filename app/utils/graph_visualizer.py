from pyvis.network import Network
import tempfile
import os
from typing import List, Dict, Any

class GraphVisualizer:
    def __init__(self):
        # Color mapping based on node labels
        self.color_map = {
            "Elder": "#97C2FC",       # Light Blue
            "Medicine": "#FF9999",    # Light Red
            "Appointment": "#FFE699", # Light Yellow
            "Symptom": "#FFB366",     # Light Orange
            "Mood": "#CC99FF",        # Light Purple
            "EmotionalMemory": "#FF99CC", # Pink
            "Location": "#99FF99",    # Light Green
            "Person": "#A6A6A6"       # Gray
        }
        
    def generate_html(self, nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> str:
        """
        Takes raw dictionaries representing nodes and edges from a Neo4j Mindmap 
        and renders an interactive HTML string utilizing Pyvis.
        """
        # Create a Pyvis network with physics enabled for natural layout
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black", directed=True)
        # Add solver to organize the tree nicely
        net.barnes_hut()
        
        # Keep track of added node IDs to prevent duplication constraints in Pyvis
        added_node_ids = set()
        
        # 1. Map Nodes
        for node in nodes:
            node_id = str(node.get("id"))
            if node_id in added_node_ids:
                continue
                
            labels = node.get("labels", [])
            primary_label = labels[0] if labels else "Unknown"
            
            # Label rendering priority
            display_label = node_id
            if "name" in node:
                display_label = node["name"]
            elif "type" in node and primary_label == "Symptom":
                display_label = node["type"]
            elif "label" in node and primary_label == "Mood":
                display_label = f"Mood: {node['label']}"
            elif "text" in node:
                # Truncate text for node label if it's too long
                display_label = node["text"][:20] + "..." if len(node["text"]) > 20 else node["text"]
                
            # Confidence Size scaling (baseline 10 -> up to 30)
            confidence = float(node.get("confidence_score", 0.5))
            node_size = max(10, int(confidence * 30))
            
            # Color assignment
            node_color = self.color_map.get(primary_label, "#D3D3D3")
            
            # Build hover title context
            title_html = f"<b>Type:</b> {primary_label}<br><b>Confidence:</b> {confidence:.2f}"
            if "last_reinforced_at" in node:
                title_html += f"<br><b>Last Reinforced:</b> {node['last_reinforced_at']}"
                
            net.add_node(
                node_id, 
                label=display_label, 
                title=title_html,
                color=node_color,
                size=node_size,
                group=primary_label
            )
            added_node_ids.add(node_id)
            
        # 2. Map Relationships
        for rel in relationships:
            source = str(rel.get("source"))
            target = str(rel.get("target"))
            rel_type = rel.get("type", "")
            
            # Basic validation to ensure both ends exist
            if source in added_node_ids and target in added_node_ids:
                net.add_edge(source, target, label=rel_type, title=rel_type, color="#848484", arrows="to")
                
        # 3. Compile output HTML string
        # Pyvis only natively writes to file, so we write to a tempfile then read the string out
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"mindmap_{os.getpid()}.html")
        
        net.write_html(temp_file)
        
        with open(temp_file, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        os.remove(temp_file)
        return html_content

graph_visualizer = GraphVisualizer()
