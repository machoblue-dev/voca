# -*- coding: utf-8 -*-

CORE = [
    {
        "name": "voca-pdf-to-app",
        "ko": "단어장 PDF → VOCA 앱 변환",
        "tag": "학원 전용",
        "stars": 3,
        "one": "기원T의 단어장·어원편 교재 PDF를 기원T VOCA 앱에 바로 넣을 수 있는 데이터로 변환한다.",
        "detail": [
            "입력이 결과의 상한을 정한다. 변환 전에 <code>probe_input.py</code>로 파일의 정체를 먼저 판별한다 — <b>pdf-native</b>(좌표·폰트가 살아 있는 원본, 최상) / <b>zip-textpack</b>(페이지 이미지+텍스트, 조각 뜻은 추정) / <b>pdf-scanned</b>(텍스트 없음, 변환 불가). 확장자가 .pdf여도 진짜 PDF가 아닌 경우가 많다.",
            "양식 A~C는 라벨 인식 기반 표 엔진(<code>convert.py</code>), 양식 D는 어원편 본문 같은 교재 카드형 어댑터(<code>textbook_adapter.py</code> + <code>textbook_refine.py</code>)로 처리한다.",
            "원본 PDF가 있으면 <b>좌표로 어원 조각 뜻을 확정</b>한다. 순서 추정으로 붙이면 실제로 틀린다 — diagonal, maintain, convention, intimate가 좌표 대조로 잡힌 실제 오류다.",
            "<b>누락 감사를 통과하기 전에는 산출하지 않는다.</b> 페이지마다 해석 번호가 01…N으로 이어지므로 카드가 빠지면 번호가 미아가 된다. 미아 번호 0 + 미인식 발음 0이어야 통과. 감사를 우회하지 않는다.",
            "11컬럼 표준: 그룹 · 어휘 · 발음기호 · 의미 · 어원 · 파생어 · 동의어 · 반의어 · 혼동어 · 예문 · 해석.",
        ],
        "triggers": [
            "단어장 PDF 변환", "단어장 엑셀로", "VOCA 앱에 넣어줘", "어휘 리스트 변환",
            "스페샬특강", "어휘끝 어원편", "Etymology-based vocabulary",
            "단어장·어원편 PDF를 첨부하고 변환을 요청할 때",
        ],
        "out": "검증 완료 엑셀 마스터(.xlsx) + TSV + 리스트 내장 앱(.html)",
        "caution": "계정판 앱은 BUILTIN_ 미지원 — TSV를 리스트 관리 화면에 붙여넣는 것이 정규 배포 방법이다. 발음기호는 폰트 서브셋에 ToUnicode가 없으면 복구 불가이므로 공란으로 두고 보고한다. 추정으로 채운 값은 반드시 추정이라고 밝힌다.",
    },
    {
        "name": "arrange-item-builder",
        "ko": "지문 → 서답형 어순 배열 문항",
        "tag": "학원 전용",
        "stars": 3,
        "one": "영어 지문에서 어순 배열 문항 후보를 뽑고, 강사가 O/X로 고른 뒤 앱용 문항 데이터로 빌드한다.",
        "detail": [
            "네 단계 중 사람이 손대는 건 검토 하나다. 지문 → 후보 추출 → <b>강사 검토</b> → 빌드. 기계는 어순이 갈리는 문장은 찾아내지만 그 학교 시험에 나올지는 판단하지 못한다. 검토를 없애면 남의 앱과 똑같아진다.",
            "학교 프로파일 5종 내장 — 경신고 고2 / 능인고 고1 / 사대부고 고1 / 동문고 고2 / 오성고 고1. 정답 길이가 학교마다 자릿수로 다르다(5~7단어 ↔ 13~29단어). 한 학교 값을 다른 학교에 옮기면 후보가 통째로 어긋난다.",
            "<b>보기 어순 3중 검증.</b> ① 첫 세 단어가 정답과 같으면 탈락 ② 정답과 같은 자리 단어가 절반 이상이면 탈락 ③ 한두 개만 옮겨 정답이 되면 탈락(이동 최소 횟수 = n − 최장증가부분수열). 셋을 모두 통과할 때까지 다시 섞는다.",
            "원지문에서 앞뒤 두 문장을 찾아 붙여 학생 화면에서 그 자리만 빈칸으로 뜨게 한다. 정답 문장은 어디에도 노출되지 않는다.",
            "문장 모드(사대부·동문·오성)와 구간 모드(경신·능인) 두 갈래. 구간 모드는 검토 화면에 원문장을 함께 띄운다.",
        ],
        "triggers": [
            "배열 문항 뽑아줘", "지문에서 문장 추출", "서답형 트레이너 문항", "어순 배열 문제 만들어줘",
            "시험범위 지문으로 앱 문항", "문항 검토표 만들어줘", "arrange item / word order item",
            "학교 이름과 지문 파일을 함께 언급할 때", "지문을 붙여넣고 “문항 만들어줘”라고만 해도 발동",
        ],
        "out": "검토용 review.html → 앱 문항 items.json",
        "caution": "동문고·오성고는 보기를 낱말이 아니라 의미 덩어리로 준다. 이 스킬은 낱말 카드를 만들므로 그 형태를 재현하지 못한다 — 낱말 배열은 감각 훈련으로 쓰고 덩어리 문항은 따로 만든다. 경신고형은 빌드 뒤 우리말 제시문(ko)과 동사원형 보기를 직접 채워야 완성된다.",
    },
    {
        "name": "figma-cardnews",
        "ko": "시험 분석 → 인스타 카드뉴스",
        "tag": "학원 전용",
        "stars": 3,
        "one": "시험 분석·출제 경향 자료를 인스타그램 6장 캐러셀 카드뉴스로 만든다. Figma에서 편집 가능한 SVG + PNG 미리보기.",
        "detail": [
            "브랜드는 <b>기원T · 학문당입시학원 조은희시스템영어</b>로 고정. 캔버스는 1080×1350(4:5)에서 절대 벗어나지 않는다.",
            "6장 구성이 정해져 있다 — ① cover(네이비, 헤드라인) ② stat(큰 숫자+미니카드 3) ③ case(A vs B 비교) ④ list(번호 5행) ⑤ grid(2×2 전략) ⑥ cta(네이비, 스파인 반복+연락).",
            "<b>스파인(한 줄 메시지)</b>이 표지와 CTA를 잇는다. 6장을 만들기 전에 스파인부터 확정하고, 릴스 대본이 있으면 그 헤드라인을 그대로 쓴다.",
            "디자인 토큰 고정 — 네이비 #1B2845, 골드 #B5894A, 라이트골드 #D4B274, 크림 #F2E9D4, 마룬 #8B2F2F, 코럴 #FF8C42. 폰트는 Noto Serif KR(헤딩) · Pretendard(본문) · Playfair Display(영문 액센트). 색과 크기를 즉흥으로 정하지 않는다.",
            "톤은 차분·정확·전문가. 단문체(-임/-이다), 느낌표 없음, 이모지 없음.",
        ],
        "triggers": [
            "카드뉴스 만들어줘", "인스타 캐러셀 / instagram carousel", "이번 시험 분석을 카드뉴스로",
            "피그마에서 쓸 거 / 피그마 import용", "이거 카드뉴스로", "인스타에 올릴 거",
            "분석 보고서를 첨부하고 시각화를 요청할 때", "릴스 대본에 맞춰서 만들어줘",
        ],
        "out": "page_01~06 SVG + 동일 PNG + 3×2 그리드 프리뷰",
        "caution": "편집 원칙 — “중간고사에 안 나온 지문이 기말에 나온다”는 식의 주장은 절대 쓰지 않는다. 한국 고교 시험은 매 시험 새 범위를 잡는다. 원자료가 그렇게 말해도 “기말 대비 학습 전략”으로 완화한다. 한글에 italic 금지, 영문 전용 폰트로 한글을 쓰면 빈 네모가 된다.",
    },
]

