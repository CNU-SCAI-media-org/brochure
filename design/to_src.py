# -*- coding: utf-8 -*-
"""design/out/pNN.png → src/ 섹션 PDF로 넣는다 (8~24쪽). 1~7쪽은 건드리지 않는다.

사용법: python design/to_src.py   (design/render.py 를 먼저 실행)
"""
import os

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUT = os.path.join(HERE, "out")
A4 = fitz.paper_rect("a4")

# (pages, src path)
PLAN = [
    ([8], "06-주요사업/01-SW중심대학.pdf"), ([9], "06-주요사업/02-BK21 plus.pdf"),
    ([10], "06-주요사업/03-정보보호 특성화대학.pdf"), ([11], "06-주요사업/04-COSS.pdf"),
    ([12], "06-주요사업/05-AI 인재양성 부트캠프.pdf"),
    ([13], "07-동아리/01-동아리 성과.pdf"), ([14], "07-동아리/02-동아리 · ANA · SPG · CRAFT：ON.pdf"),
    ([15], "07-동아리/03-동아리 · ARGOS · ADMIN · dAiv.pdf"),
    ([16], "08-연구/대학원 성과.pdf"), ([17], "09-수상/수상.pdf"), ([18], "10-학부성과/학부생 성과.pdf"),
    ([19], "11-학부소식/학부 NEWS.pdf"), ([20, 21], "12-학교행사/학교 행사.pdf"),
    ([22, 23], "13-캠퍼스/CAMPUS MOMENTS.pdf"), ([24], "14-마무리/마무리.pdf"),
]

for pages, rel in PLAN:
    doc = fitz.open()
    for n in pages:
        png = os.path.join(OUT, f"p{n:02d}.png")
        page = doc.new_page(width=A4.width, height=A4.height)
        pix = fitz.Pixmap(png)
        page.insert_image(page.rect, stream=pix.tobytes("jpg", jpg_quality=88))
    dst = os.path.join(ROOT, "src", rel)
    doc.save(dst, deflate=True, garbage=3)
    print(rel, pages)
