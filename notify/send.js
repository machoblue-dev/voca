/* ═══════════════════════════════════════════════════════════════
   VOCA꾹 알림 발송기 v1.0 — 스트릭 세이버 🔥 + 과제 마감 임박 📌
   ───────────────────────────────────────────────────────────────
   · 기존 저녁 '복습 알림'과는 별개로 도는 추가 발송기다. 복습 알림은 건드리지 않는다.
   · 안전장치 3중:
     1) 비밀키(SUPABASE_SERVICE_KEY, VAPID_PRIVATE_KEY)가 없으면 아무것도 안 보내고 조용히 끝난다.
     2) LIVE=1 이 아니면 '가상 발송' — 누구에게 무엇을 보낼지 로그로만 보여준다.
     3) 만료된 알림 주소(기기 변경 등)는 자동으로 정리한다.
   · 발송 규칙:
     - 스트릭 세이버(매일 21시 KST): 어제는 공부했는데 오늘 아직 안 한 학생에게 1통.
     - 과제 마감(매일 19시 KST): 마감까지 24시간 이내로 남은 과제를, 아직 완료 못 한 대상 학생에게 1통.
       (24시간 창 + 하루 1회 실행 = 과제당 정확히 1번만 알림이 간다)
   ═══════════════════════════════════════════════════════════════ */
'use strict';

const SB_URL = 'https://jnfkqhodwomrlfdwvtqq.supabase.co';
const VAPID_PUBLIC = 'BNyIoQozgbcFmxVir0lD0O8M5sF9iifH0XiPFI0NC0AJ3HUqzW0l8FOsFDD_GXO42dM06toNmHmvRjIp8CBfx_4';
const APP_TAG = 'voca-kkuk';

const ENV = process.env;
const TASK = (ENV.TASK || 'both').trim();            /* streak | assign | both */
const LIVE = String(ENV.LIVE || '0').trim() === '1'; /* 1이 아니면 전부 가상 발송 */

/* ── KST 시간 도구 (실행 서버가 어느 시간대든 한국 시각 기준으로 계산) ── */
const KST_MS = 9 * 3600 * 1000;
function kstParts(t) {
  const d = new Date(t + KST_MS);
  return { y: d.getUTCFullYear(), mo: d.getUTCMonth() + 1, da: d.getUTCDate(),
           h: d.getUTCHours(), mi: d.getUTCMinutes(), key: d.getUTCFullYear() + '-' + (d.getUTCMonth() + 1) + '-' + d.getUTCDate() };
}
function kstDayStart(t, offsetDays) {               /* 그 시각이 속한 KST 날짜의 00:00을 UTC 시각(ms)으로 */
  const d = new Date(t + KST_MS);
  d.setUTCHours(0, 0, 0, 0);
  return d.getTime() - KST_MS + (offsetDays || 0) * 86400000;
}

/* ── 반 대상 판정: '경신고2' 같은 정확 일치, 'N학년전체'는 반 이름 끝자리 학년 일치 ── */
function classMatches(className, targets) {
  if (!targets || !targets.length) return true;      /* 대상 미지정 = 전체 */
  const c = String(className || '').trim();
  if (!c) return false;
  return targets.some(t => {
    t = String(t || '').trim();
    const m = t.match(/^(\d)학년전체$/);
    if (m) return c.endsWith(m[1]);
    return c === t;
  });
}

/* ── 과제 완료 판정 (앱의 assignDone과 같은 규칙을 서버 쪽에서 재현) ── */
function assignDoneFor(a, userSessions) {
  const from = Date.parse(a.created_at) || 0;
  const to = Date.parse(a.due_at) || Infinity;
  const need = a.min_count || 1;
  let c = 0;
  for (const s of userSessions) {
    if (s.list_name !== a.list_name) continue;
    if (a.mode && a.mode !== 'any' && s.mode !== a.mode) continue;
    const t = Date.parse(s.created_at) || 0;
    if (t < from || t > to) continue;
    if (a.min_acc != null && a.min_acc > 0) {
      if (s.correct_count == null || !s.total) continue;
      if (Math.round(s.correct_count / s.total * 100) < a.min_acc) continue;
    }
    c++;
  }
  return c >= need;
}

