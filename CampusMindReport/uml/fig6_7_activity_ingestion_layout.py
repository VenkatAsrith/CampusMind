"""UML 2.x activity diagram for document ingestion (Figure 6.7), hand-laid in three columns so it
stays legible at A4 width. Same actions and decisions as fig6_7_activity_ingestion.puml; the
connector A joins the end of the validation column to the start of the processing column."""
from matplotlib.patches import FancyBboxPatch, Polygon
import matplotlib.pyplot as plt
from uml_draw import canvas, save, arrow, label, FS

fig, ax = canvas(7.6, 9.2)


def act(x, y, w, text, h=0.48):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.1",
                                fc="white", ec="black", lw=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=FS - 1, linespacing=1.05)
    return dict(x=x, y=y, w=w, h=h)


def dec(x, y, text, w=1.9, h=0.5):
    ax.add_patch(Polygon([(x - w / 2, y), (x, y + h / 2), (x + w / 2, y), (x, y - h / 2)], closed=True,
                         fc="white", ec="black", lw=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=FS - 1.5)
    return dict(x=x, y=y, w=w, h=h)


def start(x, y):
    ax.add_patch(plt.Circle((x, y), 0.1, fc="black", ec="black"))


def final(x, y):
    ax.add_patch(plt.Circle((x, y), 0.12, fc="white", ec="black", lw=0.9))
    ax.add_patch(plt.Circle((x, y), 0.07, fc="black", ec="black"))


def connector(x, y, name):
    ax.add_patch(plt.Circle((x, y), 0.13, fc="white", ec="black", lw=0.9))
    ax.text(x, y, name, ha="center", va="center", fontsize=FS - 1, fontweight="bold")


def down(a, b):
    arrow(ax, [(a["x"], a["y"] - a["h"] / 2), (b["x"], b["y"] + b["h"] / 2)])


A, B, C, BUS = 1.35, 3.45, 6.15, 4.65
ax.text(A, 9.05, "Administrator and validation", ha="center", va="top", fontsize=FS - 1, style="italic")
ax.text(C, 9.05, "Processing (Document Ingestion Service)", ha="center", va="top", fontsize=FS - 1, style="italic")

# ---- column A: request and validation
start(A, 8.65)
a1 = act(A, 8.1, 2.3, "Select document and\naudience role", 0.55)
a2 = act(A, 7.35, 2.3, "Submit upload\n(POST /api/admin/documents)", 0.55)
a3 = act(A, 6.65, 2.3, "Verify JWT and role")
d1 = dec(A, 6.0, "Administrator?")
a4 = act(A, 5.25, 2.3, "Validate name, extension\n(PDF/DOCX/TXT), size ≤ 10 MB,\nnon-empty", 0.7)
d2 = dec(A, 4.45, "File valid?")
a5 = act(A, 3.8, 2.3, "Compute SHA-256 hash")
a6 = act(A, 3.1, 2.3, "Create Document\n(status = PROCESSING)", 0.55)
arrow(ax, [(A, 8.55), (A, 8.375)])
down(a1, a2); down(a2, a3); down(a3, d1)
arrow(ax, [(A, 5.75), (A, 5.6)], text="[yes]", tpos=(A + 0.3, 5.66))
down(a4, d2)
arrow(ax, [(A, 4.2), (A, 4.04)], text="[yes]", tpos=(A + 0.3, 4.12))
down(a5, a6)
connector(A, 2.4, "A")
arrow(ax, [(A, 2.825), (A, 2.53)])

# ---- column B: rejections
r1 = act(B, 6.0, 1.5, "Return\n403 Forbidden", 0.55)
r2 = act(B, 4.45, 1.5, "Return 400\nvalidation error", 0.55)
arrow(ax, [(A + 0.95, 6.0), (B - 0.75, 6.0)], text="[no]", tpos=(2.48, 6.13))
arrow(ax, [(A + 0.95, 4.45), (B - 0.75, 4.45)], text="[no]", tpos=(2.48, 4.58))
final(B, 5.45); arrow(ax, [(B, 5.725), (B, 5.57)])
final(B, 3.9); arrow(ax, [(B, 4.175), (B, 4.02)])

# ---- column C: processing
connector(C, 8.65, "A")
c1 = act(C, 8.05, 2.5, "Extract text with page /\nsection metadata", 0.55)
d3 = dec(C, 7.35, "Text extracted?")
c2 = act(C, 6.65, 2.5, "Clean text; split into\noverlapping chunks", 0.55)
c3 = act(C, 5.9, 2.5, "Generate 384-d embeddings\n(batch)", 0.55)
d4 = dec(C, 5.2, "Embeddings generated?", w=2.2)
c4 = act(C, 4.5, 2.5, "Persist chunks, vectors\nand metadata", 0.55)
d5 = dec(C, 3.8, "Transaction committed?", w=2.2)
c5 = act(C, 3.1, 2.5, "Set status = COMPLETED;\nrecord chunk count", 0.55)
c6 = act(C, 2.35, 2.5, "Document listed as\nretrievable", 0.55)
arrow(ax, [(C, 8.52), (C, 8.325)])
down(c1, d3)
arrow(ax, [(C, 7.1), (C, 6.925)], text="[yes]", tpos=(C + 0.3, 7.0))
down(c2, c3); down(c3, d4)
arrow(ax, [(C, 4.95), (C, 4.775)], text="[yes]", tpos=(C + 0.3, 4.86))
down(c4, d5)
arrow(ax, [(C, 3.55), (C, 3.375)], text="[yes]", tpos=(C + 0.3, 3.46))
down(c5, c6)
final(C, 1.75); arrow(ax, [(C, 2.075), (C, 1.87)])

# ---- shared failure path (merge node, then rollback)
for d in (d3, d4, d5):
    ax.plot([d["x"] - d["w"] / 2, BUS], [d["y"], d["y"]], c="black", lw=0.8)
    label(ax, (d["x"] - d["w"] / 2 + BUS) / 2, d["y"] + 0.13, "[no]")
ax.plot([BUS, BUS], [7.35, 2.05], c="black", lw=0.8)
mx, my = BUS, 1.85
ax.add_patch(Polygon([(mx - 0.15, my), (mx, my + 0.2), (mx + 0.15, my), (mx, my - 0.2)], closed=True,
                     fc="white", ec="black", lw=0.9))
arrow(ax, [(BUS, 2.05), (BUS, 2.05)])
f1 = act(3.0, 1.0, 2.6, "Roll back chunks; status = FAILED;\nstore error; report failure", 0.6)
arrow(ax, [(mx, my - 0.2), (mx, 1.0), (3.0 + 1.3, 1.0)])
final(1.35, 1.0); arrow(ax, [(3.0 - 1.3, 1.0), (1.47, 1.0)])

save(fig, "fig6_7_activity_ingestion.png")
