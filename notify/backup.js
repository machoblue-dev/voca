/* ═══════════════════════════════════════════════════════════════
   VOCA꾹 주간 관리 로봇 v1.0 — 📦 전체 백업 → 🗜️ 기록 압축 → 🕵️ XP 감사
   ───────────────────────────────────────────────────────────────
   순서가 곧 안전장치다:
   ① 서버의 9개 표 전체를 읽어 압축 파일로 만들고, 비공개 금고(Storage 'voca-backups')에
      올린 뒤 실제로 올라갔는지 확인한다. 최근 8부만 남기고 오래된 백업은 정리한다.
   ② 백업이 확인된 경우에만, 90일 지난 학습 기록을 월별 요약으로 압축한다.
      단, 저장소 변수 ENABLE_ARCHIVE=1 이 없으면 이 단계는 잠겨 있다(대상 수만 보고).
   ③ 학습 증거(푼 문항·활동일) 대비 XP가 비정상적으로 큰 계정을 골라 보고한다.
   ④ RESEND_API_KEY와 BACKUP_EMAIL이 있으면 요약(+백업 파일 첨부)을 이메일로도 보낸다.
   ═══════════════════════════════════════════════════════════════ */
'use strict';
const zlib = require('zlib');

const SB_URL = 'https://jnfkqhodwomrlfdwvtqq.supabase.co';
const BUCKET = 'voca-backups';
const KEEP_BACKUPS = 8;

const ENV = process.env;
const SVC_KEY = (ENV.SUPABASE_SERVICE_KEY || '').trim();
const ARCHIVE_ON = String(ENV.ENABLE_ARCHIVE || '0').trim() === '1';
const KEEP_DAYS = Math.max(30, parseInt(ENV.ARCHIVE_KEEP_DAYS || '90', 10) || 90);

/* ── 열쇠 형식 판별 (send.js와 동일 규칙) ── */
function keyKind(k){
  if(!k) return 'none';
  if(k.startsWith('sb_secret_')) return 'sb_secret';
  if(k.startsWith('sb_publishable_')) return 'sb_publishable';
  const seg = k.split('.');
  if(seg.length === 3 && k.startsWith('eyJ')){
    try{ const p = JSON.parse(Buffer.from(seg[1].replace(/-/g,'+').replace(/_/g,'/'),'base64').toString());
         return p.role==='service_role' ? 'jwt_service' : (p.role==='anon' ? 'jwt_anon' : 'jwt'); }
    catch(e){ return 'jwt'; }
  }
  return 'unknown';
}
function restHeaders(k){
  const kind = keyKind(k);
  if(kind === 'jwt_service' || kind === 'jwt') return { apikey:k, Authorization:'Bearer '+k };
  return { apikey:k };
}

/* ── 백업 파일 이름 · 보관 정리 · 감사 규칙 (순수 계산 — 자가 시험 대상) ── */
function bakName(t){
  const d = new Date(t + 9*3600*1000);   /* KST */
  const p = n=>String(n).padStart(2,'0');
  return 'voca-backup-'+d.getUTCFullYear()+'-'+p(d.getUTCMonth()+1)+'-'+p(d.getUTCDate())+'-'+p(d.getUTCHours())+p(d.getUTCMinutes())+'.json.gz';
}
function pruneList(names, keep){
  const sorted = names.slice().sort().reverse();     /* 이름이 곧 시간순 */
  return sorted.slice(keep);
}
function auditCeiling(items, days){
  /* 정직하게 벌 수 있는 XP의 넉넉한 상한 — 문항당 최대치(티어2.0·탈출 포함) + 하루 고정 보너스 여유분 */
  return (items||0)*35 + (days||0)*650 + 800;
}
function auditFlag(xp, ceiling){
  return xp >= 20000 && xp > ceiling;               /* 소액·초기 계정은 건드리지 않는다 */
}

/* ═══ 자가 시험 — node backup.js --selftest ═══ */
if(process.argv.includes('--selftest')){
  const A=(n,c)=>{ console.log((c?'  ✓ ':'  ✗ FAIL ')+n); if(!c) process.exitCode=1; };
  A('백업 이름(KST)', bakName(Date.UTC(2026,6,26,18,30)) === 'voca-backup-2026-07-27-0330.json.gz');
  const names=['voca-backup-2026-07-06-0330.json.gz','voca-backup-2026-07-13-0330.json.gz','voca-backup-2026-07-20-0330.json.gz'];
  A('보관 8부 미만 → 삭제 없음', pruneList(names, 8).length===0);
  const many = Array.from({length:11},(_,i)=>'voca-backup-2026-07-'+String(i+1).padStart(2,'0')+'-0330.json.gz');
  const del = pruneList(many, 8);
  A('11부 → 오래된 3부만 삭제', del.length===3 && del.every(n=>n<='voca-backup-2026-07-03-0330.json.gz'));
  A('감사 상한 계산', auditCeiling(1000, 30) === 1000*35 + 30*650 + 800);
  A('감사: 증거 충분 → 통과', auditFlag(30000, auditCeiling(1000,30)) === false);
  A('감사: 증거 없는 거액 → 적발', auditFlag(50000, auditCeiling(100,5)) === true);
  A('감사: 소액은 면제', auditFlag(5000, 0) === false);
  const gz = zlib.gzipSync(Buffer.from('한국어 백업 시험'));
  A('압축 왕복', zlib.gunzipSync(gz).toString() === '한국어 백업 시험');
  A('열쇠 판별 재확인', keyKind('sb_secret_x')==='sb_secret' && !('Authorization' in restHeaders('sb_secret_x')));
  console.log(process.exitCode ? '자가 시험 실패' : '자가 시험 전부 통과');
  process.exit(process.exitCode || 0);
}