/* ── 마감 임박 창: 지금부터 24시간 안에 마감하는 과제만 (과제당 1회 보장) ── */
function dueSoon(a, now) {
  const due = Date.parse(a.due_at) || 0;
  return due > now && due - now <= 24 * 3600 * 1000;
}

/* ═══ 자가 시험 — 네트워크 없이 계산 규칙만 검사 (node send.js --selftest) ═══ */
if (process.argv.includes('--selftest')) {
  const A = (name, cond) => { console.log((cond ? '  ✓ ' : '  ✗ FAIL ') + name); if (!cond) process.exitCode = 1; };
  /* KST 날짜 경계: 2026-07-27 00:30 KST = 07-26 15:30 UTC */
  const t = Date.UTC(2026, 6, 26, 15, 30);
  A('KST 날짜 인식', kstParts(t).key === '2026-7-27');
  A('KST 자정 계산', kstDayStart(t, 0) === Date.UTC(2026, 6, 26, 15, 0));
  A('어제 자정 계산', kstDayStart(t, -1) === Date.UTC(2026, 6, 25, 15, 0));
  A('반 정확 일치', classMatches('경신고2', ['경신고2']) === true);
  A('반 불일치', classMatches('경신고1', ['경신고2']) === false);
  A('학년전체 일치', classMatches('운암고2', ['2학년전체']) === true);
  A('학년전체 불일치', classMatches('운암고1', ['2학년전체']) === false);
  A('대상 미지정=전체', classMatches('동문고1', null) === true);
  const now = Date.UTC(2026, 6, 27, 10, 0);
  A('마감 23시간 전 → 발송', dueSoon({ due_at: new Date(now + 23 * 3600e3).toISOString() }, now) === true);
  A('마감 25시간 전 → 미발송', dueSoon({ due_at: new Date(now + 25 * 3600e3).toISOString() }, now) === false);
  A('마감 지난 과제 → 미발송', dueSoon({ due_at: new Date(now - 1 * 3600e3).toISOString() }, now) === false);
  const asg = { created_at: new Date(now - 5 * 86400e3).toISOString(), due_at: new Date(now + 20 * 3600e3).toISOString(),
                list_name: 'HMD 수능 Day 3', mode: 'quiz', min_acc: 80, min_count: 2 };
  const ss = (m, tot, ok, dt) => ({ list_name: 'HMD 수능 Day 3', mode: m, total: tot, correct_count: ok, created_at: new Date(now - dt).toISOString() });
  A('완료 판정: 조건 충족 2회 → 완료', assignDoneFor(asg, [ss('quiz', 10, 9, 3600e3), ss('quiz', 10, 8, 7200e3)]) === true);
  A('완료 판정: 정답률 미달 → 미완', assignDoneFor(asg, [ss('quiz', 10, 7, 3600e3), ss('quiz', 10, 6, 7200e3)]) === false);
  A('완료 판정: 모드 불일치 → 미완', assignDoneFor(asg, [ss('spell', 10, 10, 3600e3), ss('spell', 10, 10, 7200e3)]) === false);
  A('완료 판정: 기간 밖 기록 → 미완', assignDoneFor(asg, [ss('quiz', 10, 10, 10 * 86400e3), ss('quiz', 10, 9, 9 * 86400e3)]) === false);
  console.log(process.exitCode ? '자가 시험 실패' : '자가 시험 전부 통과');
  process.exit(process.exitCode || 0);
}

