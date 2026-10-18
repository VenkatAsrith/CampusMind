"""Hand-laid UML 2.x use case diagram for CampusMind (Figure 6.1).

Same actors, use cases and relationships as fig6_1_use_case.puml; this script
only fixes the layout so the diagram stays readable at A4 width.
Run: python fig6_1_use_case_layout.py  ->  ../uml_png/fig6_1_use_case.png
"""
import math
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch

plt.rcParams["font.family"] = "Times New Roman"
FS = 10
W, H = 7.4, 8.2
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

EW, EH = 1.75, 0.6          # default ellipse size
uc = {}


def usecase(key, x, y, text, w=EW, h=EH):
    ax.add_patch(Ellipse((x, y), w, h, fc="white", ec="black", lw=0.9))
    ax.text(x, y, text, ha="center", va="center", fontsize=FS, linespacing=1.05)
    uc[key] = (x, y, w, h)


def actor(x, y, name, below=True):
    # stick figure, head centre at (x, y)
    ax.add_patch(plt.Circle((x, y), 0.09, fc="white", ec="black", lw=0.9))
    ax.plot([x, x], [y - 0.09, y - 0.42], c="black", lw=0.9)
    ax.plot([x - 0.17, x + 0.17], [y - 0.2, y - 0.2], c="black", lw=0.9)
    ax.plot([x, x - 0.15], [y - 0.42, y - 0.65], c="black", lw=0.9)
    ax.plot([x, x + 0.15], [y - 0.42, y - 0.65], c="black", lw=0.9)
    ax.text(x, y - 0.78, name, ha="center", va="top", fontsize=FS, linespacing=1.05)
    return (x, y - 0.3)


def edge_point(key, toward):
    x, y, w, h = uc[key]
    a, b = w / 2, h / 2
    dx, dy = toward[0] - x, toward[1] - y
    t = 1 / math.sqrt((dx / a) ** 2 + (dy / b) ** 2)
    return (x + dx * t, y + dy * t)


def line(p, q, style="-", head=None, label=None, lpos=0.5, loff=(0, 0.1)):
    if head == "open":
        arrow = FancyArrowPatch(p, q, arrowstyle="->,head_length=6,head_width=3.5",
                                linestyle=style, lw=0.8, color="black", shrinkA=0, shrinkB=0)
    elif head == "triangle":
        arrow = FancyArrowPatch(p, q, arrowstyle="-|>,head_length=9,head_width=5",
                                lw=0.8, color="black", fc="white", shrinkA=0, shrinkB=0)
    else:
        arrow = FancyArrowPatch(p, q, arrowstyle="-", linestyle=style, lw=0.8,
                                color="black", shrinkA=0, shrinkB=0)
    ax.add_patch(arrow)
    if label:
        mx = p[0] + (q[0] - p[0]) * lpos + loff[0]
        my = p[1] + (q[1] - p[1]) * lpos + loff[1]
        ax.text(mx, my, label, ha="center", va="bottom", fontsize=FS - 1.5, linespacing=1.0,
                bbox=dict(fc="white", ec="none", pad=0.6))


def dep(a, b, label, lpos=0.5, loff=(0, 0.06)):
    p = edge_point(a, uc[b][:2])
    q = edge_point(b, uc[a][:2])
    line(p, q, style=(0, (4, 3)), head="open", label=label, lpos=lpos, loff=loff)


# system boundary
BX0, BX1, BY0, BY1 = 1.75, 6.05, 0.2, 7.95
ax.add_patch(Rectangle((BX0, BY0), BX1 - BX0, BY1 - BY0, fc="none", ec="black", lw=1.0))
ax.text((BX0 + BX1) / 2, BY1 - 0.12, "CampusMind", ha="center", va="top", fontsize=FS + 1.5,
        fontweight="bold")
ax.plot([BX0, BX1], [3.0, 3.0], c="black", lw=0.7, ls=(0, (5, 4)))
ax.text(BX1 - 0.08, 3.06, "user-level functions", ha="right", va="bottom", fontsize=FS - 2,
        style="italic")
ax.text(BX1 - 0.08, 2.94, "administrative functions", ha="right", va="top", fontsize=FS - 2,
        style="italic")

L, R = 3.25, 5.15
usecase("auth", L, 7.35, "Authenticate user")
usecase("mention", L, 6.5, "Perform authorized\nrestricted-information\nworkflow (@ mention)", w=1.95, h=0.74)
usecase("ask", L, 5.6, "Ask campus question")
usecase("view", L, 4.85, "View answer\nand citations")
usecase("hist", L, 4.15, "View conversation\nhistory")
usecase("manage", L, 3.45, "Manage own\nconversations")
usecase("generate", R, 6.25, "Generate grounded\nanswer", w=1.6)
usecase("retrieve", R, 4.85, "Retrieve authorized\nevidence", w=1.6)
usecase("upload", L, 2.3, "Upload campus\ndocument")
usecase("classify", R, 2.4, "Classify document\naudience", w=1.6)
usecase("index", R, 1.55, "Process and index\ndocument", w=1.6)
usecase("status", L, 1.45, "View document\nprocessing status")
usecase("delete", L, 0.65, "Delete document")

# actors
st = actor(0.45, 7.55, "Student")
fa = actor(1.25, 7.55, "Faculty")
ru = actor(0.85, 5.55, "Registered\nUser")
ad = actor(0.85, 2.2, "Administrator")
cl = actor(6.75, 6.6, "Anthropic\nClaude API\n«external\nsystem»")

# generalisations (hollow triangle towards the parent)
line((0.45, 6.75), (0.75, 5.75), head="triangle")
line((1.25, 6.75), (0.95, 5.75), head="triangle")
line((0.85, 2.3), (0.85, 4.5), head="triangle")
ax.text(0.95, 3.5, "inherits all\nRegistered User\nuse cases", ha="left", va="center",
        fontsize=FS - 2.5, style="italic")

# associations
ru_pt = (1.12, 5.35)
def leftmost(k):
    x, y, w, h = uc[k]
    return (x - w / 2, y)


for k in ["auth", "mention", "ask", "view", "hist", "manage"]:
    line(ru_pt, leftmost(k))
ad_pt = (1.12, 1.85)
for k in ["upload", "status", "delete"]:
    line(ad_pt, leftmost(k))
line((6.55, 6.25), edge_point("generate", (6.55, 6.25)))

# include / extend
dep("ask", "retrieve", "«include»", lpos=0.5, loff=(0, 0.02))
dep("mention", "auth", "«include»", lpos=0.5, loff=(0.4, -0.06))
dep("generate", "ask", "«extend»\n[evidence ≥ τ]", lpos=0.5, loff=(-0.45, -0.02))
dep("upload", "classify", "«include»", lpos=0.5, loff=(0, 0.13))
dep("upload", "index", "«include»", lpos=0.5, loff=(0, -0.2))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uml_png", "fig6_1_use_case.png")
fig.savefig(out, dpi=220, facecolor="white")
print("saved", out)