DOCS = [
    {
        "name": "xlsx", "ko": "스프레드시트 제작·편집", "tag": "문서·데이터", "stars": 3,
        "one": "성적 집계표, 단어 마스터, 출결·명단, 수강료 정산 등 표 형태 산출물 전담.",
        "detail": [
            "openpyxl(수식·서식) / pandas(대량 데이터) / markitdown(빠른 확인)로 갈라 쓴다. 모두 사전 설치되어 있다.",
            "<b>결과값이 아니라 수식을 쓴다.</b> <code>=SUM(B2:B9)</code>를 넣지 파이썬으로 계산한 합계를 박지 않는다. 입력이 바뀌면 시트가 다시 계산되어야 한다.",
            "수식이 있으면 LibreOffice 재계산(<code>recalc.py</code>)이 필수. 오류가 하나라도 남으면 산출하지 않는다.",
            "기존 파일을 편집할 때는 그 파일의 관행이 모든 가이드보다 우선한다. 입력 셀(글자색·채우기로 표시된 자리)만 건드리고 기존 수식은 손대지 않는다.",
        ],
        "triggers": ["엑셀로 만들어줘", "성적표 / 명단 / 정산표", ".xlsx · .csv · .tsv 파일 언급", "표 정리해줘", "수식 넣어줘", "/xlsx"],
        "out": ".xlsx / .csv / .tsv",
        "caution": "산출물이 워드·HTML 리포트·파이썬 스크립트라면 이 스킬이 아니다.",
    },
    {
        "name": "docx", "ko": "워드 문서 제작·편집", "tag": "문서·데이터", "stars": 3,
        "one": "가정통신문, 학원 안내문, 학습 계획서, 공문·계약서 등 워드 산출물.",
        "detail": [
            "새로 만들 때는 docx-js(Node), 기존 파일 편집은 unzip → <code>word/document.xml</code> 수정 → zip, 읽기는 <code>pandoc -t markdown</code>.",
            "표는 표 <code>columnWidths</code>와 각 셀 <code>width</code>를 둘 다 DXA로 지정해야 구글 문서에서 깨지지 않는다.",
            "목차(TOC)를 넣으려면 제목이 내장 HeadingLevel을 써야 한다. 줄바꿈에 <code>\\n</code>을 쓰지 않고 문단을 나눈다.",
            "작성 후 PDF로 변환해 이미지로 렌더해서 눈으로 확인하는 절차가 포함되어 있다.",
        ],
        "triggers": ["워드로 만들어줘", "가정통신문 / 안내문 / 공문", ".docx · .dotx 언급", "레터헤드 · 목차 · 페이지 번호", "/docx"],
        "out": ".docx / .dotx",
        "caution": "PDF·스프레드시트·구글 문서가 목적이면 각각 pdf·xlsx 스킬로 간다.",
    },
    {
        "name": "pptx", "ko": "슬라이드 덱 제작·편집", "tag": "문서·데이터", "stars": 3,
        "one": "학부모 설명회 자료, 입시 설명회 덱, 수업용 슬라이드.",
        "detail": [
            "새 덱은 pptxgenjs, 기존 덱·템플릿 기반은 XML 직접 편집, 읽기는 markitdown 또는 슬라이드 썸네일 그리드.",
            "<code>pres.layout</code>을 슬라이드 추가 전에 정한다. 기본 캔버스는 10″×5.625″라 좌표가 밖으로 나가면 도형이 그냥 사라진다.",
            "색상 헥스에 <code>#</code>이나 알파 8자리를 쓰면 <b>파일이 깨진다</b>. 투명도는 별도 옵션으로.",
            "차트는 이미지로 넣지 않고 네이티브 차트로 넣는다. 기본 차트는 제목·데이터라벨·팔레트를 직접 지정해야 보여줄 만해진다.",
        ],
        "triggers": ["PPT 만들어줘", "설명회 자료 / 발표자료", "슬라이드 · 덱 · 프레젠테이션", ".pptx · .potx 언급", "/pptx"],
        "out": ".pptx (+ 검증 리포트, PDF 변환본)",
        "caution": "발표자 노트는 슬라이드 위 텍스트 상자가 아니라 addNotes로 넣는다.",
    },
    {
        "name": "pdf", "ko": "PDF 처리·생성", "tag": "문서·데이터", "stars": 3,
        "one": "시험지·교재 PDF의 병합·분할·회전·워터마크·암호화, 텍스트/표 추출, 스캔본 OCR, 배포용 PDF 생성.",
        "detail": [
            "pypdf로 병합·분할·회전·워터마크·암호화, pdfplumber로 표와 좌표 추출, OCR로 스캔 시험지를 검색 가능하게 만든다.",
            "PDF 양식(폼) 채우기는 별도 절차(FORMS.md)를 따른다.",
            "voca-pdf-to-app이 교재 PDF를 다루기 전 단계로 이 스킬의 도구를 함께 쓴다.",
            "<b>지금 보고 있는 이 목록표도 이 스킬로 만들었다.</b>",
        ],
        "triggers": ["PDF로 만들어줘", "PDF 합쳐줘 / 나눠줘", "PDF에서 텍스트·표 뽑아줘", "워터마크 넣어줘", "스캔본 OCR", "/pdf"],
        "out": ".pdf (또는 추출된 텍스트·표·이미지)",
        "caution": "스캔 PDF는 OCR 전에는 텍스트가 없다. 원본 PDF가 있으면 항상 원본을 쓴다.",
    },
]

