# -*- coding: utf-8 -*-
"""src/ 목차 폴더의 PDF들로 pages/, thumbs/, brochure.pdf, index.html(PAGES 배열)을 재생성한다.

사용법:
    python build.py

규칙:
  - src/ 바로 아래 폴더가 목차 순서를 정한다 (이름의 앞 숫자 기준 정렬, 예: "05-주요사업").
  - 폴더 안 *.pdf 는 파일명 정렬 순서대로 이어진다. 여러 페이지짜리 PDF도 허용.
  - 페이지 라벨 = 파일명(확장자 제외)에서 앞의 "NN-" 접두어를 뗀 것.
    Windows 파일명에 못 쓰는 문자는 전각으로 적으면 라벨에서 원래 문자로 바뀐다: ：→ :, ／→ /
  - 출력이 실제로 바뀐 경우에만 파일을 다시 쓰고, 그때만 캐시 버전(?v=N)을 올린다.
"""
import io
import json
import os
import re
import sys

import fitz  # PyMuPDF
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
PAGES_DIR = os.path.join(ROOT, "pages")
THUMBS_DIR = os.path.join(ROOT, "thumbs")
INDEX = os.path.join(ROOT, "index.html")

A4 = fitz.paper_rect("a4")          # 595 x 842 pt
TARGET_2X = 1588                    # 렌더링 목표 가로 픽셀 (A4 2배)
JPG_QUALITY = 85
THUMB_WIDTH = 120


def label_of(filename):
    stem = os.path.splitext(filename)[0]
    stem = re.sub(r"^\d+-", "", stem)
    return stem.replace("：", ":").replace("／", "/")


def collect_sources():
    """[(pdf경로, 라벨)] 을 목차 순서대로 반환."""
    if not os.path.isdir(SRC):
        sys.exit("src/ 폴더가 없습니다.")
    out = []
    for folder in sorted(os.listdir(SRC)):
        d = os.path.join(SRC, folder)
        if not os.path.isdir(d):
            continue
        pdfs = sorted(f for f in os.listdir(d) if f.lower().endswith(".pdf"))
        if not pdfs:
            print(f"경고: {folder}/ 에 PDF가 없어 건너뜁니다.")
        for f in pdfs:
            out.append((os.path.join(d, f), label_of(f)))
    if not out:
        sys.exit("src/ 아래에 PDF가 하나도 없습니다.")
    return out


def page_jpeg(doc, page):
    """페이지의 JPG 바이트를 얻는다.

    페이지가 '전면 JPEG 이미지 한 장'뿐이면 그 바이트를 그대로 꺼내 재인코딩 손실을
    피하고, 그 외(벡터·텍스트 포함)는 2배 해상도로 렌더링한다."""
    imgs = page.get_images()
    if (len(imgs) == 1 and not page.get_drawings()
            and not page.get_text().strip()):
        info = doc.extract_image(imgs[0][0])
        if info["ext"] in ("jpeg", "jpg") and not info.get("smask"):
            iw, ih = info["width"], info["height"]
            pr = page.rect
            if abs(iw / ih - pr.width / pr.height) < 0.02:
                return info["image"], iw, ih
    zoom = TARGET_2X / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csRGB)
    return pix.tobytes("jpg", jpg_quality=JPG_QUALITY), pix.width, pix.height


def make_thumb(jpg_bytes):
    im = Image.open(io.BytesIO(jpg_bytes)).convert("RGB")
    h = round(im.height * THUMB_WIDTH / im.width)
    im = im.resize((THUMB_WIDTH, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=80, optimize=True)
    return buf.getvalue()


def write_if_changed(path, data):
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read() == data:
                return False
    with open(path, "wb") as f:
        f.write(data)
    return True


def main():
    sources = collect_sources()
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(THUMBS_DIR, exist_ok=True)

    manifest = []          # PAGES 배열 항목들
    changed = False
    merged = fitz.open()   # 통합 brochure.pdf (A4 통일)
    n = 0

    for pdf_path, label in sources:
        doc = fitz.open(pdf_path)
        for page in doc:
            n += 1
            name = f"{n:02d}.jpg"
            jpg, w, h = page_jpeg(doc, page)
            if write_if_changed(os.path.join(PAGES_DIR, name), jpg):
                changed = True
                print(f"pages/{name}  ({label}, {w}x{h})")
            if write_if_changed(os.path.join(THUMBS_DIR, name), make_thumb(jpg)):
                changed = True
            manifest.append({"src": f"pages/{name}", "thumb": f"thumbs/{name}",
                             "label": label, "w": w, "h": h})
            dst = merged.new_page(width=A4.width, height=A4.height)
            dst.show_pdf_page(dst.rect, doc, page.number)
        doc.close()

    # 남는 옛 파일 정리
    for d in (PAGES_DIR, THUMBS_DIR):
        for f in os.listdir(d):
            m = re.match(r"^(\d+)\.jpg$", f)
            if m and int(m.group(1)) > n:
                os.remove(os.path.join(d, f))
                changed = True
                print(f"삭제: {os.path.basename(d)}/{f}")

    pdf_bytes = merged.tobytes(deflate=True, garbage=3)
    merged.close()
    # PDF는 저장할 때마다 트레일러의 /ID가 무작위로 바뀌므로 그 부분만 빼고 비교
    volatile = re.compile(rb"/ID ?\[<[0-9A-Fa-f]+><[0-9A-Fa-f]+>\]")
    pdf_path = os.path.join(ROOT, "brochure.pdf")
    old = open(pdf_path, "rb").read() if os.path.exists(pdf_path) else b""
    if volatile.sub(b"", old) != volatile.sub(b"", pdf_bytes):
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        print("brochure.pdf 갱신")

    # index.html: PAGES 배열 교체, 출력이 바뀌었으면 캐시 버전 +1
    with open(INDEX, encoding="utf-8") as f:
        html = f.read()
    ver = int(re.search(r"const V='(\d+)'", html).group(1))
    if changed:
        ver += 1
        html = re.sub(r"const V='\d+'", f"const V='{ver}'", html)
        html = re.sub(r"pages/01\.jpg\?v=\d+", f"pages/01.jpg?v={ver}", html)
    pages_js = json.dumps(manifest, ensure_ascii=False)
    html2 = re.sub(r"const PAGES = \[.*?\];", f"const PAGES = {pages_js};",
                   html, count=1, flags=re.S)
    if html2 != html or changed:
        with open(INDEX, "w", encoding="utf-8", newline="") as f:
            f.write(html2)
        print(f"index.html 갱신 (v={ver})")

    print(f"완료: {n}페이지")


if __name__ == "__main__":
    main()
