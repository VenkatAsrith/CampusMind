"""UML 2.x deployment diagram for CampusMind (Figure 6.6), hand-laid for A4 readability.
Same nodes and communication paths as fig6_6_deployment.puml."""
from uml_draw import canvas, save, node3d, artifact, database, arrow, FS

fig, ax = canvas(7.6, 6.6)
ax.text(3.7, 6.38, "Proposed deployment architecture (production hosting not yet verified)",
        ha="center", va="top", fontsize=FS, style="italic")

ud = node3d(ax, 0.3, 4.55, 2.4, 1.25, "User device", stereo="«device»")
br = artifact(ax, 1.5, 4.95, 1.7, 0.5, "Web browser")
fh = node3d(ax, 4.3, 4.55, 2.85, 1.25, "Frontend hosting", stereo="«execution environment»")
fb = artifact(ax, 5.72, 4.95, 2.2, 0.5, "React production build")

be = node3d(ax, 0.3, 2.15, 4.65, 1.75, "Backend application service", stereo="«container»")
a1 = artifact(ax, 1.12, 2.7, 1.45, 0.75, "campusmind-backend\n(FastAPI + Uvicorn)")
a2 = artifact(ax, 2.63, 2.7, 1.4, 0.75, "Embedding\nmodel files")
a3 = artifact(ax, 4.12, 2.7, 1.5, 0.75, "Environment secrets\n(JWT key, DB URL,\nANTHROPIC_API_KEY)")

ci = node3d(ax, 5.7, 2.5, 1.7, 1.0, "GitHub Actions CI", stereo="«deployment mechanism»")

dbn = node3d(ax, 0.3, 0.15, 2.05, 1.4, "Database server", stereo="«node» private network")
database(ax, 1.32, 0.52, 1.5, 0.42, "PostgreSQL 16\n+ pgvector")
st = node3d(ax, 2.65, 0.15, 2.0, 1.4, "Private document\nstorage (planned)", stereo="«node»", dashed=True)
cl = node3d(ax, 4.95, 0.15, 2.2, 1.4, "Anthropic Claude API", stereo="«external system»", dashed=True)

arrow(ax, [(2.7, 5.15), (4.3, 5.15)], text="HTTPS (static assets)", tpos=(3.5, 5.3))
arrow(ax, [(1.5, 4.55), (1.5, 3.9)], text="HTTPS / REST (JWT)", tpos=(2.35, 4.22))
arrow(ax, [(1.32, 2.15), (1.32, 1.55)], text="TCP 5432 (private)", tpos=(1.95, 1.85))
arrow(ax, [(3.65, 2.15), (3.65, 1.55)], dashed=True, text="file I/O", tpos=(3.95, 1.85))
arrow(ax, [(4.7, 2.15), (5.75, 1.55)], text="HTTPS + API key", tpos=(5.75, 2.0))
arrow(ax, [(5.7, 2.75), (4.95, 2.75)], dashed=True, text="test, build image", tpos=(5.32, 2.42))
arrow(ax, [(6.55, 3.5), (6.55, 4.55)], dashed=True, text="test, build bundle", tpos=(6.55, 4.02))

save(fig, "fig6_6_deployment.png")
