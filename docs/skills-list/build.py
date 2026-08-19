# -*- coding: utf-8 -*-
import base64, html, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from data import CORE, DOCS, VISUAL, COMMS, LOW, DEV, EXTRA

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FONTDIR = "/home/user/voca/fonts"
MM = 96 / 25.4  # css px per mm

def b64(p):
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

FONTS = {
    "pretendard": b64(os.path.join(FONTDIR, "PretendardVariable.woff2")),
    "paper_eb": b64(os.path.join(FONTDIR, "Paperlogy-8ExtraBold.woff2")),
    "paper_b": b64(os.path.join(FONTDIR, "Paperlogy-7Bold.woff2")),
}

CSS = open(os.path.join(HERE, "style.css"), encoding="utf-8").read()

def stars(n):
    return '<span class="st">' + '●' * n + '</span><span class="sto">' + '○' * (3 - n) + '</span>'

def card_html(s, idx, core=False):
    det = "\n".join(f"<li>{d}</li>" for d in s["detail"])
    trg = "\n".join(f'<li>{t}</li>' for t in s["triggers"])
    chip = 'core' if s['tag'] == '학원 전용' else 'gen'
    extra = f'<div class="extra">{EXTRA[s["name"]]}</div>' if s["name"] in EXTRA else ''
    return f"""<section class="card{' core' if core else ''}">
  <div class="card-head">
    <div class="num">{idx:02d}</div>
    <div class="titles"><h3>{s['name']}</h3><p class="sub">{s['ko']}</p></div>
    <div class="meta"><span class="chip chip-{chip}">{s['tag']}</span>
      <span class="rel">관련도 {stars(s['stars'])}</span></div>
  </div>
  <p class="one">{s['one']}</p>
  <div class="body">
    <div class="col-l"><h4>상세 설명</h4><ul class="detail">{det}</ul></div>
    <div class="col-r"><h4>발동 문구</h4><ul class="trig">{trg}</ul>
      <h4 class="mt">산출물</h4><p class="out">{s['out']}</p></div>
  </div>
  <div class="caution"><span class="cl">주의</span>{s['caution']}</div>
  {extra}
</section>"""

def sechead_html(title, lead, cont=False):
    t = title + (" <span class='cont'>(계속)</span>" if cont else "")
    p = f"<p>{lead}</p>" if lead and not cont else ""
    return f'<div class="sec-head"><h2>{t}</h2>{p}</div>'

# ---- build block list -------------------------------------------------
GROUPS = [
    ("1. 학원 전용 스킬",
     "기원T·학문당입시학원 업무만을 위해 직접 만든 스킬. 다른 곳에서는 쓸 수 없고, 여기서는 이것 없이 일이 돌아가지 않는다.",
     CORE, True),
    ("2. 교재·문서·데이터",
     "시험지, 성적표, 안내문, 설명회 자료 — 종이와 파일로 나가는 모든 산출물.", DOCS, False),
    ("3. 홍보·비주얼",
     "학부모와 학생에게 보이는 화면. 카드뉴스는 전용 스킬이 따로 있고, 그 밖의 시각물을 여기서 담당한다.", VISUAL, False),
    ("4. 기획·커뮤니케이션",
     "원 내부에서 돌리는 문서와 말. 강사진 공유, 커리큘럼 기획, 개념 설명.", COMMS, False),
]

blocks = []   # (kind, key, html, group_title, group_lead)
cont_blocks = []
idx = 1
for title, lead, items, core in GROUPS:
    blocks.append(("head", f"h{title[:2]}", sechead_html(title, lead), title, lead))
    cont_blocks.append((f"c{title[:2]}", sechead_html(title, lead, cont=True)))
    for s in items:
        blocks.append(("card", s["name"], card_html(s, idx, core), title, lead))
        idx += 1

