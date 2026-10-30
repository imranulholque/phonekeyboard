# The page the phone opens after scanning the QR code.
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#e9edf4">
<meta name="color-scheme" content="light dark">
<title>Phone Keyboard</title>
<style>
  :root{
    --bg:#e9edf4; --bg2:#f6f8fc; --card:#ffffff; --ink:#18202f; --muted:#6b7488;
    --key:#ffffff; --key-edge:#c5ccda; --key-shadow:rgba(30,45,90,.10);
    --field:#f1f4f9; --accent:#3556ff; --accent-edge:#2038c4; --accent-ink:#ffffff;
    --ok:#12b886; --bad:#f06a6a; --chip:#dde3ef; --on:#18202f; --on-ink:#ffffff;
  }
  @media (prefers-color-scheme: dark){
    :root{
      --bg:#0d1017; --bg2:#151a24; --card:#171c27; --ink:#eef1f8; --muted:#8c96ad;
      --key:#262d3d; --key-edge:#0a0d13; --key-shadow:rgba(0,0,0,.35);
      --field:#0f131b; --accent:#6c85ff; --accent-edge:#3a4fd0; --accent-ink:#0b1030;
      --chip:#20273a; --on:#eef1f8; --on-ink:#0d1017;
    }
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html{height:100%}
  html,body{margin:0;background:var(--bg);color:var(--ink);overscroll-behavior:none;
    font-family:ui-rounded,"SF Pro Rounded","Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
  body{height:100%;overflow-y:auto;display:flex;flex-direction:column;gap:14px;
    padding:max(14px,env(safe-area-inset-top)) 14px max(14px,env(safe-area-inset-bottom));
    background:linear-gradient(var(--bg2),var(--bg) 55%)}

  header{display:flex;align-items:center;justify-content:space-between;padding:2px 4px}
  .brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:18px;letter-spacing:.1px}
  .logo{width:30px;height:30px;border-radius:9px;background:var(--accent);display:grid;place-items:center}
  .logo svg{width:18px;height:18px;fill:none;stroke:var(--accent-ink);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .status{display:flex;align-items:center;gap:7px;font-size:13px;font-weight:600;color:var(--muted);
    background:var(--card);padding:7px 12px;border-radius:999px;box-shadow:0 1px 0 var(--key-edge)}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--bad)}
  .on .dot{background:var(--ok);box-shadow:0 0 0 4px color-mix(in srgb,var(--ok) 22%,transparent)}
  .on{color:var(--ink)}

  header,.chips,.pad{flex:none}
  .field{flex:1;min-height:110px;display:flex;flex-direction:column;background:var(--card);border-radius:22px;padding:14px 16px 12px;
    box-shadow:0 1px 0 var(--key-edge),0 10px 24px var(--key-shadow)}
  .field label{display:block;font-size:13px;font-weight:600;color:var(--muted);margin-bottom:6px}
  textarea{width:100%;flex:1;min-height:0;resize:none;border:0;outline:0;background:transparent;color:var(--ink);
    font:inherit;font-size:22px;line-height:1.35;padding:0;caret-color:var(--accent)}

  .chips{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;margin:0 -14px;padding:2px 14px}
  .chips::-webkit-scrollbar{display:none}
  .chip{flex:none;min-height:40px;padding:0 16px;border-radius:999px;font-size:14px;background:var(--chip);color:var(--ink);
    box-shadow:none;border:0}
  .chip:active{transform:scale(.96)}

  .pad{margin-top:auto;display:flex;flex-direction:column;gap:10px}
  .grid2{display:grid;grid-template-columns:1.15fr 1fr;gap:12px;align-items:stretch}
  .dpad{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:8px}
  .dpad .up{grid-column:2;grid-row:1} .dpad .left{grid-column:1;grid-row:2}
  .dpad .down{grid-column:2;grid-row:2} .dpad .right{grid-column:3;grid-row:2}
  .misc{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
  .mods{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
  .bottom{display:grid;grid-template-columns:1fr 1.7fr 1.3fr;gap:8px}

  button{font:inherit;font-weight:600;font-size:15px;color:var(--ink);border:0;border-radius:16px;min-height:52px;
    background:var(--key);box-shadow:0 3px 0 var(--key-edge),0 8px 14px var(--key-shadow);
    display:grid;place-items:center;touch-action:manipulation;user-select:none;-webkit-user-select:none;
    transition:transform .05s,box-shadow .05s}
  button:active{transform:translateY(3px);box-shadow:0 0 0 var(--key-edge),0 2px 4px var(--key-shadow)}
  button svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
  .small{min-height:44px;font-size:14px;border-radius:14px}
  .mod{background:var(--chip);box-shadow:none;color:var(--muted);min-height:42px;border-radius:14px;font-size:14px}
  .mod:active{transform:scale(.97);box-shadow:none}
  .mod.active{background:var(--on);color:var(--on-ink)}
  .primary{background:var(--accent);color:var(--accent-ink);box-shadow:0 3px 0 var(--accent-edge),0 8px 14px var(--key-shadow)}
  .primary:active{box-shadow:0 0 0 var(--accent-edge),0 2px 4px var(--key-shadow)}
  .space{color:var(--muted)}
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo"><svg viewBox="0 0 24 24"><rect x="2.5" y="6" width="19" height="12" rx="3"/><path d="M7 10h.01M11 10h.01M15 10h.01M8 14h8"/></svg></div>
    Phone Keyboard
  </div>
  <div class="status" id="status"><span class="dot"></span><span id="stext">Connecting</span></div>
</header>

<div class="field">
  <label for="ta">Typing on your PC</label>
  <textarea id="ta" autocapitalize="off" autocomplete="off" autocorrect="off" spellcheck="false"></textarea>
</div>

<div class="chips">
  <button class="chip" data-combo="c">Copy</button>
  <button class="chip" data-combo="v">Paste</button>
  <button class="chip" data-combo="x">Cut</button>
  <button class="chip" data-combo="z">Undo</button>
  <button class="chip" data-combo="y">Redo</button>
  <button class="chip" data-combo="a">Select all</button>
  <button class="chip" data-combo="s">Save</button>
  <button class="chip" data-combo="f">Find</button>
</div>

<div class="pad">
  <div class="mods">
    <button class="mod" data-mod="ctrl">Ctrl</button>
    <button class="mod" data-mod="alt">Alt</button>
    <button class="mod" data-mod="shift">Shift</button>
    <button class="mod" data-mod="win">Win</button>
  </div>

  <div class="grid2">
    <div class="dpad">
      <button class="up" data-key="up" data-repeat aria-label="Up"><svg viewBox="0 0 24 24"><path d="M6 15l6-6 6 6"/></svg></button>
      <button class="left" data-key="left" data-repeat aria-label="Left"><svg viewBox="0 0 24 24"><path d="M15 6l-6 6 6 6"/></svg></button>
      <button class="down" data-key="down" data-repeat aria-label="Down"><svg viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg></button>
      <button class="right" data-key="right" data-repeat aria-label="Right"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg></button>
    </div>
    <div class="misc">
      <button class="small" data-key="esc">Esc</button>
      <button class="small" data-key="tab">Tab</button>
      <button class="small" data-key="delete" data-repeat>Del</button>
      <button class="small" data-key="home">Home</button>
      <button class="small" data-key="end">End</button>
      <button class="small" data-key="pageup">PgUp</button>
    </div>
  </div>

  <div class="bottom">
    <button data-key="backspace" data-repeat aria-label="Backspace"><svg viewBox="0 0 24 24"><path d="M9 5h11a1 1 0 011 1v12a1 1 0 01-1 1H9l-6-7z"/><path d="M13 9.5l5 5M18 9.5l-5 5"/></svg></button>
    <button class="space" data-key="space" data-repeat>Space</button>
    <button class="primary" data-key="enter" data-repeat aria-label="Enter"><svg viewBox="0 0 24 24"><path d="M20 5v6a3 3 0 01-3 3H5"/><path d="M9 10l-4 4 4 4"/></svg></button>
  </div>
</div>

<script>
(function(){
  var TOKEN = new URLSearchParams(location.search).get('t') || '';
  var ta = document.getElementById('ta');
  var statusEl = document.getElementById('status');
  var stext = document.getElementById('stext');
  var PAD = '\u200b';          // invisible padding so Backspace works on an empty box
  var prev = '', composing = false;
  var mods = {ctrl:false, alt:false, shift:false, win:false};

  function buzz(){ if (navigator.vibrate) navigator.vibrate(6); }

  /* ---- ordered send queue (keeps keystrokes in order) ---- */
  var queue = [], busy = false;
  function setOnline(v){
    statusEl.classList.toggle('on', v);
    stext.textContent = v ? 'Connected' : 'Reconnecting';
  }
  function post(path, body){ queue.push([path, body]); pump(); }
  function merge(a, b){            // join two input jobs into one request
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
    fetch(job[0], {method:'POST', headers:{'Content-Type':'application/json','X-Token':TOKEN},
                   body: JSON.stringify(job[1])})
      .then(function(r){ setOnline(r.ok); })
      .catch(function(){ setOnline(false); })
      .finally(function(){ busy = false; pump(); });
  }
  function ping(){
    fetch('/api/ping', {method:'POST', headers:{'X-Token':TOKEN}, body:'{}'})
      .then(function(r){ setOnline(r.ok); }).catch(function(){ setOnline(false); });
  }
  setInterval(ping, 3000); ping();

  /* ---- text box -> diff -> PC ---- */
  function resetBox(tail){
    ta.value = PAD.repeat(12) + (tail || '');
    prev = ta.value;
    var n = ta.value.length; ta.setSelectionRange(n, n);
  }
  function activeMods(){ return Object.keys(mods).filter(function(m){ return mods[m]; }); }
  function clearMods(){
    Object.keys(mods).forEach(function(m){ mods[m] = false; });
    document.querySelectorAll('[data-mod]').forEach(function(b){ b.classList.remove('active'); });
  }
  function handleInput(){
    var cur = ta.value, i = 0;
    var max = Math.min(prev.length, cur.length);
    while (i < max && prev.charCodeAt(i) === cur.charCodeAt(i)) i++;
    var back = prev.length - i;
    var added = cur.slice(i);
    var am = activeMods();
    if (am.length && back === 0 && added.length === 1){
      post('/api/key', {key: added.toLowerCase(), mods: am});
      clearMods();
      ta.value = prev;
      var n = ta.value.length; ta.setSelectionRange(n, n);
      return;
    }
    if (back || added) post('/api/input', {back: back, text: added});
    prev = cur;
    if (!composing){
      if (cur.length > 300) resetBox(cur.slice(-40));
      else if (cur.length < 6) resetBox(cur.replace(/\u200b/g, ''));
    }
  }
  ta.addEventListener('compositionstart', function(){ composing = true; });
  ta.addEventListener('compositionend', function(){ composing = false; handleInput(); });
  ta.addEventListener('input', handleInput);
  ta.addEventListener('focus', function(){ setTimeout(function(){ var n=ta.value.length; ta.setSelectionRange(n,n); }, 0); });
  resetBox('');

  /* ---- buttons ---- */
  function bind(btn){
    var timer = null, rep = null;
    function stop(){ clearTimeout(timer); clearInterval(rep); }
    function fire(){
      buzz();
      if (btn.dataset.mod){
        mods[btn.dataset.mod] = !mods[btn.dataset.mod];
        btn.classList.toggle('active', mods[btn.dataset.mod]);
        return;
      }
      if (btn.dataset.combo){ post('/api/key', {key: btn.dataset.combo, mods:['ctrl']}); return; }
      var am = activeMods();
      post('/api/key', {key: btn.dataset.key, mods: am});
      if (am.length) clearMods();
    }
    btn.addEventListener('pointerdown', function(e){
      e.preventDefault(); fire();
      if (btn.hasAttribute('data-repeat') && !activeMods().length){
        timer = setTimeout(function(){ rep = setInterval(fire, 60); }, 380);
      }
    });
    ['pointerup','pointercancel','pointerleave'].forEach(function(ev){ btn.addEventListener(ev, stop); });
    btn.addEventListener('mousedown', function(e){ e.preventDefault(); });   // keep keyboard open
    btn.addEventListener('touchstart', function(e){ e.preventDefault(); }, {passive:false});
    btn.addEventListener('contextmenu', function(e){ e.preventDefault(); });
  }
  document.querySelectorAll('button').forEach(bind);
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