/* ═══ 본 작업 ═══ */
async function main(){
  if(!SVC_KEY){ console.log('🔒 SUPABASE_SERVICE_KEY가 없어 아무것도 하지 않고 끝냅니다.'); return; }
  const H = restHeaders(SVC_KEY);

  async function sbGet(path, tolerate404){
    const out = [];
    for(let off=0;;off+=1000){
      const r = await fetch(SB_URL+'/rest/v1/'+path, {headers: Object.assign({Range: off+'-'+(off+999), 'Range-Unit':'items'}, H)});
      if(r.status===404){ if(tolerate404) return {missing:true, rows:out}; throw new Error('표 없음 — '+path.split('?')[0]); }
      if(!r.ok){ let w=''; try{ w=(await r.text()).slice(0,180);}catch(e){} throw new Error('조회 실패 '+r.status+' — '+path.split('?')[0]+(w?' · '+w:'')); }
      const rows = await r.json();
      out.push(...rows);
      if(rows.length < 1000) return {rows: out};
    }
  }
  /* Storage는 문에 따라 받는 열쇠 칸이 달라 두 방식을 차례로 시도한다 */
  async function storageReq(path, opts){
    opts = opts || {};
    const tries = [ Object.assign({apikey:SVC_KEY, Authorization:'Bearer '+SVC_KEY}, opts.headers||{}),
                    Object.assign({apikey:SVC_KEY}, opts.headers||{}) ];
    let last = null;
    for(const h of tries){
      last = await fetch(SB_URL+'/storage/v1/'+path, Object.assign({}, opts, {headers: h}));
      if(last.status !== 401 && last.status !== 403) return last;
    }
    return last;
  }

  /* ── ① 전체 백업 ── */
  console.log('─ ① 전체 백업 ─');
  const TABLES = ['profiles','progress','word_lists','assignments','exams','messages','push_subscriptions','sessions','sessions_archive'];
  const snap = { app:'VOCA꾹', taken_at:new Date().toISOString(), tables:{} };
  const counts = {};
  for(const t of TABLES){
    const q = await sbGet(t+'?select=*', true);
    if(q.missing){ counts[t]='(표 없음)'; continue; }
    snap.tables[t] = q.rows; counts[t] = q.rows.length;
  }
  console.log('수집: '+Object.entries(counts).map(([k,v])=>k+' '+v).join(' · '));
  const gz = zlib.gzipSync(Buffer.from(JSON.stringify(snap)), {level: 9});
  const name = bakName(Date.now());
  console.log('압축 크기: '+(gz.length/1024/1024).toFixed(2)+'MB → '+name);

  let bk = await storageReq('bucket', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id:BUCKET, name:BUCKET, public:false})});
  if(!(bk.ok || bk.status===409 || bk.status===400)) throw new Error('금고 생성 실패 '+bk.status);
  const up = await storageReq('object/'+BUCKET+'/'+name, {method:'POST', headers:{'Content-Type':'application/gzip','x-upsert':'true'}, body: gz});
  if(!up.ok){ let w=''; try{ w=(await up.text()).slice(0,180);}catch(e){} throw new Error('백업 업로드 실패 '+up.status+' · '+w); }
  const ls = await storageReq('object/list/'+BUCKET, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prefix:'', limit:100})});
  const files = ls.ok ? (await ls.json()).map(x=>x.name) : [];
  if(!files.includes(name)) throw new Error('업로드 확인 실패 — 금고에서 방금 파일이 보이지 않습니다');
  console.log('📦 금고 보관 확인 ✓ (보관 중 '+files.length+'부)');
  const old = pruneList(files.filter(n=>n.startsWith('voca-backup-')), KEEP_BACKUPS);
  if(old.length){
    const dl = await storageReq('object/'+BUCKET, {method:'DELETE', headers:{'Content-Type':'application/json'}, body: JSON.stringify({prefixes: old})});
    console.log('오래된 백업 정리: '+old.length+'부 '+(dl.ok?'✓':'실패('+dl.status+')'));
  }

  /* ── ② 기록 압축 (백업 확인 후에만) ── */
  console.log('\n─ ② 기록 압축 ─');
  const cutoff = new Date(Date.now() - KEEP_DAYS*86400000).toISOString();
  const cr = await fetch(SB_URL+'/rest/v1/sessions?select=user_id&created_at=lt.'+encodeURIComponent(cutoff)+'&limit=1',
    {method:'HEAD', headers: Object.assign({Prefer:'count=exact'}, H)});
  const cand = parseInt((cr.headers.get('content-range')||'/0').split('/')[1], 10) || 0;
  if(!ARCHIVE_ON){
    console.log('🔒 압축 스위치 꺼짐(ENABLE_ARCHIVE≠1) — 대상 '+cand+'행을 세기만 하고 보존합니다.');
  } else if(cand === 0){
    console.log(KEEP_DAYS+'일 지난 기록 없음 — 압축할 것이 없습니다.');
  } else {
    const r = await fetch(SB_URL+'/rest/v1/rpc/archive_old_sessions', {method:'POST',
      headers: Object.assign({'Content-Type':'application/json'}, H), body: JSON.stringify({keep_days: KEEP_DAYS})});
    if(!r.ok){ let w=''; try{ w=(await r.text()).slice(0,180);}catch(e){} console.log('압축 실패 '+r.status+' · '+w+' — sustain.sql 설치 여부를 확인하세요.'); }
    else{
      const d = (await r.json())[0] || {};
      console.log('🗜️ 월별 요약 '+(d.archived_rows||0)+'묶음 저장 · 원본 '+(d.deleted_rows||0)+'행 정리 (백업에는 원본 그대로 보존됨)');
    }
  }

  /* ── ③ XP 감사 ── */
  console.log('\n─ ③ XP 감사 ─');
  const stu = new Map();
  (snap.tables.profiles||[]).forEach(p=>{ if(p.role==='student' && !p.blocked) stu.set(p.id, p); });
  const ev = new Map();   /* user → {items, days:Set|months} */
  (snap.tables.sessions||[]).forEach(s=>{
    if(!stu.has(s.user_id)) return;
    const e = ev.get(s.user_id) || {items:0, days:new Set(), extra:0};
    e.items += (s.total||0);
    e.days.add(String(s.created_at).slice(0,10));
    ev.set(s.user_id, e);
  });
  (snap.tables.sessions_archive||[]).forEach(s=>{
    if(!stu.has(s.user_id)) return;
    const e = ev.get(s.user_id) || {items:0, days:new Set(), extra:0};
    e.items += (s.total_sum||0);
    e.extra += Math.min(s.n||0, 31);
    ev.set(s.user_id, e);
  });
  const flags = [];
  (snap.tables.progress||[]).forEach(pr=>{
    const p = stu.get(pr.user_id); if(!p) return;
    const xp = (pr.data && pr.data.game && pr.data.game.xp) || 0;
    const e = ev.get(pr.user_id) || {items:0, days:new Set(), extra:0};
    const ceil = auditCeiling(e.items, e.days.size + e.extra);
    if(auditFlag(xp, ceil)) flags.push({name:p.name||'?', cls:p.class_name||'', xp, ceil, ratio: xp/Math.max(ceil,1)});
  });
  flags.sort((x,y)=>y.ratio-x.ratio);
  if(!flags.length) console.log('이상 없음 — 모든 학생의 XP가 학습 증거 범위 안입니다 ✓');
  else flags.slice(0,10).forEach(f=>console.log('⚠ '+f.name+'('+f.cls+') XP '+f.xp.toLocaleString()+' · 증거 상한 '+f.ceil.toLocaleString()+' · '+f.ratio.toFixed(1)+'배'));

  /* ── ④ 이메일 요약 (선택) ── */
  if(ENV.RESEND_API_KEY && ENV.BACKUP_EMAIL){
    const body = ['📦 VOCA꾹 주간 백업 완료 — '+name,
      '수집: '+Object.entries(counts).map(([k,v])=>k+' '+v).join(' · '),
      ARCHIVE_ON ? '기록 압축: 실행됨' : '기록 압축: 잠김(대상 '+cand+'행)',
      flags.length ? 'XP 감사 적발 '+flags.length+'명: '+flags.slice(0,5).map(f=>f.name+'('+f.ratio.toFixed(1)+'배)').join(', ') : 'XP 감사: 이상 없음'
    ].join('\n');
    const payload = { from: ENV.BACKUP_FROM || 'VOCA-KKUK <onboarding@resend.dev>',
      to: [ENV.BACKUP_EMAIL], subject: '📦 VOCA꾹 주간 백업 — '+name.slice(12,22), text: body };
    if(gz.length < 8*1024*1024) payload.attachments = [{filename: name, content: gz.toString('base64')}];
    const er = await fetch('https://api.resend.com/emails', {method:'POST',
      headers:{'Content-Type':'application/json', Authorization:'Bearer '+ENV.RESEND_API_KEY.trim()}, body: JSON.stringify(payload)});
    console.log('\n이메일 요약: '+(er.ok ? '발송 ✓ → '+ENV.BACKUP_EMAIL : '실패 '+er.status));
  }

  console.log('\n요약: 백업 ✓ · 압축 '+(ARCHIVE_ON?'✓':'잠김')+' · 감사 '+(flags.length? '⚠ '+flags.length+'명':'✓'));
}
main().catch(e=>{ console.error('오류로 중단: '+e.message); process.exit(1); });
