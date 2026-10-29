# -*- coding: utf-8 -*-
"""design/pNN.html 을 Chrome headless 로 1588×2246 PNG로 찍고, 검수용 비교 이미지도 만든다.

사용법:
    python design/render.py            # 모든 design/p*.html
    python design/render.py 08 16      # 지정 페이지만
출력:
    design/out/pNN.png                 # 렌더 결과
    design/out/cmp_pNN.png             # 원본(왼쪽) | 새 디자인(오른쪽) 비교
"""
import glob
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
ORIG = os.path.join(HERE, "..", "..", "content", "pages")   # scratchpad/content/pages/pNN.png (원본 2x)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1588, 2246

os.makedirs(OUT, exist_ok=True)
want = sys.argv[1:]
pages = sorted(glob.glob(os.path.join(HERE, "p*.html")))
for html in pages:
    n = os.path.basename(html)[1:3]
    if want and n not in want:
        continue
    png = os.path.join(OUT, f"p{n}.png")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--window-size={W},{H}", "--force-device-scale-factor=1",
                    f"--screenshot={png}", "file:///" + html.replace("\\", "/")],
                   capture_output=True, timeout=120)
    im = Image.open(png)
    if im.size != (W, H):
        im = im.crop((0, 0, W, H))
        im.save(png)
    orig = os.path.join(ORIG, f"p{n}.png")
    if os.path.exists(orig):
        o = Image.open(orig).convert("RGB").resize((W // 2, H // 2))
        c = Image.new("RGB", (W + 20, H // 2), "#999")
        c.paste(o, (0, 0)); c.paste(im.convert("RGB").resize((W // 2, H // 2)), (W // 2 + 20, 0))
        c.save(os.path.join(OUT, f"cmp_p{n}.png"))
    print(f"p{n}: {im.size}")
