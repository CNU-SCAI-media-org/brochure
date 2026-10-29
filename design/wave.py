# -*- coding: utf-8 -*-
"""원본 16쪽 머리의 라인 웨이브 그래픽을 SVG로 다시 그린다 (밴드 배경용).

사용법: python design/wave.py  →  design/wave.svg (1588×620, 투명 배경, 흰 선)
"""
import math
import os

W, H = 1588, 620
LINES = 46
paths = []
for k in range(LINES):
    t = k / (LINES - 1)
    y0 = 120 + t * 420
    amp = 70 + 90 * math.sin(t * math.pi)
    pts = []
    for i in range(0, W + 1, 16):
        x = i / W
        y = (y0 + amp * math.sin(x * 2 * math.pi * 1.15 + t * 2.2)
             + 60 * math.sin(x * 2 * math.pi * 0.45 - t * 1.4) * (1 - t))
        pts.append(f"{i},{y:.1f}")
    op = 0.18 + 0.5 * (1 - abs(t - 0.5) * 2) ** 1.4
    paths.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#FFFFFF" stroke-opacity="{op:.2f}" stroke-width="1.1"/>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
       + "".join(paths) + "</svg>")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wave.svg")
open(out, "w", encoding="utf-8").write(svg)
print(out, len(svg), "bytes")
