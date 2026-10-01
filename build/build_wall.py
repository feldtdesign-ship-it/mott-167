"""build_wall.py — live-wall.html from data/cameras.json: the six nearest DOT cameras, refreshed every 20 s."""
import json, os, html
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(S)
cams = json.load(open(os.path.join(R, 'data', 'cameras.json')))[:6]
figs = ''.join(f'<figure data-id="{c["id"]}"><img alt="{html.escape(c["name"])}"><figcaption><b>{html.escape(c["name"])}</b> · {c["dist"]} m · <a href="https://webcams.nyctmc.org/" target="_blank" rel="noopener">DOT</a></figcaption></figure>' for c in cams)
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>167 Mott · live cameras</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta property="og:title" content="167 Mott Street · Live Camera Wall"><meta property="og:description" content="The six nearest NYC DOT cameras. The closest is {cams[0]['dist']} m from the door. None of them sees Mott Street."><meta property="og:image" content="https://feldtdesign-ship-it.github.io/mott-167/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&display=swap">
<style>
body{{margin:0;background:#141210;color:#F3EDE3;font-family:"DM Mono",ui-monospace,Menlo,monospace;font-size:12px}}
header{{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid #33302B;letter-spacing:.1em;text-transform:uppercase;gap:12px;flex-wrap:wrap}}
header b{{color:#2DBE6C;font-weight:400}}
main{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(352px,100%),1fr));gap:10px;padding:10px}}
figure{{margin:0;background:#1E1B18;border:1px solid #33302B}} img{{width:100%;aspect-ratio:352/240;object-fit:cover;display:block;background:#000}}
figcaption{{padding:8px 10px;color:#C9C2B6}} figcaption b{{color:#F3EDE3;font-weight:500}} a{{color:#2DBE6C}}
button{{font:inherit;background:transparent;color:#C9C2B6;border:1px solid #33302B;padding:5px 10px;cursor:pointer;letter-spacing:.08em;text-transform:uppercase}}
p{{padding:0 16px 16px;color:#8A857C;max-width:80ch}}
</style></head><body>
<header><span><a href="./" style="color:#C9C2B6;text-decoration:none">← 167 Mott</a> &nbsp;·&nbsp; nearest live DOT cameras</span><span><b id="t">–</b> &nbsp; <button id="p">Pause</button></span></header>
<main>{figs}</main>
<p>The nearest camera is {cams[0]['dist']} m from the door. None of them sees Mott Street or the door itself; they watch Broome, Kenmare, Grand, Delancey and Canal. The city keeps no recordings; this wall refreshes the public feeds every 20 seconds.</p>
<script>
const figs=[...document.querySelectorAll('figure')]; let on=true;
function refresh(){{ const ts=Date.now(); figs.forEach(f=>{{ f.querySelector('img').src='https://webcams.nyctmc.org/api/cameras/'+f.dataset.id+'/image?t='+ts; }}); document.getElementById('t').textContent='refreshed '+new Date().toLocaleTimeString('en-US',{{timeZone:'America/New_York'}})+' NYC'; }}
refresh(); setInterval(()=>{{ if(on) refresh(); }}, 20000);
document.getElementById('p').onclick=e=>{{ on=!on; e.target.textContent=on?'Pause':'Resume'; }};
</script></body></html>'''
open(os.path.join(R, 'live-wall.html'), 'w').write(page); print('built live-wall.html', len(cams), 'cameras')
