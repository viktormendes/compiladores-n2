from typing import Any, Dict, Tuple, List
import matplotlib.pyplot as plt


def node_label(n: Any) -> str:
    t = type(n).__name__
    if t == "Program":
        return "Program"
    if t == "FunctionDecl":
        return f"Func({getattr(n, 'name', '?')})"
    if t == "VarDecl":
        return f"VarDecl({getattr(n, 'name', '?')})"
    if t == "Assign":
        return "Assign"
    if t == "If":
        return "If"
    if t == "While":
        return "While"
    if t == "For":
        return "For"
    if t == "Return":
        return "Return"
    if t == "Block":
        return "Block"
    if t == "BinOp":
        return f"{getattr(n, 'op', '?')}"
    if t == "Call":
        return "Call"
    if t == "Index":
        return "Index"
    if t == "Var":
        return f"Id({getattr(n, 'name', '?')})"
    if t == "Num":
        return f"Num({getattr(n, 'value', '?')})"
    if t == "Char":
        return f"Char({getattr(n, 'value', '?')})"
    if t == "Str":
        return "Str"
    return t

def children(n: Any) -> List[Any]:
    t = type(n).__name__
    if t == "Program":
        return list(n.body)
    if t == "FunctionDecl":
        return [n.body]
    if t == "VarDecl":
        return [n.init] if getattr(n, "init", None) is not None else []
    if t == "Assign":
        return [n.target, n.value]
    if t == "If":
        lst = [n.test, n.then]
        if getattr(n, "otherwise", None) is not None:
            lst.append(n.otherwise)
        return lst
    if t == "While":
        return [n.test, n.body]
    if t == "For":
        out = []
        out.append(n.init)
        out.append(n.cond)
        out.append(n.step)
        out.append(n.body)
        # filter None
        return [x for x in out if x is not None]
    if t == "Return":
        return [n.value] if getattr(n, "value", None) is not None else []
    if t == "Block":
        return list(n.body)
    if t == "BinOp":
        return [n.left, n.right]
    if t == "Call":
        return [n.callee] + list(n.args)
    if t == "Index":
        return [n.target, n.index]
    return []

def _compute_layout(n: Any, x0: float = 0.0, y0: float = 0.0, y_spacing: float = 1.6) -> Tuple[Dict[int, Tuple[float, float]], float]:
    ch = [c for c in children(n) if c is not None]
    if not ch:
        return ({id(n): (x0, y0)}, 1.0)
    pos: Dict[int, Tuple[float, float]] = {}
    widths: List[float] = []
    subs: List[Any] = []
    for c in ch:
        subpos, w = _compute_layout(c, 0.0, 0.0, y_spacing)
        pos.update(subpos)
        widths.append(w)
        subs.append(c)
    total_w = sum(widths) + (len(widths) - 1) * 0.8
    cur_x = x0 - total_w / 2.0

    def shift(node: Any, dx: float, dy: float):
        x, y = pos[id(node)]
        pos[id(node)] = (x + dx, y + dy)
        for cc in children(node):
            if cc is not None:
                shift(cc, dx, dy)

    for c, w in zip(subs, widths):
        cx = cur_x + w / 2.0
        shift(c, cx, y0 - y_spacing)
        cur_x += w + 0.8

    pos[id(n)] = (x0, y0)
    return pos, total_w

def draw_tree(root: Any, filename: str, figsize=(10, 7), dpi: int = 160):
    pos, _ = _compute_layout(root, 0.0, 0.0)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_axis_off()

    def draw_edges(node: Any):
        x, y = pos[id(node)]
        for c in children(node):
            if c is None:
                continue
            xc, yc = pos[id(c)]
            ax.plot([x, xc], [y - 0.05, yc + 0.05])
            draw_edges(c)

    def draw_nodes(node: Any):
        x, y = pos[id(node)]
        bbox = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1)
        ax.text(x, y, node_label(node), ha="center", va="center", bbox=bbox, fontsize=10)
        for c in children(node):
            if c is not None:
                draw_nodes(c)

    draw_edges(root)
    draw_nodes(root)

    xs = [xy[0] for xy in pos.values()]
    ys = [xy[1] for xy in pos.values()]
    pad = 1.2
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    plt.tight_layout()
    plt.savefig(filename, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
