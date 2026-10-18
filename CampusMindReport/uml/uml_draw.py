"""Small monochrome UML drawing helpers (matplotlib) used for the hand-laid figures."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle, Polygon, Ellipse, Arc

plt.rcParams["font.family"] = "Times New Roman"
FS = 10
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "uml_png")


def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT_DIR, name)
    fig.savefig(path, dpi=220, facecolor="white")
    print("saved", path)


def component(ax, cx, cy, w, h, text, stereo="«component»"):
    """UML 2 component: rectangle with stereotype and the component icon."""
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="white", ec="black", lw=0.9))
    ix, iy = cx + w / 2 - 0.22, cy + h / 2 - 0.2
    ax.add_patch(Rectangle((ix, iy - 0.06), 0.14, 0.16, fc="white", ec="black", lw=0.6))
    ax.add_patch(Rectangle((ix - 0.04, iy + 0.04), 0.08, 0.03, fc="white", ec="black", lw=0.6))
    ax.add_patch(Rectangle((ix - 0.04, iy - 0.03), 0.08, 0.03, fc="white", ec="black", lw=0.6))
    ax.text(cx, cy + 0.06, stereo, ha="center", va="bottom", fontsize=FS - 2.5, style="italic")
    ax.text(cx, cy + 0.04, text, ha="center", va="top", fontsize=FS, linespacing=1.05)
    return dict(x=cx, y=cy, w=w, h=h)


def node3d(ax, x0, y0, w, h, title, stereo=None, d=0.12, dashed=False):
    """UML node (3-D box). Returns inner box coordinates."""
    ls = (0, (4, 3)) if dashed else "-"
    ax.add_patch(Rectangle((x0, y0), w, h, fc="white", ec="black", lw=0.9, ls=ls))
    ax.add_patch(Polygon([(x0, y0 + h), (x0 + d, y0 + h + d), (x0 + w + d, y0 + h + d), (x0 + w, y0 + h)],
                         closed=True, fc="white", ec="black", lw=0.9, ls=ls))
    ax.add_patch(Polygon([(x0 + w, y0), (x0 + w + d, y0 + d), (x0 + w + d, y0 + h + d), (x0 + w, y0 + h)],
                         closed=True, fc="white", ec="black", lw=0.9, ls=ls))
    ty = y0 + h - 0.08
    if stereo:
        ax.text(x0 + w / 2, ty, stereo, ha="center", va="top", fontsize=FS - 2, style="italic")
        ty -= 0.2
    ax.text(x0 + w / 2, ty, title, ha="center", va="top", fontsize=FS, fontweight="bold", linespacing=1.05)
    return dict(x=x0 + w / 2, y=y0 + h / 2, w=w, h=h, x0=x0, y0=y0)


def artifact(ax, cx, cy, w, h, text):
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="white", ec="black", lw=0.8))
    fx, fy = cx + w / 2 - 0.2, cy + h / 2 - 0.22
    ax.add_patch(Polygon([(fx, fy), (fx, fy + 0.16), (fx + 0.08, fy + 0.16), (fx + 0.12, fy + 0.12), (fx + 0.12, fy)],
                         closed=True, fc="white", ec="black", lw=0.6))
    ax.text(cx, cy + h / 2 - 0.06, "«artifact»", ha="center", va="top", fontsize=FS - 2.5, style="italic")
    ax.text(cx, cy - 0.06, text, ha="center", va="center", fontsize=FS - 0.5, linespacing=1.05)
    return dict(x=cx, y=cy, w=w, h=h)


def database(ax, cx, cy, w, h, text):
    e = 0.14
    ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), w, h, fc="white", ec="none"))
    ax.plot([cx - w / 2, cx - w / 2], [cy - h / 2, cy + h / 2], c="black", lw=0.9)
    ax.plot([cx + w / 2, cx + w / 2], [cy - h / 2, cy + h / 2], c="black", lw=0.9)
    ax.add_patch(Ellipse((cx, cy + h / 2), w, e * 2, fc="white", ec="black", lw=0.9))
    ax.add_patch(Arc((cx, cy - h / 2), w, e * 2, theta1=180, theta2=360, ec="black", lw=0.9))
    ax.text(cx, cy - 0.1, text, ha="center", va="center", fontsize=FS, linespacing=1.05)
    return dict(x=cx, y=cy, w=w, h=h)


def label(ax, x, y, text, ha="center", va="center", size=None, italic=False):
    ax.text(x, y, text, ha=ha, va=va, fontsize=size or FS - 1.5, style="italic" if italic else "normal",
            linespacing=1.0, bbox=dict(fc="white", ec="none", pad=0.8))


def arrow(ax, pts, dashed=False, head=True, text=None, tpos=None, tha="center"):
    """Polyline with an open arrowhead on the last segment."""
    ls = (0, (4, 3)) if dashed else "-"
    for a, b in zip(pts[:-2], pts[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], c="black", lw=0.8, ls=ls)
    a, b = pts[-2], pts[-1]
    style = "->,head_length=6,head_width=3.5" if head else "-"
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, lw=0.8, color="black", ls=ls, shrinkA=0, shrinkB=0))
    if text:
        label(ax, tpos[0], tpos[1], text, ha=tha)


def ball_socket(ax, p, q, name, frac=0.5, name_off=(0.12, 0.0), name_ha="left"):
    """Assembly connector: required interface (socket) on p's side meets provided (ball) on q's side."""
    mx, my = p[0] + (q[0] - p[0]) * frac, p[1] + (q[1] - p[1]) * frac
    import math
    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    r = 0.07
    # line from requirer to socket, and from ball to provider
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ax.plot([p[0], mx - ux * 0.13], [p[1], my - uy * 0.13], c="black", lw=0.8)
    ax.plot([mx + ux * r, q[0]], [my + uy * r, q[1]], c="black", lw=0.8)
    ax.add_patch(plt.Circle((mx, my), r, fc="white", ec="black", lw=0.8))
    ax.add_patch(Arc((mx, my), 0.26, 0.26, theta1=ang + 100, theta2=ang + 260, ec="black", lw=0.8))
    label(ax, mx + name_off[0], my + name_off[1], name, ha=name_ha, italic=True)


def bottom(b):
    return (b["x"], b["y"] - b["h"] / 2)


def top(b):
    return (b["x"], b["y"] + b["h"] / 2)


def left(b):
    return (b["x"] - b["w"] / 2, b["y"])


def right(b):
    return (b["x"] + b["w"] / 2, b["y"])
