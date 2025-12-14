from graph import generate_graph

# Genera un archivo Mermaid para visualizar el flujo del agente.

graph = generate_graph()

mermaid_code = graph.get_graph().draw_mermaid()

with open("agent_flow.mmd", "w", encoding="utf-8") as f:
    f.write(mermaid_code)