# ---- measure ----------------------------------------------------------
def measure():
    allb = [(k, h) for _, k, h, _, _ in blocks] + cont_blocks
    meas = "\n".join(f'<div class="mblk" data-k="{k}">{h}</div>' for k, h in allb)
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{CSS}
    body{{width:210mm}} .mwrap{{width:180mm;padding:0;margin:0}} .mblk{{}}</style></head><body>
    <div class="mwrap">{meas}</div><pre id="M"></pre>
    <script>
      const o={{}};
      document.querySelectorAll('.mblk').forEach(function(e){{
        const c=e.firstElementChild; const st=getComputedStyle(c);
        o[e.dataset.k]=c.getBoundingClientRect().height+parseFloat(st.marginBottom||0);
      }});
      document.getElementById('M').textContent=JSON.stringify(o);
    </script></body></html>"""
    mp = os.path.join(HERE, "_measure.html")
    open(mp, "w", encoding="utf-8").write(doc.replace("@FONT_PRETENDARD@", FONTS["pretendard"])
        .replace("@FONT_PAPER_EB@", FONTS["paper_eb"]).replace("@FONT_PAPER_B@", FONTS["paper_b"]))
    out = subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                          "--virtual-time-budget=8000", "--dump-dom", "file://" + mp],
                         capture_output=True, text=True, timeout=180).stdout
    m = re.search(r'<pre id="M">(.*?)</pre>', out, re.S)
    if not m:
        print(out[-2000:]); raise SystemExit("measure failed")
    return json.loads(html.unescape(m.group(1)))

H = measure()
print("measured heights (mm):", {k: round(v / MM, 1) for k, v in H.items()})

# ---- pack -------------------------------------------------------------
PAGE_H = (297 - 16 - 13) * MM   # content box, minus footer band
pages, cur, curh, cur_group = [], [], 0.0, None
for kind, k, hml, gt, gl in blocks:
    h = H[k]
    if kind == "head":
        cur_group = (gt, gl, "c" + gt[:2])
        if cur and curh + h + 100 * MM > PAGE_H:   # head needs a card with it
            pages.append(cur); cur, curh = [], 0.0
        cur.append(hml); curh += h
        continue
    if curh + h > PAGE_H:
        pages.append(cur); cur, curh = [], 0.0
        ch = sechead_html(cur_group[0], cur_group[1], cont=True)
        cur.append(ch); curh += H[cur_group[2]]
    cur.append(hml); curh += h
if cur:
    pages.append(cur)

print("packed pages:", len(pages))
open(os.path.join(HERE, "_packed.json"), "w").write(json.dumps([len(p) for p in pages]))
PACKED = pages
open(os.path.join(HERE, "_pages.html"), "w", encoding="utf-8").write(
    "\n".join(f'<div class="page">{"".join(p)}<div class="foot"><span>학원업무 스킬 상세목록표</span>'
              f'<span>{i+3:02d}</span></div></div>' for i, p in enumerate(pages)))
print("ok")

# ---------------- assemble final document ----------------
tot = [sum(H[k] for k in []) for _ in pages]
def sumrow(s):
    chip = 'core' if s['tag'] == '학원 전용' else 'gen'
    return f"""<tr><td class="c-name"><code>{s['name']}</code><span class="ko">{s['ko']}</span></td>
      <td class="c-tag"><span class="chip chip-{chip}">{s['tag']}</span></td>
      <td class="c-rel">{stars(s['stars'])}</td><td class="c-one">{s['one']}</td></tr>"""

ALL = CORE + DOCS + VISUAL + COMMS
summary_rows = "\n".join(sumrow(s) for s in ALL)
low_rows = "\n".join(f"<tr><td><code>{n}</code></td><td>{d}</td><td class='tg'>{t}</td><td class='nt'>{note}</td></tr>"
                     for n, d, t, note in LOW)
dev_rows = "\n".join(f"<tr><td><code>{n}</code></td><td>{d}</td><td class='tg'>{t}</td></tr>" for n, d, t in DEV)

def foot(n):
    return f'<div class="foot"><span>학원업무 스킬 상세목록표 · 기원T</span><span>{n:02d}</span></div>'

body_pages = "\n".join(f'<div class="page">{"".join(p)}{foot(i+4)}</div>' for i, p in enumerate(pages))

COVER = """<div class="page cover">
  <div class="cv-orn tl"></div><div class="cv-orn br"></div>
  <div class="cv-inner">
    <div class="cv-eyebrow">CLAUDE SKILLS · REFERENCE</div>
    <div class="cv-rule"></div>
    <h1>학원업무 스킬<br><em>상세목록표</em></h1>
    <p class="cv-lead">기원T · 학문당입시학원 업무에 쓰는 모든 스킬의 이름, 하는 일, 그리고
    <b style="color:#D4B274">어떤 말을 하면 발동하는지</b>를 한 권에 정리했다.
    스킬은 이름을 몰라도 자연스러운 말에 걸리지만, 확실하게 부르려면
    <code style="background:rgba(255,255,255,.12);color:#F2E9D4">/스킬이름</code>을 치면 된다.</p>
    <div class="cv-stats">
      <div class="cv-stat"><div class="n">3</div><div class="l">학원 전용 스킬<br>직접 만들어 쓰는 것</div></div>
      <div class="cv-stat"><div class="n">16</div><div class="l">업무 활용 스킬<br>본문에서 상세 설명</div></div>
      <div class="cv-stat"><div class="n">18</div><div class="l">보조 · 개발 지원<br>부록 A · B</div></div>
    </div>
  </div>
  <div class="cv-sign"><span><b>기원T</b> · 학문당입시학원 조은희시스템영어</span><span>2026. 08. 19. 기준</span></div>
