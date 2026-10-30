# The page the phone opens after scanning the QR code.
PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="theme-color" content="#11152b">
<title>Phone Keyboard</title>
<style>
  :root{
    --bg:#11152b; --panel:#181e3b; --key:#262e57; --key-edge:#141937; --key-hi:#313b6e;
    --text:#eef0ff; --muted:#9aa3d6; --accent:#8b9bff; --ok:#5eead4; --bad:#ff7a8a;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;height:100%;background:var(--bg);color:var(--text);
    font-family:"Segoe UI",system-ui,-apple-system,Roboto,sans-serif;overscroll-behavior:none}
  body{display:flex;flex-direction:column;gap:12px;padding:max(14px,env(safe-area-inset-top)) 14px max(14px,env(safe-area-inset-bottom));
    background:radial-gradient(120% 60% at 50% 0%,#1d2450 0%,var(--bg) 60%)}
  header{display:flex;align-items:center;justify-content:space-between}
  h1{font-size:19px;margin:0;font-weight:700;letter-spacing:.2px}
  .status{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);
    background:var(--panel);padding:6px 12px;border-radius:999px}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--bad);transition:background .2s}
  .on .dot{background:var(--ok);box-shadow:0 0 8px var(--ok)}
  .card{background:var(--panel);border-radius:18px;padding:12px;border:1px solid #232b55}
  .card label{display:block;font-size:13px;color:var(--muted);margin:0 2px 8px}
  textarea{width:100%;height:112px;resize:none;border:0;outline:0;border-radius:12px;
    background:#0e1226;color:var(--text);font:inherit;font-size:18px;line-height:1.4;padding:12px;
    caret-color:var(--accent)}
  textarea:focus{box-shadow:0 0 0 2px var(--accent)}
  .row{display:grid;gap:8px}
  .mods{grid-template-columns:repeat(4,1fr)}
  .keys{grid-template-columns:repeat(4,1fr)}
  .keys .w2{grid-column:span 2}
  button{font:inherit;color:var(--text);border:0;border-radius:12px;min-height:46px;font-size:15px;font-weight:600;
    background:linear-gradient(var(--key-hi),var(--key));border-bottom:3px solid var(--key-edge);
    touch-action:manipulation;user-select:none;-webkit-user-select:none;transition:transform .05s}
  button:active{transform:translateY(2px);border-bottom-width:1px;margin-top:2px}
  button.mod{background:var(--panel);border:1px solid #2b3466;border-bottom-width:3px;color:var(--muted)}
  button.mod.active{background:var(--accent);color:#0e1226;border-color:var(--accent)}
  button.go{background:var(--accent);color:#0e1226;border-bottom-color:#5566d6}
  .hint{font-size:12px;color:var(--muted);text-align:center;margin-top:auto;padding-top:4px}
  .scroll{overflow-y:auto;display:flex;flex-direction:column;gap:12px;flex:1;min-height:0}
</style>
</head>
<body>
<header>
  <h1>Phone Keyboard</h1>
  <div class="status" id="status"><span class="dot"></span><span id="stext">Connecting…</span></div>
</header>

<div class="scroll">
  <div class="card">
    <label for="ta">Type here and it appears on your PC</label>
    <textarea id="ta" autocapitalize="off" autocomplete="off" autocorrect="off" spellcheck="false"></textarea>
  </div>

  <div class="row mods" id="mods">
    <button class="mod" data-mod="ctrl">Ctrl</button>
    <button class="mod" data-mod="alt">Alt</button>
    <button class="mod" data-mod="shift">Shift</button>
    <button class="mod" data-mod="win">Win</button>
  </div>

  <div class="row keys">
    <button data-key="esc">Esc</button>
    <button data-key="tab">Tab</button>
    <button data-key="backspace" data-repeat>⌫</button>
    <button data-key="delete" data-repeat>Del</button>

    <button data-key="home">Home</button>
    <button data-key="up" data-repeat>↑</button>
    <button data-key="end">End</button>
    <button data-key="pageup">PgUp</button>

    <button data-key="left" data-repeat>←</button>
    <button data-key="down" data-repeat>↓</button>
    <button data-key="right" data-repeat>→</button>
    <button data-key="pagedown">PgDn</button>

    <button data-combo="c">Copy</button>
    <button data-combo="v">Paste</button>
    <button data-combo="x">Cut</button>
    <button data-combo="z">Undo</button>

    <button data-combo="a">Select all</button>
    <button data-key="enter" class="go w2" data-repeat>Enter ↵</button>
    <button data-key="space" data-repeat>Space</button>
  </div>
  <div class="hint">Tap a modifier, then type a letter to send shortcuts like Ctrl+S.</div>
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

  /* ---- ordered send queue (keeps keystrokes in order) ---- */
  var queue = [], busy = false, online = false;
  function setOnline(v){
    online = v;
    statusEl.classList.toggle('on', v);
    stext.textContent = v ? 'Connected' : 'Reconnecting…';
  }
  function post(path, body){ queue.push([path, body]); pump(); }
  function pump(){
    if (busy || !queue.length) return;
    busy = true;
    var job = queue.shift();
    fetch(job[0], {method:'POST', headers:{'Content-Type':'application/json','X-Token':TOKEN},
                   body: JSON.stringify(job[1]), keepalive:true})
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
      ta.value = prev;                      // keep the box unchanged
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
<body style="font-family:system-ui;background:#11152b;color:#eef0ff;display:grid;place-items:center;height:100vh;margin:0;text-align:center;padding:24px">
<div><h2>Scan the QR code again</h2><p style="color:#9aa3d6">This link is missing its access key. Open Phone Keyboard on your PC and scan the code shown there.</p></div>
"""
