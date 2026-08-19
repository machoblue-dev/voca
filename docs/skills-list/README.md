# 학원업무 스킬 상세목록표 — 생성 스크립트

`docs/학원업무_스킬_상세목록표.pdf`를 만드는 소스.

## 구성
| 파일 | 역할 |
|---|---|
| `data.py` | 스킬별 내용 — 이름·상세설명·발동 문구·산출물·주의, 학원 전용 스킬의 실행 절차 |
| `style.css` | 문서 스타일. 폰트는 `@FONT_*@` 자리에 base64로 주입된다 |
| `build.py` | 측정 → 페이지 배치 → `final.html` 생성 |

## 다시 만들기
```bash
python3 build.py            # final.html 생성 (블록 높이를 브라우저로 실측해 페이지를 채운다)
chrome --headless --no-pdf-header-footer \
  --print-to-pdf=학원업무_스킬_상세목록표.pdf file://$PWD/final.html
```
- 폰트는 저장소의 `fonts/PretendardVariable.woff2`, `fonts/Paperlogy-*.woff2`를 그대로 쓴다.
- 브랜드 색은 figma-cardnews 스킬의 디자인 시스템과 같다 — 네이비 `#1B2845`, 골드 `#B5894A`, 크림 `#F2E9D4`.
- 카드 높이가 바뀌면 배치가 자동으로 다시 잡히지만, 페이지 번호는 본문이 10쪽일 때를 기준으로 박혀 있다.
  스킬을 추가·삭제해 쪽수가 달라지면 `build.py`의 `foot()` 인자를 함께 고친다.