</div>"""

OVERVIEW1 = f"""<div class="page">
  <div class="sec-head"><h2>한눈에 보기</h2>
    <p>업무에 실제로 쓰는 16개 스킬. 관련도는 학원업무 기준이며 ●●●은 이것 없이 일이 돌아가지 않는 것을 뜻한다.</p></div>
  <table class="sum"><thead><tr><th>스킬</th><th>구분</th><th>관련도</th><th>하는 일</th></tr></thead>
  <tbody>{summary_rows}</tbody></table>
  <div class="legend">
    <span><b>●●●</b> 핵심 — 주 업무가 이 스킬로 돌아간다</span>
    <span><b>●●○</b> 보조 — 상황에 따라 자주 쓴다</span>
    <span><b>●○○</b> 주변 — 조건이 맞을 때만</span>
  </div>{foot(2)}</div>"""

OVERVIEW2 = f"""<div class="page">
  <div class="sec-head"><h2>부르는 법과 업무 흐름</h2>
    <p>스킬은 말에 걸리거나 이름으로 불린다. 그리고 대개 혼자 쓰이지 않고 줄줄이 이어진다.</p></div>
  <h3 class="blk">발동하는 두 가지 방법</h3>
  <p class="blkp"><b>① 자연스러운 말.</b> 각 스킬의 “발동 문구”에 있는 말을 하면 자동으로 걸린다.
  파일을 첨부하고 한 줄만 던져도 대개 잡힌다 — 지문 파일과 학교 이름을 같이 말하면
  <code>arrange-item-builder</code>가, 단어장 PDF를 붙이면 <code>voca-pdf-to-app</code>이 발동한다.<br>
  <b>② 이름으로 직접.</b> <code>/voca-pdf-to-app</code>처럼 슬래시와 스킬 이름을 치면 확실하게 그 스킬로 간다.
  말이 애매해 다른 스킬로 샐 것 같을 때 쓴다.</p>
  <h3 class="blk">업무 흐름 — 스킬은 이렇게 이어진다</h3>
  <div class="flow">
    <div class="flowrow"><div class="flowlbl">단어장 → 앱</div><div class="flowsteps">
      <span class="step">교재 PDF</span><span class="arw">▶</span><span class="step sk">voca-pdf-to-app</span><span class="arw">▶</span>
      <span class="step">누락 감사</span><span class="arw">▶</span><span class="step sk">xlsx</span><span class="arw">▶</span>
      <span class="step">TSV 붙여넣기</span><span class="arw">▶</span><span class="step">VOCA 앱</span></div></div>
    <div class="flowrow"><div class="flowlbl">시험범위 → 문항</div><div class="flowsteps">
      <span class="step">지문 .txt</span><span class="arw">▶</span><span class="step sk">arrange-item-builder</span><span class="arw">▶</span>
      <span class="step">강사 O/X 검토</span><span class="arw">▶</span><span class="step">items.json</span><span class="arw">▶</span>
      <span class="step">서답형 트레이너</span></div></div>
    <div class="flowrow"><div class="flowlbl">분석 → 홍보</div><div class="flowsteps">
      <span class="step">시험 분석 보고서</span><span class="arw">▶</span><span class="step sk">figma-cardnews</span><span class="arw">▶</span>
      <span class="step">SVG + PNG</span><span class="arw">▶</span><span class="step">Figma 편집</span><span class="arw">▶</span>
      <span class="step">인스타 캐러셀</span></div></div>
    <div class="flowrow"><div class="flowlbl">성적 → 학부모</div><div class="flowsteps">
      <span class="step">성적 원자료</span><span class="arw">▶</span><span class="step sk">xlsx</span><span class="arw">▶</span>
      <span class="step sk">dataviz</span><span class="arw">▶</span><span class="step sk">web-artifacts-builder</span><span class="arw">▶</span>
      <span class="step">학부모 리포트</span></div></div>
    <div class="flowrow"><div class="flowlbl">설명회 준비</div><div class="flowsteps">
      <span class="step">기획</span><span class="arw">▶</span><span class="step sk">doc-coauthoring</span><span class="arw">▶</span>
      <span class="step sk">pptx</span><span class="arw">▶</span><span class="step sk">theme-factory</span><span class="arw">▶</span>
      <span class="step sk">pdf</span><span class="arw">▶</span><span class="step">배포본</span></div></div>
  </div>
  <div class="note"><b>순서를 건너뛰지 않는다.</b> 두 학원 전용 스킬에는 각각 건너뛸 수 없는 관문이 하나씩 있다 —
  <code>voca-pdf-to-app</code>의 <b>누락 감사</b>와 <code>arrange-item-builder</code>의 <b>강사 O/X 검토</b>다.
  앞의 것은 단어 데이터의 오류가 학생에게 그대로 흘러가기 때문이고, 뒤의 것은 그 판단만은 기계가 못 하기 때문이다.</div>
  {foot(3)}</div>"""

APPENDIX = f"""<div class="page">
  <div class="sec-head"><h2>부록 A. 관련도가 낮은 스킬</h2>
    <p>설치되어 있지만 학원업무에서는 쓸 일이 드문 스킬. 무엇인지 알고만 있으면 된다.</p></div>
  <table class="apx"><thead><tr><th style="width:32mm">스킬</th><th style="width:50mm">하는 일</th>
    <th style="width:40mm">발동 문구</th><th>학원업무 관점</th></tr></thead><tbody>{low_rows}</tbody></table>
  <div class="sec-head" style="margin-top:7mm"><h2>부록 B. 앱 개발·운영 지원</h2>
    <p>기원T VOCA 앱(<code>index.html</code>)을 고치고 배포할 때 쓰는 도구. 수업·행정이 아니라 앱 유지보수용이다.</p></div>
  <table class="apx"><thead><tr><th style="width:40mm">스킬</th><th>하는 일</th>
    <th style="width:52mm">발동 문구</th></tr></thead><tbody>{dev_rows}</tbody></table>
  <div class="note"><b>스킬이 안 걸릴 때.</b> 말이 애매하면 스킬이 발동하지 않고 그냥 일반 답변이 나온다.
  그럴 때는 <code>/스킬이름</code>으로 직접 부른다. 반대로 같은 요청을 세 번 이상 반복하고 있는데 맞는 스킬이 없다면
  그때가 <code>skill-creator</code>로 새 스킬을 만들 시점이다 — 학원 전용 스킬 세 개도 모두 그렇게 생겼다.</div>
  {foot(14)}</div>"""

DOC = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>학원업무 스킬 상세목록표</title><style>{CSS}</style></head><body>
{COVER}
{OVERVIEW1}
{OVERVIEW2}
{body_pages}
{APPENDIX}
</body></html>"""
DOC = (DOC.replace("@FONT_PRETENDARD@", FONTS["pretendard"])
          .replace("@FONT_PAPER_EB@", FONTS["paper_eb"])
          .replace("@FONT_PAPER_B@", FONTS["paper_b"]))
outp = os.path.join(HERE, "final.html")
open(outp, "w", encoding="utf-8").write(DOC)
print("final.html written:", len(DOC))