VISUAL = [
    {
        "name": "dataviz", "ko": "데이터 시각화", "tag": "홍보·비주얼", "stars": 2,
        "one": "성적 추이, 정답률, 오답 분포 등 모든 차트·그래프·대시보드의 설계 기준.",
        "detail": [
            "차트 코드를 한 줄이라도 쓰기 전에 먼저 읽는 스킬. 매체(HTML·SVG·matplotlib·Recharts·이미지) 무관하게 적용된다.",
            "형태 선택 휴리스틱, 검증 가능한 색상 공식, 마크 규격, 인터랙션 규칙을 제공해 여러 그래프가 <b>하나의 시스템</b>으로 읽히게 한다.",
            "라이트/다크 양쪽에서 접근성이 유지되는 팔레트를 기본으로 준다.",
        ],
        "triggers": ["차트 / 그래프 / 플롯", "성적 추이 그래프", "정답률 시각화", "대시보드", "히트맵 · 스파크라인 · 범례", "/dataviz"],
        "out": "차트·대시보드 (아티팩트 / 이미지 / 코드)",
        "caution": "차트를 만들기 전에 반드시 먼저 로드한다. 나중에 색만 바꾸는 식으로는 시스템이 잡히지 않는다.",
    },
    {
        "name": "design", "ko": "디자인 캔버스", "tag": "홍보·비주얼", "stars": 2,
        "one": "여러 아트보드를 한 캔버스에 펼친 시안. 클릭 편집·PNG/PDF 내보내기가 되는 아티팩트로 발행된다.",
        "detail": [
            "포스터·전단·브로슈어는 단일 아트보드, 안내문·리포트는 한 장으로 흐르는 아트보드로 만든다.",
            "UI 목업, 화면 흐름, 랜딩 페이지, 배너, 카드, 원페이저에 쓴다.",
            "새 캔버스를 만들거나 다시 씨앗을 뿌릴 때만 쓴다. 이미 발행된 캔버스는 그 아티팩트 안에서 편집한다.",
        ],
        "triggers": ["시안 만들어줘", "목업 / 와이어프레임", "포스터 · 전단 · 브로슈어 디자인", "랜딩페이지", "/design"],
        "out": "다중 아트보드 캔버스 아티팩트 (PNG/PDF 내보내기)",
        "caution": "figma-cardnews가 담당하는 인스타 카드뉴스와는 목적이 다르다. 브랜드 고정 산출물은 figma-cardnews로 간다.",
    },
    {
        "name": "canvas-design", "ko": "포스터·아트 제작", "tag": "홍보·비주얼", "stars": 2,
        "one": "디자인 철학을 먼저 세우고 그것을 .png / .pdf 한 장으로 표현하는 정적 비주얼 작업.",
        "detail": [
            "두 단계다 — ① 미학적 선언(디자인 철학 .md) ② 캔버스 위 표현(.pdf 또는 .png).",
            "레이아웃 템플릿이 아니라 형태·여백·색·구성으로 말하는 결과물을 목표로 한다. 텍스트는 시각 액센트 수준(90% 비주얼 / 10% 텍스트).",
            "학원 홍보 포스터, 특강 안내 비주얼, 표지 아트에 쓴다.",
        ],
        "triggers": ["포스터 만들어줘", "전단지 디자인", "아트워크 / 표지", "/canvas-design"],
        "out": ".md(철학) + .pdf / .png",
        "caution": "기존 작가의 작업을 모사하지 않고 항상 원본 디자인을 만든다.",
    },
    {
        "name": "theme-factory", "ko": "테마 통일", "tag": "홍보·비주얼", "stars": 2,
        "one": "슬라이드·문서·리포트·HTML에 10종 프리셋 테마(색·폰트)를 일괄 적용하거나 새 테마를 즉석에서 만든다.",
        "detail": [
            "Ocean Depths, Sunset Boulevard, Forest Canopy, Modern Minimalist, Golden Hour, Arctic Frost, Desert Rose, Tech Innovation, Botanical Garden, Midnight Galaxy 10종.",
            "테마 쇼케이스 PDF를 먼저 보여주고 선택을 받은 뒤에 적용한다.",
            "설명회 덱과 배포 문서의 톤을 한 번에 맞출 때 유용하다.",
        ],
        "triggers": ["테마 적용해줘", "스타일 통일", "이 덱 예쁘게", "/theme-factory"],
        "out": "테마가 적용된 기존 산출물",
        "caution": "학원 브랜드 아이덴티티(네이비·골드)는 figma-cardnews의 디자인 시스템이 정본이다.",
    },
    {
        "name": "web-artifacts-builder", "ko": "복합 웹 아티팩트", "tag": "홍보·비주얼", "stars": 2,
        "one": "React·Tailwind·shadcn/ui 기반의 상태 관리·라우팅이 필요한 복합 HTML 산출물.",
        "detail": [
            "학부모용 인터랙티브 성적 리포트, 원내 운영 대시보드, 여러 화면을 오가는 도구에 쓴다.",
            "단일 파일 HTML/JSX 정도로 끝나는 간단한 아티팩트에는 쓰지 않는다 — 과한 도구다.",
        ],
        "triggers": ["웹페이지로 만들어줘", "인터랙티브 리포트", "대시보드 만들어줘", "/web-artifacts-builder"],
        "out": "다중 컴포넌트 HTML 아티팩트",
        "caution": "간단한 한 장짜리는 그냥 HTML로 만드는 편이 빠르다.",
    },
]

