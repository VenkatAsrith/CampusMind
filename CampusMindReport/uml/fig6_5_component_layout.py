"""UML 2.x component diagram for CampusMind (Figure 6.5), hand-laid for A4 readability.
Same components and interfaces as fig6_5_component.puml."""
from matplotlib.patches import Rectangle
from uml_draw import (canvas, save, component, database, arrow, ball_socket, label,
                      top, bottom, left, right, FS)

fig, ax = canvas(7.4, 7.0)

# backend boundary (subsystem) with tab
ax.add_patch(Rectangle((0.25, 1.4), 6.85, 4.4, fc="none", ec="black", lw=1.0))
ax.add_patch(Rectangle((0.25, 5.8), 2.6, 0.26, fc="white", ec="black", lw=1.0))
ax.text(0.33, 5.93, "«subsystem» CampusMind Backend (FastAPI)", ha="left", va="center", fontsize=FS - 1,
        fontweight="bold")

fe = component(ax, 3.7, 6.5, 2.1, 0.72, "React Frontend\n(TypeScript, Vite)")
cl = component(ax, 6.2, 6.5, 1.6, 0.72, "Anthropic\nClaude API", stereo="«external system»")

auth = component(ax, 1.3, 5.0, 1.85, 0.75, "Authentication and\nAuthorization")
api = component(ax, 3.7, 5.0, 1.85, 0.75, "FastAPI REST API\n(routers, validation)")
llm = component(ax, 6.0, 5.0, 1.8, 0.75, "LLM Provider\nAdapter")
conv = component(ax, 1.5, 3.55, 1.6, 0.75, "Conversation\nService")
rag = component(ax, 3.7, 3.55, 1.85, 0.75, "Retrieval / RAG Service\n(RAG Orchestrator)")
ing = component(ax, 6.0, 3.55, 1.8, 0.75, "Document Ingestion\nService")
emb = component(ax, 4.9, 2.15, 1.6, 0.75, "Embedding Service\n(all-MiniLM-L6-v2)")
db = database(ax, 3.7, 0.62, 6.5, 0.5, "PostgreSQL 16 + pgvector")

# interfaces (assembly connectors)
ball_socket(ax, bottom(fe), top(api), "REST / JSON over HTTPS", name_off=(0.12, 0.02))
ball_socket(ax, left(api), right(auth), "IAuth", name_off=(0, 0.17), name_ha="center")
ball_socket(ax, (4.45, 3.925), (5.7, 4.625), "IGenerate", name_off=(0.12, -0.05))
ball_socket(ax, (4.2, 3.175), (4.55, 2.525), "IEmbed", name_off=(-0.12, 0.0), name_ha="right")
ball_socket(ax, (5.75, 3.175), (5.3, 2.525), "IEmbed", name_off=(0.12, 0.0))

# usage dependencies from the API layer
arrow(ax, [(3.15, 4.625), (1.9, 3.925)], dashed=True, text="«use»", tpos=(2.45, 4.35))
arrow(ax, [(3.7, 4.625), (3.7, 3.925)], dashed=True, text="«use»", tpos=(3.95, 4.27))
# routed around the LLM adapter so it does not cross the IGenerate connector
arrow(ax, [(4.35, 5.375), (4.35, 5.6), (7.0, 5.6), (7.0, 3.55), (6.9, 3.55)], dashed=True,
      text="«use»", tpos=(7.0, 4.5))

# external call
arrow(ax, [top(llm), (6.0, 6.14)], text="HTTPS +\nAPI key", tpos=(5.62, 5.86))
# SQL access
arrow(ax, [(0.55, 4.625), (0.55, 0.87)], text="SQL", tpos=(0.55, 2.6))
arrow(ax, [bottom(conv), (1.5, 0.87)], text="SQL", tpos=(1.5, 2.3))
arrow(ax, [(3.4, 3.175), (3.4, 0.87)], text="SQL + vector search\n(role filter in WHERE)", tpos=(3.0, 1.95))
arrow(ax, [(6.5, 3.175), (6.5, 0.87)], text="SQL\n(one transaction)", tpos=(6.5, 1.8))

save(fig, "fig6_5_component.png")
