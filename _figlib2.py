"""论文 3 绘图共享库：一套布局 + 双渲染器（SVG 矢量源 / PIL PNG 预览）。

设计要点（来自 F5 的教训）：
  1. **文字锚点语义与 SVG 对齐**——y 是基线（PIL 用 "s" 结尾的 anchor），否则两种渲染器会有
     约一个字符高的垂直偏移，曾导致标签被画出色块外。
  2. **声明尺寸由 viewBox 推算**，保证 SVG 的 mm 尺寸与内容同比。
  3. 渲染后自动做**文字越界自检**（超出画布即报告，不静默通过）。
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
OUT = os.path.join(ROOT, "论文2_生物学", "输出")
MM_W = 174.0          # CE 单栏/整页上限 174 mm（Springer 规格）
INK = "#1a1a1a"


def wrap(text, ncols):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= ncols:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class SVGCanvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.S = float(os.environ.get("CE_FIG_SCALE", PILCanvas.S))
        self.parts = ["<svg xmlns='http://www.w3.org/2000/svg' width='%.1fmm' height='%.1fmm' "
                      "viewBox='0 0 %d %d'>" % (MM_W, MM_W * h / w, w, h),
                      "<rect width='%d' height='%d' fill='white'/>" % (w, h)]

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=1.0, dash=None, rx=0):
        a = ["stroke='%s'" % stroke if stroke else "stroke='none'", "stroke-width='%.1f'" % sw]
        if dash:
            a.append("stroke-dasharray='%s'" % dash)
        if rx:
            a.append("rx='%.1f'" % rx)
        self.parts.append("<rect x='%.1f' y='%.1f' width='%.1f' height='%.1f' fill='%s' %s/>"
                          % (x, y, w, h, fill or "none", " ".join(a)))

    def line(self, x1, y1, x2, y2, stroke, sw=1.0, dash=None):
        d = " stroke-dasharray='%s'" % dash if dash else ""
        self.parts.append("<line x1='%.1f' y1='%.1f' x2='%.1f' y2='%.1f' stroke='%s' stroke-width='%.1f'%s/>"
                          % (x1, y1, x2, y2, stroke, sw, d))

    def text(self, x, y, s, size=10, fill=INK, anchor="start", weight="normal", style=""):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append("<text x='%.1f' y='%.1f' font-family='Helvetica,Arial,sans-serif' font-size='%d' "
                          "text-anchor='%s' fill='%s' font-weight='%s'%s>%s</text>"
                          % (x, y, size, anchor, fill, weight, style, s))

    def save(self, path):
        self.parts.append("</svg>")
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(self.parts) + "\n")


class PILCanvas:
    S = float(os.environ.get("CE_FIG_SCALE", 2))

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (int(w * self.S), int(h * self.S)), "white")
        self.dr = ImageDraw.Draw(self.img)
        self.cache = {}
        self.overflow = []

    def _f(self, size, bold):
        key = (size, bold)
        if key not in self.cache:
            self.cache[key] = self._load(int(size * self.S), bold)
        return self.cache[key]

    @staticmethod
    def _load(px, bold):
        for n in (["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/msyhbd.ttc", "DejaVuSans-Bold.ttf"]
                  if bold else
                  ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/msyh.ttc", "DejaVuSans.ttf"]):
            try:
                return ImageFont.truetype(n, px)
            except Exception:
                continue
        return ImageFont.load_default()

    def rect(self, x, y, w, h, fill=None, stroke=None, sw=1.0, dash=None, rx=0):
        box = [x * self.S, y * self.S, (x + w) * self.S, (y + h) * self.S]
        if fill:
            if rx:
                self.dr.rounded_rectangle(box, radius=rx * self.S, fill=fill)
            else:
                self.dr.rectangle(box, fill=fill)
        if stroke:
            if dash:
                self._dash([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)], stroke, sw)
            else:
                if rx:
                    self.dr.rounded_rectangle(box, radius=rx * self.S, outline=stroke,
                                              width=max(1, int(sw * self.S)))
                else:
                    self.dr.rectangle(box, outline=stroke, width=max(1, int(sw * self.S)))

    def _dash(self, pts, color, sw, on=6, off=4):
        import math
        for i in range(len(pts) - 1):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            dx, dy = x2 - x1, y2 - y1
            ln = math.hypot(dx, dy)
            if ln == 0:
                continue
            t = 0.0
            while t < ln:
                t2 = min(t + on, ln)
                self.dr.line([(x1 + dx * t / ln) * self.S, (y1 + dy * t / ln) * self.S,
                              (x1 + dx * t2 / ln) * self.S, (y1 + dy * t2 / ln) * self.S],
                             fill=color, width=max(1, int(sw * self.S)))
                t = t2 + off

    def line(self, x1, y1, x2, y2, stroke, sw=1.0, dash=None):
        if dash:
            self._dash([(x1, y1), (x2, y2)], stroke, sw)
        else:
            self.dr.line([x1 * self.S, y1 * self.S, x2 * self.S, y2 * self.S],
                         fill=stroke, width=max(1, int(sw * self.S)))

    def text(self, x, y, s, size=10, fill=INK, anchor="start", weight="normal", style=""):
        # anchor 第三字母 "s" = baseline，与 SVG 的 y 语义一致
        amap = {"start": "ls", "middle": "ms", "end": "rs"}
        f = self._f(size, weight == "bold")
        self.dr.text((x * self.S, y * self.S), s, font=f, fill=fill, anchor=amap[anchor])
        bbox = self.dr.textbbox((x * self.S, y * self.S), s, font=f, anchor=amap[anchor])
        if bbox[2] > self.img.width + 1 or bbox[3] > self.img.height + 1 or bbox[0] < -1 or bbox[1] < -1:
            self.overflow.append((s[:44], tuple(round(v / self.S, 1) for v in bbox)))

    def save(self, path):
        self.img.save(path, dpi=(300, 300))


def card(c, x, y, w, h, title=None, lines=(), fill=None, stroke="#c9c9c9", title_fill=None,
         size=10, tsize=11, pad=8, lh=14, mark=None):
    """卡片：可选标题（加粗）+ 若干行正文；返回卡片底部 y。"""
    c.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1)
    yy = y + pad + tsize
    if title:
        c.text(x + pad, yy, title, tsize, title_fill or INK, weight="bold")
        yy += lh
    for ln in lines:
        c.text(x + pad, yy, ln, size, INK)
        yy += lh
    if mark:
        c.text(x + pad, y + h - pad, mark, 9, "#666666")
    return y + h


def render(name, w, h, draw_fn, verbose=True):
    name = os.environ.get("CE_FIG_NAME", name)
    svg = SVGCanvas(w, h)
    draw_fn(svg)
    p_svg = os.path.join(OUT, name + ".svg")
    svg.save(p_svg)

    png = PILCanvas(w, h)
    draw_fn(png)
    p_png = os.path.join(OUT, name + ".png")
    png.save(p_png)

    if verbose:
        print("[落盘]", p_svg)
        print("[落盘]", p_png)
        print("文字越界自检：%d 处" % len(png.overflow))
        for s, bbox in png.overflow[:6]:
            print("   !!", s, bbox)
    return p_svg, p_png, png.overflow