COMMS = [
    {
        "name": "doc-coauthoring", "ko": "문서 공동 집필", "tag": "기획·커뮤니케이션", "stars": 2,
        "one": "커리큘럼 기획서·운영 제안서·결정 문서를 3단계로 함께 쓴다.",
        "detail": [
            "① 맥락 수집(질문으로 머릿속을 꺼냄) ② 구조화·다듬기(섹션별 반복) ③ <b>독자 테스트</b>(맥락 없는 새 Claude에게 읽혀 빈틈을 찾음).",
            "혼자 쓰면 빠지는 전제를 3단계에서 잡아낸다. 남에게 보낼 문서일수록 값이 크다.",
        ],
        "triggers": ["기획서 같이 써줘", "제안서 초안", "스펙 · PRD · 결정 문서", "문서 정리해줘", "/doc-coauthoring"],
        "out": "완성 문서(md) + 독자 테스트 피드백",
        "caution": "사용자가 원하지 않으면 자유 형식으로 바로 쓴다.",
    },
    {
        "name": "internal-comms", "ko": "내부 커뮤니케이션", "tag": "기획·커뮤니케이션", "stars": 2,
        "one": "강사진 주간 업데이트, 원내 공지, FAQ, 사건 보고 등 내부 소통 문서.",
        "detail": [
            "3P 업데이트(Progress / Plans / Problems), 뉴스레터, FAQ 답변, 일반 공지 네 가지 양식 파일을 갖고 있다.",
            "요청에서 문서 유형을 먼저 식별하고 해당 가이드라인을 로드해 형식·톤을 맞춘다.",
        ],
        "triggers": ["주간 보고 써줘", "3P 업데이트", "공지 작성", "FAQ 정리", "뉴스레터", "/internal-comms"],
        "out": "내부 공유용 텍스트/문서",
        "caution": "양식에 없는 유형이면 형식을 먼저 확인하고 쓴다.",
    },
    {
        "name": "learn", "ko": "학습·튜터링 모드", "tag": "기획·커뮤니케이션", "stars": 2,
        "one": "답을 주는 대신 스스로 답할 수 있게 만드는 튜터링 모드. 강사 연수, 개념 정리, 퀴즈·플래시카드.",
        "detail": [
            "가르치기 전에 <b>진단</b>한다 — 개념이 막힌 건지, 절차인지, 표기인지, 문제 자체를 못 읽은 건지. 계산 질문 하나로 위치를 먼저 잡는다.",
            "매 턴 초점 질문 하나 + 앞으로 나아가게 하는 작은 발판 하나. 질문 폭탄도, 빈손 턴도 없다.",
            "문법 개념 정리, 신입 강사 연수 자료, 학생 설명 스크립트 만들기에 쓸 수 있다.",
        ],
        "triggers": ["설명해줘 / 가르쳐줘", "ELI5 · 쉽게 풀어줘", "퀴즈 내줘 · 플래시카드", "이거 자꾸 헷갈려", "무엇부터 공부해야 해?", "/learn"],
        "out": "대화형 튜터링 (문서 산출은 별도)",
        "caution": "코딩·번역·계산 같은 <b>작업</b> 요청에는 발동하지 않는다. 의견을 묻는 질문에도 발동하지 않는다.",
    },
    {
        "name": "morning", "ko": "모닝 브리핑", "tag": "기획·커뮤니케이션", "stars": 1,
        "one": "그날의 일정·메일을 정리한 아침 브리핑을 HTML 아티팩트로 렌더하거나 평일 반복 작업으로 설정한다.",
        "detail": [
            "명시적으로 요청했을 때만 동작한다. 일정에 대한 단순 질문은 그냥 답한다.",
            "캘린더·메일 커넥터가 연결되어 있어야 값이 있다.",
        ],
        "triggers": ["/morning", "모닝 브리핑 보여줘", "아침 브리핑 매일 아침에 띄워줘"],
        "out": "브리핑 HTML 아티팩트 / 반복 작업 등록",
        "caution": "“오늘 일정 뭐야?”는 브리핑 요청이 아니다.",
    },
    {
        "name": "skill-creator", "ko": "스킬 제작·개선", "tag": "기획·커뮤니케이션", "stars": 2,
        "one": "반복되는 학원업무를 새 스킬로 굳히거나 기존 스킬을 개선·평가한다.",
        "detail": [
            "스킬 신규 작성, 편집·최적화, 평가(eval) 실행, 발동 문구(description) 정확도 개선을 담당한다.",
            "voca-pdf-to-app · arrange-item-builder · figma-cardnews 세 학원 전용 스킬도 이 방식으로 만들고 다듬는다.",
            "같은 요청을 세 번 이상 하고 있다면 스킬로 만들 시점이다.",
        ],
        "triggers": ["스킬 만들어줘", "이 작업 스킬로 굳혀줘", "스킬 개선 / 발동이 잘 안 돼", "/skill-creator"],
        "out": "SKILL.md + scripts/ + references/",
        "caution": "발동 문구가 부정확하면 스킬이 있어도 안 걸린다. 실제로 쓰는 말을 그대로 넣는다.",
    },
]

