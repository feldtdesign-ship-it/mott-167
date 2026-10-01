"""make_template.py — one-off: builds build/mott_template.html from the Clinton template's CSS and chart code plus Mott's own words.
After this has run, edit mott_template.html directly; this file is kept as the record of what changed from Clinton."""
import os, re
S = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(S, '..', '..', 'clinton-84', 'build', 'clinton_template.html')).read()
css = src[src.index('<style>'):src.index('</style>') + 8]
js = src[src.index('<script>\nconst D = __DATA__'):]
def sub(s, pairs):
    for a, b in pairs:
        assert a in s, a[:70]; s = s.replace(a, b)
    return s
css = sub(css, [
 ('--f:#FF6319;--jz:#B07A3E;--l:#6B6660;--amber:#D9A441;', '--f:#2DBE6C;--six:#00933C;--jz:#B07A3E;--bd:#FF6319;--c:#FCCC0A;--l:#6B6660;--amber:#FCCC0A;'),
 ('--disp:"Newsreader","Georgia",serif;--body:"Instrument Sans",system-ui,-apple-system,sans-serif;--mono:"Space Mono",ui-monospace,Menlo,monospace',
  '--disp:"Bricolage Grotesque","Arial Narrow",sans-serif;--body:"Figtree",system-ui,-apple-system,sans-serif;--mono:"DM Mono",ui-monospace,Menlo,monospace'),
 ('h1 em{font-style:italic;font-weight:400;color:var(--f)}', 'h1 em{font-style:normal;font-weight:300;color:var(--f)}'),
 ('h2 em{font-style:italic;font-weight:400}', 'h2 em{font-style:normal;font-weight:300;color:var(--ink-2)}'),
 ('.hero .unit{font-family:var(--disp);font-style:italic;font-weight:400;', '.hero .unit{font-family:var(--disp);font-style:normal;font-weight:300;'),
 ('.f{color:var(--f)} .jz{color:var(--jz)}', '.f{color:var(--f)} .jz{color:var(--jz)} .bd{color:var(--bd)} .c{color:var(--c)}'),
 ('.card.jz{border-top-color:var(--jz)}', '.card.jz{border-top-color:var(--jz)} .card.bd{border-top-color:var(--bd)}'),
 ('.multi .y{fill:none;stroke-width:2} .multi .y.l{stroke:var(--f)} .multi .y.eb{stroke:var(--amber)}', '.multi .y{fill:none;stroke-width:2} .multi .y.f{stroke:var(--f)} .multi .y.jz{stroke:var(--jz)} .multi .y.bd{stroke:var(--bd)} .multi .y.c{stroke:var(--c)}'),
 ('.multi .ylab{font-family:var(--disp);font-weight:700;font-size:15px} .multi .ylab.l{fill:var(--f)} .multi .ylab.eb{fill:var(--amber)}', '.multi .ylab{font-family:var(--disp);font-weight:700;font-size:15px} .multi .ylab.f{fill:var(--f)} .multi .ylab.jz{fill:var(--jz)} .multi .ylab.bd{fill:var(--bd)} .multi .ylab.c{fill:var(--c)}'),
 ('.reg td.v{color:var(--f);font-weight:700}', '.reg td.v{color:var(--f);font-weight:500} .reg td.q{color:var(--muted)}'),
 ('.legend i.l{background:var(--f)} .legend i.a{background:var(--jz)} .legend i.c{background:var(--l)}', '.legend i.l{background:var(--f)} .legend i.a{background:var(--jz)} .legend i.c{background:var(--l)} .legend i.bd{background:var(--bd)} .legend i.y{background:var(--c)}'),
])
js = sub(js, [
 ("people an hour", "people an hour") if False else ("$('sub').innerHTML=`Entries doubled to include exits, summer 2026 average. The stairs are <b>260 m</b> west along Delancey. Peak for a ${dayName} is <b>${fmt(Math.max(...L[state.day])*2)}</b> an hour.`;",
  "$('sub').innerHTML=`Entries at Bowery, Spring Street and Grand Street added together and doubled to include exits, summer 2026 average. The nearest stairs are <b>215 m</b> away. Peak for a ${dayName} is <b>${fmt(Math.max(...L[state.day])*2)}</b> an hour.`;"),
 ("vehicles\"></i>`", "vehicles\"></i>`"),
 ("""  const series=[['l',D.l_months||[]],['eb',D.eb_months||[]]].filter(s=>s[1].length); if(!series.length){ $('multi').parentElement.style.display='none'; return; }""",
  """  const LAB={}; const series=(D.series||[]).map(s=>{LAB[s.k]=s.label; return [s.k,s.pts];}).filter(s=>s[1].length); if(!series.length){ $('multi').parentElement.style.display='none'; return; }"""),
 ("${{l:'Delancey-Essex',eb:'East Broadway'}[cls]}", "${LAB[cls]}"),
 ("""  const per=['AM','Midday','PM','Saturday'];
  $('feis').innerHTML=`<div style="font-family:var(--mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)"><span>2011 sidewalk, effective width</span><span>per 15 min · AM · midday · PM · Saturday</span></div>`+(D.feis||[]).map(r=>`<div><span class="k">${r.sidewalk}</span><span><b>${r.AM?r.AM.eff_width_ft+' ft':''}</b> · ${per.map(p=>r[p]?r[p].per_15min:'–').join(' · ')}</span></div>`).join('');
""", ""),
 ("const MODEL='assets/clinton_84.glb';", "const MODEL='assets/mott_167.glb';"),
 ("const P=__POINTS__; const DOOR=P.site, STN=[P.delancey_essex_station[0],0,-P.delancey_essex_station[1]], BRG=[P.bridge_approach[0],0,-P.bridge_approach[1]], EC=[P.essex_crossing[0],0,-P.essex_crossing[1]];",
  "const P=__POINTS__; const DOOR=P.door, N=[0.956,0.292];   // N = the way the front faces, out over Mott Street\n const G=k=>[P[k][0],0,-P[k][1]], BOW=G('bowery_jz'), SPR=G('spring_6'), GRD=G('grand_bd'); const MID=[(BOW[0]+SPR[0]+GRD[0])/3,0,(BOW[2]+SPR[2]+GRD[2])/3];"),
])
a = js.index(' {p:[330,470,330]'); b = js.index('let renderer,scene,cam')
js = js[:a] + """ {p:[330,470,330],t:[0,8,0],s:250,o:0},                                               // s0 wide
 {p:[DOOR[0]+N[0]*70+40,110,DOOR[2]+N[1]*70+50],t:[DOOR[0]-8,10,DOOR[2]],s:50,o:-.42}, // s1 the lot (o = slide the picture sideways, clear of the text card)
 {p:[DOOR[0]+N[0]*42-6,80,DOOR[2]+N[1]*42+22],t:[DOOR[0],7,DOOR[2]],s:24,o:.46},      // s2 the dark door, from over the street
 {p:[DOOR[0]+N[0]*42+14,78,DOOR[2]+N[1]*42-26],t:[DOOR[0],9,DOOR[2]],s:30,o:-.46},    // s3 the tenants, the other way
 {p:[MID[0]+120,520,MID[2]+140],t:[MID[0]*0.6,0,MID[2]*0.6],s:330,o:0},               // s4 the trains, from above
 {p:[10,760,90],t:[0,0,0],s:280,o:0},                                                 // s5 plan of the block
 {p:[DOOR[0]+N[0]*60+30,95,DOOR[2]+N[1]*60+40],t:[DOOR[0],8,DOOR[2]],s:58,o:.42},     // s6 the rent, back at the door
 {p:[420,560,420],t:[0,8,0],s:320,o:0}];                                              // s7 wide, out
""" + js[b:]
js = sub(js, [
 ("if(n.startsWith('LES_MASSING')){o.castShadow=true;o.receiveShadow=true;if(m)m.color=new THREE.Color(0x302C28);}\n   else if(n.startsWith('SITE_84')){o.castShadow=true;if(m){m.color=new THREE.Color(0xFF6319);m.emissive=new THREE.Color(0xFF6319);m.emissiveIntensity=.5;}}",
  "if(n.startsWith('NOLITA_MASSING')){o.castShadow=true;o.receiveShadow=true;if(m)m.color=new THREE.Color(0x302C28);}\n   else if(n.startsWith('SITE_167')||n.startsWith('B167_BRICK')){o.castShadow=true;if(m){m.color=new THREE.Color(0x9A6048);m.emissive=new THREE.Color(0x9A6048);m.emissiveIntensity=.38;}}\n   else if(n.startsWith('B167_SITE')){if(m){m.color=new THREE.Color(0x00933C);m.emissive=new THREE.Color(0x2DBE6C);m.emissiveIntensity=.75;}}\n   else if(n.startsWith('B167_GLASS')){if(m)m.color=new THREE.Color(0x0D1714);}\n   else if(n.startsWith('B167_TRIM')){if(m){m.color=new THREE.Color(0xC9C2B4);m.emissive=new THREE.Color(0xC9C2B4);m.emissiveIntensity=.25;}}\n   else if(n.startsWith('B167_IRON')){if(m)m.color=new THREE.Color(0x0A0A0A);}"),
 ("const MONTHS=__MONTHS__;", "const MONTHS=__DARKMAX__;"),
 ("num.style.color=s.dataset.numc==='jz'?'var(--jz)':'var(--f)'; }", "num.style.color='var(--'+(s.dataset.numc||'f')+')'; }"),
])
js = sub(js, [
 ("const state={p:new THREE.Vector3(),t:new THREE.Vector3(),s:250}, goal={p:new THREE.Vector3(),t:new THREE.Vector3(),s:250};", "const state={p:new THREE.Vector3(),t:new THREE.Vector3(),s:250,o:0}, goal={p:new THREE.Vector3(),t:new THREE.Vector3(),s:250,o:0};"),
 ("goal.s=lerp(a.s,b.s,f)*mult();", "goal.s=lerp(a.s,b.s,f)*mult(); goal.o=innerWidth<760?0:lerp(a.o,b.o,f);"),
 ("if(reduced){state.p.copy(goal.p);state.t.copy(goal.t);state.s=goal.s;}", "if(reduced){state.p.copy(goal.p);state.t.copy(goal.t);state.s=goal.s;state.o=goal.o;}"),
 ("state.s+=(goal.s-state.s)*0.07;}", "state.s+=(goal.s-state.s)*0.07;state.o+=(goal.o-state.o)*0.07;}"),
 ("cam.left=-state.s*a; cam.right=state.s*a;", "const off=state.o*state.s*a; cam.left=-state.s*a-off; cam.right=state.s*a-off;"),
 ("state.p.copy(goal.p); state.t.copy(goal.t); state.s=goal.s; frame();", "state.p.copy(goal.p); state.t.copy(goal.t); state.s=goal.s; state.o=goal.o; frame();"),
 ("key.shadow.mapSize.set(2048,2048);", "key.shadow.mapSize.set(2048,2048); key.shadow.bias=-0.0006; key.shadow.normalBias=1.2;"),
])
js = sub(js, [
 ("const seg=t*(WP.length-1), i=Math.min(WP.length-2,Math.floor(seg)), f=smooth(seg-i), a=WP[i], b=WP[i+1];",
  "const yc=scrollY+innerHeight*0.5, cs=secs.map(x=>x.offsetTop+dm.offsetTop+x.offsetHeight/2); let k=0; while(k<cs.length-2&&yc>=cs[k+1])k++;\n  const seg=Math.min(WP.length-1,Math.max(0,k+(yc-cs[k])/(cs[k+1]-cs[k]))), i=Math.min(WP.length-2,Math.floor(seg)), f=smooth(seg-i), a=WP[i], b=WP[i+1];   // camera follows the sections, not raw scroll distance"),
])
head = open(os.path.join(S, 'mott_head.html')).read(); body = open(os.path.join(S, 'mott_body.html')).read()
open(os.path.join(S, 'mott_template.html'), 'w').write(head + css + '</head><body>\n' + body + js)
print('template written', len(head + css + body + js) // 1024, 'KB')