/* ═══ 여기서부터 실제 발송 흐름 ═══ */
async function main() {
  if (!ENV.SUPABASE_SERVICE_KEY || !ENV.VAPID_PRIVATE_KEY) {
    console.log('🔒 비밀키가 아직 설정되지 않아 발송 없이 끝냅니다. (Settings → Secrets에 SUPABASE_SERVICE_KEY, VAPID_PRIVATE_KEY 등록 후 다시)');
    return;
  }
  let webpush;
  try { webpush = require('web-push'); }
  catch (e) { console.error('web-push 모듈이 없습니다 — 워크플로의 npm install 단계를 확인하세요.'); process.exit(1); }
  webpush.setVapidDetails('mailto:voca@hakmundang.app', VAPID_PUBLIC, ENV.VAPID_PRIVATE_KEY);

  const H = { apikey: ENV.SUPABASE_SERVICE_KEY, Authorization: 'Bearer ' + ENV.SUPABASE_SERVICE_KEY };
  async function sbGet(path) {                       /* 1000행 단위로 끝까지 받아온다 */
    const out = [];
    for (let off = 0; ; off += 1000) {
      const r = await fetch(SB_URL + '/rest/v1/' + path, { headers: Object.assign({ Range: off + '-' + (off + 999), 'Range-Unit': 'items', Prefer: 'count=exact' }, H) });
      if (r.status === 404) return { missing: true, rows: out };
      if (!r.ok) throw new Error('조회 실패 ' + r.status + ' — ' + path.split('?')[0]);
      const rows = await r.json();
      out.push(...rows);
      if (rows.length < 1000) return { rows: out };
    }
  }

  /* 1) 알림 구독자 · 학생 명단 */
  const subQ = await sbGet('push_subscriptions?select=*');
  if (subQ.missing) { console.log('push_subscriptions 표가 없습니다 — 배포 가이드 4단계 상태를 확인하세요.'); return; }
  const subs = subQ.rows;
  if (!subs.length) { console.log('알림을 켠 학생이 아직 없습니다. 오늘은 보낼 곳이 없어 끝냅니다.'); return; }
  if (subs.every(s => s.user_id == null)) {
    console.log('⚠ push_subscriptions에 user_id가 비어 있어 "누구의 기기인지"를 알 수 없습니다.');
    console.log('  → Supabase에서 user_id 기본값(auth.uid()) 설정이 필요합니다. 이 상태로는 표적 알림을 보낼 수 없어 끝냅니다.');
    return;
  }
  const profQ = await sbGet('profiles?select=id,name,role,class_name,blocked');
  const stu = new Map();
  for (const p of profQ.rows) {
    if (p.role !== 'student' || p.blocked) continue;
    if (p.class_name === '퇴원' || p.class_name === '졸업') continue;
    stu.set(p.id, p);
  }
  const subsByUser = new Map();
  for (const s of subs) {
    if (!s.user_id || !stu.has(s.user_id)) continue;
    if (!subsByUser.has(s.user_id)) subsByUser.set(s.user_id, []);
    subsByUser.get(s.user_id).push(s);
  }
  console.log('구독 기기 ' + subs.length + '대 · 알림 대상 학생 ' + subsByUser.size + '명 · 모드: ' + (LIVE ? '🔴 실제 발송' : '🟡 가상 발송(로그만)'));

  /* 2) 발송 도우미 — 실패한 만료 주소는 그 자리에서 정리 */
  let sent = 0, dead = 0;
  async function pushTo(uid, title, body) {
    const p = stu.get(uid) || {};
    const label = (p.name || uid.slice(0, 6)) + '(' + (p.class_name || '반 미지정') + ')';
    for (const s of (subsByUser.get(uid) || [])) {
      if (!LIVE) { console.log('  [가상] ' + label + ' ← ' + title + ' | ' + body); sent++; continue; }
      try {
        await webpush.sendNotification({ endpoint: s.endpoint, keys: { p256dh: s.p256dh, auth: s.auth } },
          JSON.stringify({ title, body, tag: APP_TAG, url: './' }), { TTL: 6 * 3600 });
        console.log('  [발송] ' + label + ' ← ' + title);
        sent++;
      } catch (e) {
        const code = e && e.statusCode;
        if (code === 404 || code === 410) {
          dead++;
          try { await fetch(SB_URL + '/rest/v1/push_subscriptions?endpoint=eq.' + encodeURIComponent(s.endpoint), { method: 'DELETE', headers: H }); } catch (e2) {}
          console.log('  [정리] ' + label + ' — 만료된 기기 주소 삭제');
        } else console.log('  [실패] ' + label + ' — ' + (code || e.message));
      }
    }
  }

  const now = Date.now();

  /* 3) 🔥 스트릭 세이버 — 어제는 했는데 오늘 아직 안 한 학생 */
  if (TASK === 'streak' || TASK === 'both') {
    console.log('\n─ 스트릭 세이버 점검 ─');
    const ydayStart = new Date(kstDayStart(now, -1)).toISOString();
    const sess = (await sbGet('sessions?select=user_id,created_at&created_at=gte.' + encodeURIComponent(ydayStart))).rows;
    const todayStart = kstDayStart(now, 0);
    const didToday = new Set(), didYday = new Set();
    for (const s of sess) {
      const t = Date.parse(s.created_at) || 0;
      (t >= todayStart ? didToday : didYday).add(s.user_id);
    }
    const risky = [...subsByUser.keys()].filter(uid => didYday.has(uid) && !didToday.has(uid));
    console.log('오늘 학습 ' + didToday.size + '명 · 어제만 하고 오늘 빈 학생 ' + risky.length + '명');
    let streaks = new Map();
    if (risky.length) {
      const q = risky.map(encodeURIComponent).join(',');
      const prog = (await sbGet('progress?select=user_id,data&user_id=in.(' + q + ')')).rows;
      for (const r of prog) {
        const n = r && r.data && r.data.game && r.data.game.streak;
        if (n >= 1) streaks.set(r.user_id, n);
      }
    }
    for (const uid of risky) {
      const n = streaks.get(uid);
      if (!n) continue;                              /* 스트릭이 없는 학생은 재촉하지 않는다 */
      await pushTo(uid, '🔥 ' + n + '일 스트릭이 오늘 밤 사라져요!',
        '자정 전에 딱 한 판이면 지켜져요. 새 단어든 메모리 락이든, 뭐든 좋아요!');
    }
  }

  /* 4) 📌 과제 마감 임박 — 24시간 안에 마감 + 아직 미완료인 대상 학생 */
  if (TASK === 'assign' || TASK === 'both') {
    console.log('\n─ 과제 마감 점검 ─');
    const asQ = await sbGet('assignments?select=*');
    if (asQ.missing) console.log('assignments 표가 없어 과제 알림은 건너뜁니다.');
    else {
      const soon = asQ.rows.filter(a => dueSoon(a, now));
      console.log('24시간 내 마감 과제 ' + soon.length + '건');
      if (soon.length) {
        const oldest = soon.reduce((m, a) => Math.min(m, Date.parse(a.created_at) || m), now);
        const sess = (await sbGet('sessions?select=user_id,list_name,mode,total,correct_count,created_at&created_at=gte.'
          + encodeURIComponent(new Date(oldest).toISOString()))).rows;
        const byUser = new Map();
        for (const s of sess) { if (!byUser.has(s.user_id)) byUser.set(s.user_id, []); byUser.get(s.user_id).push(s); }
        for (const a of soon) {
          const due = Date.parse(a.due_at);
          const k = kstParts(due), today = kstParts(now);
          const when = (k.key === today.key ? '오늘' : '내일') + ' ' + k.h + ':' + String(k.mi).padStart(2, '0');
          let cnt = 0;
          for (const uid of subsByUser.keys()) {
            const p = stu.get(uid);
            if (!classMatches(p.class_name, a.target_classes)) continue;
            if (assignDoneFor(a, byUser.get(uid) || [])) continue;
            await pushTo(uid, '📌 과제 마감 임박', '"' + (a.title || a.list_name) + '" — ' + when + ' 마감이에요. 지금 한 판이면 끝!');
            cnt++;
          }
          console.log('· "' + (a.title || a.list_name) + '" (' + when + ' 마감) → 미완료 알림 ' + cnt + '명');
        }
      }
    }
  }

  console.log('\n요약: ' + (LIVE ? '실제 발송 ' : '가상 발송 ') + sent + '건' + (dead ? ' · 만료 주소 정리 ' + dead + '건' : ''));
}

main().catch(e => { console.error('오류로 중단: ' + e.message); process.exit(1); });