LOW = [
    ("brand-guidelines", "Anthropic 공식 브랜드 컬러·타이포 적용", "“브랜드 가이드 적용”, /brand-guidelines", "Anthropic 브랜드용이라 학원 아이덴티티에는 맞지 않는다. 학원 브랜드는 figma-cardnews의 디자인 시스템이 정본."),
    ("algorithmic-art", "p5.js 제너러티브 아트 (시드 기반)", "“제너러티브 아트”, “코드로 그림”, /algorithmic-art", "배경 그래픽 소재 정도로만 쓸 여지가 있다."),
    ("slack-gif-creator", "Slack용 애니메이션 GIF 제작", "“슬랙용 GIF 만들어줘”, /slack-gif-creator", "학원에서 Slack을 쓰지 않으면 해당 없음."),
    ("mcp-builder", "MCP 서버 개발 가이드 (Python/TS)", "“MCP 서버 만들어줘”, /mcp-builder", "외부 서비스를 앱에 연동할 때만."),
]

DEV = [
    ("code-review", "변경된 코드의 버그·중복·비효율 리뷰", "/code-review"),
    ("security-review", "브랜치 변경분 보안 점검", "/security-review"),
    ("simplify", "변경 코드 정리·단순화 후 반영", "/simplify"),
    ("run", "앱을 실제로 띄워 변경 동작 확인·스크린샷", "/run"),
    ("init", "CLAUDE.md 생성 — 저장소 문서화", "/init"),
    ("session-start-hook", "웹 세션에서 테스트·린트가 돌게 저장소 준비", "/session-start-hook"),
    ("update-config", "권한·훅·환경변수 등 settings.json 설정", "“npm 명령 허용해줘”, /update-config"),
    ("keybindings-help", "단축키 커스터마이즈", "“단축키 바꿔줘”, /keybindings-help"),
    ("loop", "지정 주기로 작업 반복 실행", "/loop 10m …"),
    ("claude-api", "Claude API·모델·가격·캐싱 레퍼런스", "모델/가격/토큰 질문 시 자동"),
    ("artifact-design", "아티팩트 디자인 기준 (발행 전 필수)", "아티팩트 작성 시 자동"),
    ("artifact-diagramming", "아티팩트용 다이어그램 SVG 작법", "다이어그램 필요 시 자동"),
    ("artifact-capabilities", "아티팩트 런타임 기능(실시간 데이터·저장 등)", "동적 아티팩트 요청 시 자동"),
    ("fewer-permission-prompts", "반복되는 권한 프롬프트를 허용목록으로 축소", "/fewer-permission-prompts"),
]

