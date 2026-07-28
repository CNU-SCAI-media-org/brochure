# 컴퓨터인공지능학부 · 한학기 성과 모음 (웹)

주소는 이미 `https://jookite.github.io/cnu-brochure/` 로 채워져 있습니다.
아래 이름 그대로 올리면 추가 수정 없이 바로 동작합니다.

## 올리는 법 — GitHub Pages

1. github.com/new → 리포지토리 이름 **`cnu-brochure`** → **Public** → Create
2. `uploading an existing file` 클릭
3. **이 폴더 안의 내용물 전부** 드래그
   - `index.html`, `cover.jpg`, `pages` 폴더, `thumbs` 폴더
   - ⚠️ `web` 폴더째로 넣으면 주소가 `/cnu-brochure/web/` 이 되어 안 맞습니다
4. `Commit changes`
5. `Settings` → `Pages` → Source: **Deploy from a branch** → `main` / `(root)` → Save
6. 1~2분 뒤 `https://jookite.github.io/cnu-brochure/` 접속

리포지토리 이름을 `cnu-brochure`가 아닌 다른 걸로 만들면
`index.html` 위쪽 3줄(canonical, og:url, og:image)의 주소도 같이 바꿔야
카톡·인스타 미리보기가 정상적으로 뜹니다.

## 기능

- 특정 페이지 링크: 주소 끝에 `#p10` 을 붙이면 10페이지로 바로 열림
- `링크 복사` 버튼은 현재 보고 있는 페이지 주소를 복사
- 좌우 화살표 키 · 페이지 양옆 클릭 · 모바일 스와이프
- 하단 썸네일로 바로 이동
- `넘김 효과` 버튼으로 애니메이션 끄기
- 두쪽 보기에서는 실제 책처럼 낱장이 책등을 축으로 3D 회전하며 넘어감
  (표지는 오른쪽에 놓이고, 마지막 장은 왼쪽에 남는 실제 책 구조)
- `두쪽 보기` 버튼으로 펼침면(표지는 한 장, 이후 2·3, 4·5 …) 전환
  — 화면이 넓으면 자동으로 두쪽, 모바일은 한쪽으로 시작
- `PDF로 저장` 버튼으로 전체 16페이지를 `brochure.pdf` 한 파일로 다운로드
  (페이지 이미지를 교체하면 `brochure.pdf`도 다시 만들어 함께 올려야 합니다)

## 페이지를 교체하거나 추가할 때

`pages/01.jpg` ~ `pages/16.jpg` 를 같은 이름으로 덮어쓰면 됩니다.
`thumbs/` 도 같은 번호로 함께 교체해야 하단 썸네일이 맞습니다.
페이지 수가 바뀌면 `index.html` 안의 목록도 수정이 필요하니 다시 만드는 편이 빠릅니다.

## 미리보기가 안 뜰 때

카카오톡은 한 번 읽은 미리보기를 캐시합니다.
배포 전에 링크를 공유한 적이 있다면
카카오 개발자 도구(developers.kakao.com/tool/clear/og)에서 캐시를 지운 뒤 다시 공유하세요.

## 페이지를 고친 뒤 확실히 반영시키기

파일명이 같으면 브라우저·CDN 캐시 때문에 남들에게는 옛날 이미지가 보일 수 있습니다.
이미지를 덮어쓴 뒤 `index.html` 안의 `v=1` 을 `v=2` 로 바꿔서 함께 커밋하세요.
(`v=1` 은 18번째 줄 preload, 158번째 줄 스크립트 두 군데에 있습니다.)
다음에 또 고치면 3, 4 로 계속 올리면 됩니다.
