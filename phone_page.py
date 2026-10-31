# The page the phone opens after scanning the QR code.
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover, interactive-widget=resizes-content">
<meta name="theme-color" content="#0b0e1c">
<title>Phone Keyboard</title>
<style>
  :root{
    --red:#ff6b7f; --amber:#ffb347; --green:#38e0a0; --teal:#2fd3d8; --blue:#5aa5ff;
    --violet:#a583ff; --pink:#ff7ad1; --slate:#9aa7c7;
    --ink:#eef1ff; --muted:#8e99bd;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;width:100%;height:100%;overflow:hidden;background:
    radial-gradient(90% 45% at 0% 0%,rgba(125,92,255,.30),transparent 62%),
    radial-gradient(80% 45% at 100% 100%,rgba(47,211,216,.20),transparent 62%),#0b0e1c;
    color:var(--ink);overscroll-behavior:none;touch-action:manipulation;
    font-family:ui-rounded,"SF Pro Rounded","Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
  #app{position:fixed;left:0;top:0;width:100%;height:100dvh;display:flex;flex-direction:column;gap:10px;
    padding:max(10px,env(safe-area-inset-top)) 12px max(10px,env(safe-area-inset-bottom))}
  #app.kb{padding-bottom:8px;gap:8px}

  /* header */
  header{flex:none;display:flex;align-items:center;justify-content:space-between;padding:0 2px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;letter-spacing:.2px}
  .logo{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;
    background:linear-gradient(135deg,var(--violet),var(--blue));box-shadow:0 4px 14px rgba(125,92,255,.45)}
  .logo svg{width:19px;height:19px;color:#0b0e1c}
  .status{display:flex;align-items:center;gap:7px;font-size:12.5px;font-weight:700;color:var(--muted);
    background:rgba(255,255,255,.07);padding:7px 12px;border-radius:999px}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--red)}
  .status.on{color:var(--ink)}
  .status.on .dot{background:var(--green);box-shadow:0 0 0 4px rgba(56,224,160,.22)}

  /* text card */
  .card{flex:1 1 0;min-height:64px;position:relative;display:flex;flex-direction:column;border-radius:22px;
    padding:10px 14px 8px;background:linear-gradient(rgba(255,255,255,.10),rgba(255,255,255,.05));
    box-shadow:inset 0 1px 0 rgba(255,255,255,.14),0 10px 30px rgba(0,0,0,.35);overflow:hidden}
  .card::before{content:"";position:absolute;left:0;top:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--violet),var(--blue),var(--teal))}
  .cardtop{display:flex;align-items:center;justify-content:space-between;font-size:11.5px;font-weight:800;
    letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);margin-bottom:2px}
  .tools{display:flex;gap:6px}
  .tool{width:34px;height:30px;border:0;border-radius:10px;display:grid;place-items:center;color:var(--ink);
    background:rgba(255,255,255,.10)}
  .tool svg{width:18px;height:18px}
  .tool:active{background:rgba(255,255,255,.2)}
  textarea{flex:1;min-height:0;width:100%;resize:none;border:0;outline:0;background:transparent;color:#fff;
    font:inherit;font-size:21px;line-height:1.35;padding:0;caret-color:var(--teal)}
  .hint{position:absolute;inset:34px 0 0 0;display:grid;place-items:center;color:var(--muted);font-weight:700;
    font-size:15px;pointer-events:none;text-align:center;padding:0 20px}
  .hint.hide{display:none}

  /* key panel */
  .panel{flex:none;height:clamp(190px,44%,292px)}
  .keys{display:none;height:100%;grid-template-columns:repeat(12,1fr);grid-auto-rows:minmax(0,1fr);gap:7px}
  .keys.show{display:grid}

  .k{--c:var(--slate);min-height:0;min-width:0;height:100%;border:0;border-radius:15px;padding:0 4px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;
    font:inherit;font-weight:800;font-size:14px;color:color-mix(in srgb,var(--c) 62%,#fff);
    background:linear-gradient(color-mix(in srgb,var(--c) 30%,#1d233f),color-mix(in srgb,var(--c) 15%,#151a31));
    box-shadow:inset 0 1px 0 rgba(255,255,255,.16),0 3px 0 color-mix(in srgb,var(--c) 50%,#070a14),0 7px 12px rgba(0,0,0,.35);
    user-select:none;-webkit-user-select:none;transition:transform .05s,box-shadow .05s}
  .k:active{transform:translateY(3px);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 0 0 transparent,0 2px 4px rgba(0,0,0,.4)}
  .k.on{background:var(--c);color:#0b0e1c;
    box-shadow:0 0 20px color-mix(in srgb,var(--c) 70%,transparent),0 3px 0 color-mix(in srgb,var(--c) 55%,#000)}
  .k span{font-size:11px;font-weight:700;opacity:.9;line-height:1}
  .k.txt span{font-size:15px;font-weight:800;opacity:1}
  .i{width:22px;height:22px;flex:none;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}

  /* tabs */
  .tabs{flex:none;display:grid;grid-template-columns:repeat(4,1fr);gap:6px;padding:5px;border-radius:20px;
    background:rgba(255,255,255,.06)}
  .tab{border:0;height:46px;border-radius:15px;background:transparent;color:var(--muted);font:inherit;font-weight:800;
    font-size:11px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px}
  .tab .i{width:20px;height:20px}
  .tab.active{color:#0b0e1c;background:linear-gradient(135deg,var(--violet),var(--blue));
    box-shadow:0 4px 14px rgba(125,92,255,.4)}

  /* keyboard open: compact layout */
  #app.kb .tab{height:38px;flex-direction:row;gap:6px;font-size:12px}
  #app.kb .tab .i{width:17px;height:17px}
  #app.kb .k{flex-direction:row;gap:6px;border-radius:12px}
  #app.kb .k .i{width:18px;height:18px}
  #app.kb .k span{font-size:11px}
  #app.kb .k.n{flex-direction:column;gap:2px}
  #app.kb .keys{gap:6px}
  #app.kb .hint{inset:30px 0 0 0}
</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <symbol id="i-kbd" viewBox="0 0 24 24"><rect x="2.5" y="6" width="19" height="12" rx="3"/><path d="M7 10h.01M11 10h.01M15 10h.01M8 14h8"/></symbol>
  <symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 3L5 14h6l-1 7 8-11h-6z"/></symbol>
  <symbol id="i-grid" viewBox="0 0 24 24"><rect x="4" y="4" width="6" height="6" rx="1.5"/><rect x="14" y="4" width="6" height="6" rx="1.5"/><rect x="4" y="14" width="6" height="6" rx="1.5"/><rect x="14" y="14" width="6" height="6" rx="1.5"/></symbol>
  <symbol id="i-media" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M10 8.5l5 3.5-5 3.5z"/></symbol>
  <symbol id="i-trash" viewBox="0 0 24 24"><path d="M5 7h14M10 7V5h4v2M7 7l1 13h8l1-13"/></symbol>
  <symbol id="i-copy" viewBox="0 0 24 24"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 012-2h9"/></symbol>
  <symbol id="i-paste" viewBox="0 0 24 24"><rect x="6" y="5" width="12" height="16" rx="2"/><path d="M9 5V4a1 1 0 011-1h4a1 1 0 011 1v1"/></symbol>
  <symbol id="i-cut" viewBox="0 0 24 24"><circle cx="6" cy="6.5" r="2.5"/><circle cx="6" cy="17.5" r="2.5"/><path d="M8 8l12 9M8 16L20 7"/></symbol>
  <symbol id="i-undo" viewBox="0 0 24 24"><path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 010 12h-3"/></symbol>
  <symbol id="i-redo" viewBox="0 0 24 24"><path d="M15 14l5-5-5-5"/><path d="M20 9H10a6 6 0 000 12h3"/></symbol>
  <symbol id="i-all" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="3" stroke-dasharray="3 3"/><path d="M9 12l2 2 4-4"/></symbol>
  <symbol id="i-save" viewBox="0 0 24 24"><path d="M5 4h11l3 3v13H5z"/><path d="M8 4v5h7V4M8 20v-6h8v6"/></symbol>
  <symbol id="i-find" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/></symbol>
  <symbol id="i-switch" viewBox="0 0 24 24"><rect x="3" y="4" width="12" height="10" rx="2"/><rect x="9" y="10" width="12" height="10" rx="2"/></symbol>
  <symbol id="i-desk" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></symbol>
  <symbol id="i-snip" viewBox="0 0 24 24"><path d="M6 2v14a2 2 0 002 2h14M2 6h14a2 2 0 012 2v14"/></symbol>
  <symbol id="i-task" viewBox="0 0 24 24"><path d="M3 12h4l3-8 4 16 3-8h4"/></symbol>
  <symbol id="i-up" viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></symbol>
  <symbol id="i-down" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></symbol>
  <symbol id="i-left" viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></symbol>
  <symbol id="i-right" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></symbol>
  <symbol id="i-bksp" viewBox="0 0 24 24"><path d="M9 5h11a1 1 0 011 1v12a1 1 0 01-1 1H9l-6-7z"/><path d="M13 9.5l5 5M18 9.5l-5 5"/></symbol>
  <symbol id="i-del" viewBox="0 0 24 24"><path d="M15 5H4a1 1 0 00-1 1v12a1 1 0 001 1h11l6-7z"/><path d="M8 9.5l5 5M13 9.5l-5 5"/></symbol>
  <symbol id="i-enter" viewBox="0 0 24 24"><path d="M20 5v6a3 3 0 01-3 3H5"/><path d="M9 10l-4 4 4 4"/></symbol>
  <symbol id="i-tab" viewBox="0 0 24 24"><path d="M3 12h13M12 8l4 4-4 4M21 6v12"/></symbol>
  <symbol id="i-home" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7"/><path d="M6 10v10h12V10"/></symbol>
  <symbol id="i-end" viewBox="0 0 24 24"><path d="M3 12h13M12 8l4 4-4 4M21 6v12"/></symbol>
  <symbol id="i-pgup" viewBox="0 0 24 24"><path d="M7 11l5-5 5 5M7 18l5-5 5 5"/></symbol>
  <symbol id="i-pgdn" viewBox="0 0 24 24"><path d="M7 6l5 5 5-5M7 13l5 5 5-5"/></symbol>
  <symbol id="i-caps" viewBox="0 0 24 24"><path d="M12 4l7 8h-4v4H9v-4H5z"/><path d="M9 20h6"/></symbol>
  <symbol id="i-shift" viewBox="0 0 24 24"><path d="M12 4l8 9h-5v7H9v-7H4z"/></symbol>
  <symbol id="i-win" viewBox="0 0 24 24"><g fill="currentColor" stroke="none"><rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1"/><rect x="13" y="3.5" width="7.5" height="7.5" rx="1"/><rect x="3.5" y="13" width="7.5" height="7.5" rx="1"/><rect x="13" y="13" width="7.5" height="7.5" rx="1"/></g></symbol>
  <symbol id="i-cam" viewBox="0 0 24 24"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></symbol>
  <symbol id="i-prev" viewBox="0 0 24 24"><path d="M19 5v14L9 12z" fill="currentColor"/><path d="M5.5 5v14"/></symbol>
  <symbol id="i-next" viewBox="0 0 24 24"><path d="M5 5v14l10-7z" fill="currentColor"/><path d="M18.5 5v14"/></symbol>
  <symbol id="i-play" viewBox="0 0 24 24"><path d="M5 5l9 7-9 7z" fill="currentColor"/><path d="M18 5v14"/></symbol>
  <symbol id="i-voldn" viewBox="0 0 24 24"><path d="M4 10h4l5-4v12l-5-4H4z"/><path d="M16.5 9.5a4 4 0 010 5"/></symbol>
  <symbol id="i-volup" viewBox="0 0 24 24"><path d="M4 10h4l5-4v12l-5-4H4z"/><path d="M16.5 9.5a4 4 0 010 5M19 7a8 8 0 010 10"/></symbol>
  <symbol id="i-mute" viewBox="0 0 24 24"><path d="M4 10h4l5-4v12l-5-4H4z"/><path d="M17 9.5l5 5M22 9.5l-5 5"/></symbol>
</defs></svg>

<div id="app">
  <header>
    <div class="brand"><div class="logo"><svg class="i" viewBox="0 0 24 24"><use href="#i-kbd"/></svg></div>Phone Keyboard</div>
    <div class="status" id="status"><span class="dot"></span><span id="stext">Connecting</span></div>
  </header>

  <div class="card" id="card">
    <div class="cardtop">
      <span>Typing on your PC</span>
      <div class="tools">
        <button class="tool" id="clearBtn" aria-label="Clear box"><svg class="i" viewBox="0 0 24 24"><use href="#i-trash"/></svg></button>
        <button class="tool" id="kbBtn" aria-label="Show or hide keyboard"><svg class="i" viewBox="0 0 24 24"><use href="#i-kbd"/></svg></button>
      </div>
    </div>
    <textarea id="ta" autocapitalize="off" autocomplete="off" autocorrect="off" spellcheck="false"></textarea>
    <div class="hint" id="hint">Tap here to open your keyboard</div>
  </div>

  <div class="panel" id="panel"></div>
  <nav class="tabs" id="tabs"></nav>
</div>

<script>
(function(){
  var TOKEN = new URLSearchParams(location.search).get('t') || '';
  var app = document.getElementById('app'), ta = document.getElementById('ta');
  var statusEl = document.getElementById('status'), stext = document.getElementById('stext');
  var hint = document.getElementById('hint');
  var PAD = '\u200b', prev = '', composing = false;
  var mods = {ctrl:false, alt:false, shift:false, win:false}, modBtns = {};
  var C = {red:'var(--red)',amber:'var(--amber)',green:'var(--green)',teal:'var(--teal)',blue:'var(--blue)',
           violet:'var(--violet)',pink:'var(--pink)',slate:'var(--slate)'};

  /* ---------- fit exactly into the visible screen (above the phone keyboard) ---------- */
  var baseH = 0, baseW = 0;
  function fit(){
    var vv = window.visualViewport;
    var h = vv ? vv.height : window.innerHeight, top = vv ? vv.offsetTop : 0;
    if (window.innerWidth !== baseW){ baseW = window.innerWidth; baseH = 0; }
    if (h > baseH) baseH = h;
    app.style.height = h + 'px';
    app.style.transform = 'translateY(' + top + 'px)';
    app.classList.toggle('kb', h < baseH * 0.8);
    if (window.scrollY) window.scrollTo(0, 0);
  }
  if (window.visualViewport){
    visualViewport.addEventListener('resize', fit);
    visualViewport.addEventListener('scroll', fit);
  }
  window.addEventListener('resize', fit);
  window.addEventListener('orientationchange', function(){ setTimeout(fit, 250); });
  fit();

  /* ---------- keys ---------- */
  // s = column span (of 12), c = colour, i = icon, l = label, t = text-only key
  var TABS = [
    {name:'Keys', icon:'kbd', keys:[
      {mod:'ctrl', l:'Ctrl', c:'violet', s:3, t:1}, {mod:'alt', l:'Alt', c:'violet', s:3, t:1},
      {mod:'shift', l:'Shift', i:'shift', c:'violet', s:3}, {mod:'win', l:'Win', i:'win', c:'violet', s:3},
      {k:'esc', l:'Esc', c:'red', s:2, t:1}, {k:'tab', l:'Tab', i:'tab', c:'amber', s:2},
      {k:'capslock', l:'Caps', i:'caps', c:'slate', s:2}, {k:'insert', l:'Ins', c:'slate', s:2, t:1},
      {k:'delete', l:'Del', i:'del', c:'red', s:2, r:1}, {k:'printscreen', l:'PrtSc', i:'cam', c:'pink', s:2},
      {k:'home', l:'Home', i:'home', c:'teal', s:2}, {k:'up', l:'Up', i:'up', c:'blue', s:2, r:1},
      {k:'end', l:'End', i:'end', c:'teal', s:2}, {k:'pageup', l:'PgUp', i:'pgup', c:'teal', s:3, r:1},
      {k:'pagedown', l:'PgDn', i:'pgdn', c:'teal', s:3, r:1},
      {k:'left', l:'Left', i:'left', c:'blue', s:2, r:1}, {k:'down', l:'Down', i:'down', c:'blue', s:2, r:1},
      {k:'right', l:'Right', i:'right', c:'blue', s:2, r:1},
      {k:'backspace', l:'Back', i:'bksp', c:'red', s:3, r:1}, {k:'enter', l:'Enter', i:'enter', c:'green', s:3, r:1}
    ]},
    {name:'Shortcuts', icon:'bolt', keys:[
      {x:'c', m:['ctrl'], l:'Copy', i:'copy', c:'blue', s:4}, {x:'v', m:['ctrl'], l:'Paste', i:'paste', c:'green', s:4},
      {x:'x', m:['ctrl'], l:'Cut', i:'cut', c:'red', s:4},
      {x:'z', m:['ctrl'], l:'Undo', i:'undo', c:'amber', s:4}, {x:'y', m:['ctrl'], l:'Redo', i:'redo', c:'amber', s:4},
      {x:'a', m:['ctrl'], l:'Select all', i:'all', c:'violet', s:4},
      {x:'s', m:['ctrl'], l:'Save', i:'save', c:'green', s:4}, {x:'f', m:['ctrl'], l:'Find', i:'find', c:'blue', s:4},
      {x:'tab', m:['alt'], l:'Switch app', i:'switch', c:'pink', s:4},
      {x:'d', m:['win'], l:'Desktop', i:'desk', c:'teal', s:4},
      {x:'s', m:['win','shift'], l:'Snip', i:'snip', c:'pink', s:4},
      {x:'esc', m:['ctrl','shift'], l:'Task Mgr', i:'task', c:'red', s:4}
    ]},
    {name:'F-keys', icon:'grid', keys:(function(){
      var a = [], cols = ['pink','pink','pink','pink','amber','amber','amber','amber','teal','teal','teal','teal'];
      for (var n = 1; n <= 12; n++) a.push({k:'f'+n, l:'F'+n, c:cols[n-1], s:3, t:1});
      return a; })()},
    {name:'Media', icon:'media', keys:[
      {k:'prevtrack', l:'Previous', i:'prev', c:'violet', s:4}, {k:'playpause', l:'Play / Pause', i:'play', c:'green', s:4},
      {k:'nexttrack', l:'Next', i:'next', c:'violet', s:4},
      {k:'voldown', l:'Vol -', i:'voldn', c:'blue', s:4, r:1}, {k:'mute', l:'Mute', i:'mute', c:'red', s:4},
      {k:'volup', l:'Vol +', i:'volup', c:'blue', s:4, r:1}
    ]}
  ];
  function icon(n){ return '<svg class="i" viewBox="0 0 24 24"><use href="#i-' + n + '"/></svg>'; }

  var panel = document.getElementById('panel'), tabsEl = document.getElementById('tabs');
  var pages = [], tabBtns = [];
  TABS.forEach(function(tab, ti){
    var page = document.createElement('div');
    page.className = 'keys' + (ti === 0 ? ' show' : '');
    tab.keys.forEach(function(d){
      var b = document.createElement('button');
      b.className = 'k' + (d.t ? ' txt' : '') + (d.s <= 2 ? ' n' : '');
      b.style.setProperty('--c', C[d.c]);
      b.style.gridColumn = 'span ' + d.s;
      b.innerHTML = (d.i ? icon(d.i) : '') + '<span>' + d.l + '</span>';
      b.setAttribute('aria-label', d.l);
      if (d.mod) modBtns[d.mod] = b;
      bind(b, d);
      page.appendChild(b);
    });
    panel.appendChild(page); pages.push(page);

    var tb = document.createElement('button');
    tb.className = 'tab' + (ti === 0 ? ' active' : '');
    tb.innerHTML = icon(tab.icon) + '<span>' + tab.name + '</span>';
    tb.addEventListener('pointerdown', function(e){
      e.preventDefault(); buzz();
      pages.forEach(function(p, i){ p.classList.toggle('show', i === ti); });
      tabBtns.forEach(function(t, i){ t.classList.toggle('active', i === ti); });
    });
    guard(tb);
    tabsEl.appendChild(tb); tabBtns.push(tb);
  });

  function buzz(){ if (navigator.vibrate) navigator.vibrate(6); }
  function guard(el){          // pressing a button must never steal focus (keeps the phone keyboard open)
    el.addEventListener('mousedown', function(e){ e.preventDefault(); });
    el.addEventListener('touchstart', function(e){ e.preventDefault(); }, {passive:false});
    el.addEventListener('contextmenu', function(e){ e.preventDefault(); });
  }

  /* ---------- send queue (keeps order, merges fast typing) ---------- */
  var queue = [], busy = false;
  function setOnline(v){ statusEl.classList.toggle('on', v); stext.textContent = v ? 'Connected' : 'Reconnecting'; }
  function post(path, body){ queue.push([path, body]); pump(); }
  function merge(a, b){
    var t = a.text, back = a.back;
    if (b.back <= t.length) t = t.slice(0, t.length - b.back) + b.text;
    else { back += b.back - t.length; t = b.text; }
    return {back: back, text: t};
  }
  function pump(){
    if (busy || !queue.length) return;
    busy = true;
    var job = queue.shift();
    while (queue.length && job[0] === '/api/input' && queue[0][0] === '/api/input'){
      job = ['/api/input', merge(job[1], queue.shift()[1])];
    }
    fetch(job[0], {method:'POST', headers:{'Content-Type':'application/json','X-Token':TOKEN}, body: JSON.stringify(job[1])})
      .then(function(r){ setOnline(r.ok); })
      .catch(function(){ setOnline(false); })
      .finally(function(){ busy = false; pump(); });
  }
  function ping(){
    fetch('/api/ping', {method:'POST', headers:{'X-Token':TOKEN}, body:'{}'})
      .then(function(r){ setOnline(r.ok); }).catch(function(){ setOnline(false); });
  }
  setInterval(ping, 3000); ping();

  /* ---------- text box -> diff -> PC ---------- */
  function typed(){ return ta.value.replace(/\u200b/g, ''); }
  function updateHint(){ hint.classList.toggle('hide', document.activeElement === ta || typed() !== ''); }
  function resetBox(tail){
    ta.value = PAD.repeat(12) + (tail || '');
    prev = ta.value;
    var n = ta.value.length; ta.setSelectionRange(n, n); ta.scrollTop = ta.scrollHeight;
    updateHint();
  }
  function activeMods(){ return Object.keys(mods).filter(function(m){ return mods[m]; }); }
  function clearMods(){
    Object.keys(mods).forEach(function(m){ mods[m] = false; if (modBtns[m]) modBtns[m].classList.remove('on'); });
  }
  function handleInput(){
    var cur = ta.value, i = 0, max = Math.min(prev.length, cur.length);
    while (i < max && prev.charCodeAt(i) === cur.charCodeAt(i)) i++;
    var back = prev.length - i, added = cur.slice(i), am = activeMods();
    if (am.length && back === 0 && added.length === 1){
      post('/api/key', {key: added.toLowerCase(), mods: am});
      clearMods(); ta.value = prev;
      var n = ta.value.length; ta.setSelectionRange(n, n);
      return;
    }
    if (back || added) post('/api/input', {back: back, text: added});
    prev = cur;
    if (!composing){
      if (cur.length > 300) resetBox(cur.slice(-40));
      else if (cur.length < 6) resetBox(typed());
    }
    ta.scrollTop = ta.scrollHeight;
    updateHint();
  }
  ta.addEventListener('compositionstart', function(){ composing = true; });
  ta.addEventListener('compositionend', function(){ composing = false; handleInput(); });
  ta.addEventListener('input', handleInput);
  ta.addEventListener('focus', function(){ setTimeout(function(){ var n = ta.value.length; ta.setSelectionRange(n, n); fit(); }, 0); updateHint(); });
  ta.addEventListener('blur', function(){ updateHint(); setTimeout(fit, 150); });
  document.getElementById('card').addEventListener('pointerdown', function(e){
    if (!e.target.closest('.tool')) setTimeout(function(){ ta.focus(); }, 0);
  });
  var kbBtn = document.getElementById('kbBtn'), clearBtn = document.getElementById('clearBtn');
  [kbBtn, clearBtn].forEach(guard);
  kbBtn.addEventListener('pointerdown', function(e){
    e.preventDefault(); e.stopPropagation(); buzz();
    if (document.activeElement === ta) ta.blur(); else ta.focus();
  });
  clearBtn.addEventListener('pointerdown', function(e){ e.preventDefault(); e.stopPropagation(); buzz(); resetBox(''); });
  resetBox('');

  /* ---------- key presses ---------- */
  function bind(btn, d){
    var timer = null, rep = null;
    function stop(){ clearTimeout(timer); clearInterval(rep); }
    function fire(){
      buzz();
      if (d.mod){ mods[d.mod] = !mods[d.mod]; btn.classList.toggle('on', mods[d.mod]); return; }
      if (d.x){ post('/api/key', {key: d.x, mods: d.m}); return; }
      var am = activeMods();
      post('/api/key', {key: d.k, mods: am});
      if (am.length) clearMods();
    }
    btn.addEventListener('pointerdown', function(e){
      e.preventDefault(); fire();
      if (d.r && !activeMods().length) timer = setTimeout(function(){ rep = setInterval(fire, 60); }, 380);
    });
    ['pointerup','pointercancel','pointerleave'].forEach(function(ev){ btn.addEventListener(ev, stop); });
    guard(btn);
  }
})();
</script>
</body>
</html>
"""

DENIED = """<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<body style="font-family:system-ui;display:grid;place-items:center;height:100vh;margin:0;text-align:center;padding:24px">
<div><h2>Scan the QR code again</h2><p style="opacity:.65">This link is missing its access key. Open Phone Keyboard on your PC and scan the code shown there.</p></div>
"""