# ---- 학원 전용 스킬의 실행 절차 / 부가 표 -------------------------------
EXTRA = {
"voca-pdf-to-app": """
<h4>실행 절차</h4>
<pre class="cmd"><span class="cm"># ① 입력의 정체부터 — 결과의 상한이 여기서 정해진다</span>
python3 scripts/probe_input.py 입력.pdf
<span class="cm"># ② 추출 (양식 D · 어원편). DAY 시작 페이지를 환경변수로 지정</span>
export VOCA_PAGES=/path/pages VOCA_STARTS=1,10,18,… VOCA_DAY_BASE=11
python3 scripts/textbook_refine.py 1 83 cards.json
<span class="cm"># ③ 누락 감사 — 미아 번호 0 + 미인식 발음 0이어야 다음으로 간다</span>
python3 scripts/audit.py cards.json
<span class="cm"># ④ 어원 조각 뜻을 좌표로 확정 (원본 PDF가 있을 때만)</span>
python3 scripts/pdf_etym.py 원본.pdf pdf_etym.json
python3 scripts/apply_pdf_etym.py cards.json pdf_etym.json cards2.json
<span class="cm"># ⑤ 산출</span>
python3 scripts/make_xlsx.py final.json "리스트명" 출력.xlsx</pre>
<table class="mini">
<thead><tr><th>입력 종류</th><th>정체</th><th>할 수 있는 것</th></tr></thead>
<tbody>
<tr><td><code>pdf-native</code></td><td>좌표·폰트가 살아 있는 원본</td><td>표제어·조각 뜻을 위치로 확정 — 최상</td></tr>
<tr><td><code>zip-textpack</code></td><td>페이지 이미지 + 텍스트 묶음</td><td>변환은 되나 조각 뜻은 추정, 발음기호 복구 불가</td></tr>
<tr><td><code>pdf-scanned</code></td><td>텍스트 없음</td><td>불가 → 원본 PDF를 요청한다</td></tr>
</tbody></table>""",

"arrange-item-builder": """
<h4>실행 절차</h4>
<pre class="cmd"><span class="cm"># ① 후보 뽑기 — 학교 이름은 한글로 넣어도 잡힌다</span>
python3 scripts/extract.py 지문.txt --school 사대부고 --out review.html
<span class="cm"># ② review.html을 브라우저로 열어 문장마다 O/X. 100문장에 10분.</span>
<span class="cm">#    다 고르면 “확정 내보내기” → confirmed.json 으로 저장</span>
<span class="cm"># ③ 빌드 — 보기 재섞기·3중 검증·문맥 첨부가 여기서 자동으로 돈다</span>
python3 scripts/build.py confirmed.json --passages 지문.txt --out items.json</pre>
<table class="mini">
<thead><tr><th>학교</th><th>모드</th><th>정답 길이</th><th>배열 훈련의 무게</th></tr></thead>
<tbody>
<tr><td>경신고 고2</td><td>구간</td><td>5~7단어</td><td>형태 그대로 일치. 이 자리 셋이 1↔2등급을 갈랐다</td></tr>
<tr><td>능인고 고1</td><td>구간</td><td>5~10단어</td><td>보기와 정답 단어 수가 같은 순수 배열</td></tr>
<tr><td>사대부고 고1</td><td>문장</td><td>4~12단어</td><td>서답형 8문항 35점 전부 조건 영작 — 가장 무겁다</td></tr>
<tr><td>동문고 고2</td><td>문장</td><td>15단어</td><td>순수 배열 + 다조건형이 한 시험에 같이 나온다</td></tr>
<tr><td>오성고 고1</td><td>문장</td><td>13~29단어</td><td>조건 영작은 두 자리, 대신 정답이 가장 길다</td></tr>
</tbody></table>""",

"figma-cardnews": """
<h4>6장 구성 (이 순서를 벗어나지 않는다)</h4>
<table class="mini">
<thead><tr><th>#</th><th>타입</th><th>배경</th><th>역할</th></tr></thead>
<tbody>
<tr><td>1</td><td><code>cover</code></td><td>다크 네이비</td><td>큰 헤드라인 + 스파인. 스크롤을 멈추게 한다</td></tr>
<tr><td>2</td><td><code>stat</code></td><td>라이트 크림</td><td>거대한 숫자 하나 + 핵심 주장 + 미니카드 3</td></tr>
<tr><td>3</td><td><code>case</code></td><td>라이트 크림</td><td>A vs B 비교 (원문 vs 시험, 전 vs 후)</td></tr>
<tr><td>4</td><td><code>list</code></td><td>라이트 크림</td><td>번호 붙은 5행 (패턴·규칙·실수)</td></tr>
<tr><td>5</td><td><code>grid</code></td><td>라이트 크림</td><td>2×2 전략 카드</td></tr>
<tr><td>6</td><td><code>cta</code></td><td>다크 네이비</td><td>스파인 반복 + 제공 타일 2 + 연락 CTA</td></tr>
</tbody></table>
<h4 class="mt">브랜드 토큰 (즉흥 금지)</h4>
<div class="sw">
<span class="s" style="background:#1B2845;color:#F2E9D4">네이비 #1B2845</span>
<span class="s" style="background:#B5894A;color:#fff">골드 #B5894A</span>
<span class="s" style="background:#D4B274;color:#3a2c12">라이트골드 #D4B274</span>
<span class="s" style="background:#F2E9D4;color:#4a3a1c">크림 #F2E9D4</span>
<span class="s" style="background:#8B2F2F;color:#fff">마룬 #8B2F2F</span>
<span class="s" style="background:#FF8C42;color:#4a2000">코럴 #FF8C42</span>
</div>
<p class="tiny">캔버스 1080×1350 고정 · 좌우 여백 80px · 헤딩 Noto Serif KR · 본문 Pretendard · 영문 액센트 Playfair Display</p>""",
}
