#!/usr/bin/env python3
"""Turn an idea-graph JSON spec into a self-contained interactive HTML deliverable.

The model does the thinking — reading the project and deciding what the concepts
(nodes) and relationships (edges) are. This script does the deterministic part:
it computes a stable force-directed layout (seeded, so the same spec always
lays out the same way), bakes the positions into a single HTML file with no
external dependencies (inline SVG + JS: pan, zoom, click-to-focus, clusters,
legend, search), and prints graph analytics — clusters, hubs, and orphans — so
the model can write an honest read-out of what the graph reveals.

The HTML is the deliverable: it sits in the project, opens in any browser
offline, and is meant to be shared to explain the ideas to others.

Spec (JSON):
{
  "title": "Acme — Idea Map",
  "nodes": [
    {"id": "subs", "label": "Subscription product", "cluster": "Product",
     "summary": "The new recurring-revenue offer at the centre of the strategy."}
  ],
  "edges": [
    {"source": "subs", "target": "younger", "label": "targets"}
  ]
}

Usage:  python build_graph.py SPEC.json OUTPUT.html
        (also writes OUTPUT.mmd — a Mermaid source for pasting into docs)
"""
import json
import math
import random
import sys
from pathlib import Path

PALETTE = [
    "#2d6a4f", "#1d6fb8", "#b7791f", "#7048a6", "#b23a48",
    "#0e7c7b", "#a64d79", "#3a7d44", "#c2571a", "#4a5568",
]
W = H = 1000.0


def layout(nodes, edges, seed=7, iters=400):
    """Deterministic Fruchterman-Reingold layout into a W x H box."""
    rng = random.Random(seed)
    n = len(nodes)
    if n == 0:
        return
    pos = {nd["id"]: [rng.uniform(0, W), rng.uniform(0, H)] for nd in nodes}
    ids = [nd["id"] for nd in nodes]
    adj = [(e["source"], e["target"]) for e in edges
           if e.get("source") in pos and e.get("target") in pos]
    area = W * H
    k = math.sqrt(area / n) * 0.8
    t = W / 10.0
    cool = t / (iters + 1)

    for _ in range(iters):
        disp = {i: [0.0, 0.0] for i in ids}
        # repulsion between every pair
        for a in range(n):
            ia = ids[a]
            for b in range(a + 1, n):
                ib = ids[b]
                dx = pos[ia][0] - pos[ib][0]
                dy = pos[ia][1] - pos[ib][1]
                dist = math.hypot(dx, dy) or 0.01
                force = (k * k) / dist
                ux, uy = dx / dist, dy / dist
                disp[ia][0] += ux * force
                disp[ia][1] += uy * force
                disp[ib][0] -= ux * force
                disp[ib][1] -= uy * force
        # attraction along edges
        for s, d in adj:
            dx = pos[s][0] - pos[d][0]
            dy = pos[s][1] - pos[d][1]
            dist = math.hypot(dx, dy) or 0.01
            force = (dist * dist) / k
            ux, uy = dx / dist, dy / dist
            disp[s][0] -= ux * force
            disp[s][1] -= uy * force
            disp[d][0] += ux * force
            disp[d][1] += uy * force
        # limit by temperature, keep in box
        for i in ids:
            dx, dy = disp[i]
            dlen = math.hypot(dx, dy) or 0.01
            pos[i][0] += (dx / dlen) * min(dlen, t)
            pos[i][1] += (dy / dlen) * min(dlen, t)
            pos[i][0] = min(W - 20, max(20, pos[i][0]))
            pos[i][1] = min(H - 20, max(20, pos[i][1]))
        t -= cool

    for nd in nodes:
        nd["x"] = round(pos[nd["id"]][0], 1)
        nd["y"] = round(pos[nd["id"]][1], 1)


def analyse(nodes, edges):
    deg = {nd["id"]: 0 for nd in nodes}
    for e in edges:
        if e.get("source") in deg:
            deg[e["source"]] += 1
        if e.get("target") in deg:
            deg[e["target"]] += 1
    for nd in nodes:
        nd["degree"] = deg.get(nd["id"], 0)

    # connected components (undirected)
    adj = {nd["id"]: set() for nd in nodes}
    for e in edges:
        s, d = e.get("source"), e.get("target")
        if s in adj and d in adj:
            adj[s].add(d)
            adj[d].add(s)
    seen, components = set(), []
    for nid in adj:
        if nid in seen:
            continue
        stack, comp = [nid], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack.extend(adj[x] - seen)
        components.append(comp)

    label = {nd["id"]: nd.get("label", nd["id"]) for nd in nodes}
    orphans = [label[i] for i in deg if deg[i] == 0]
    hubs = sorted(((deg[i], label[i]) for i in deg), reverse=True)[:5]
    clusters = {}
    for nd in nodes:
        clusters.setdefault(nd.get("cluster", "Uncategorised"), []).append(nd["label"])
    return {
        "nodes": len(nodes), "edges": len(edges),
        "clusters": clusters,
        "orphans": orphans,
        "hubs": [h[1] for h in hubs if h[0] > 0],
        "components": len(components),
    }


def assign_colors(nodes):
    clusters = []
    cmap = {}
    for nd in nodes:
        c = nd.get("cluster", "Uncategorised")
        if c not in cmap:
            cmap[c] = PALETTE[len(cmap) % len(PALETTE)]
            clusters.append({"name": c, "color": cmap[c]})
        nd["color"] = cmap[c]
    return clusters


def write_mermaid(spec, out_mmd):
    lines = ["graph LR"]
    safe = lambda s: "".join(ch if ch.isalnum() else "_" for ch in str(s))
    for nd in spec["nodes"]:
        lines.append(f'  {safe(nd["id"])}["{nd.get("label", nd["id"])}"]')
    for e in spec.get("edges", []):
        lbl = e.get("label", "")
        arrow = f'-- {lbl} -->' if lbl else "-->"
        lines.append(f'  {safe(e["source"])} {arrow} {safe(e["target"])}')
    Path(out_mmd).write_text("\n".join(lines), encoding="utf-8")


def build(spec, out_html):
    nodes = spec.get("nodes", [])
    edges = spec.get("edges", [])
    clusters = assign_colors(nodes)
    stats = analyse(nodes, edges)
    layout(nodes, edges)
    data = {
        "title": spec.get("title", "Idea Graph"),
        "nodes": nodes, "edges": edges, "clusters": clusters,
    }
    html = TEMPLATE.replace("__TITLE__", json.dumps(data["title"])[1:-1])
    html = html.replace("__GRAPH_DATA__", json.dumps(data))
    Path(out_html).write_text(html, encoding="utf-8")
    return stats


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --ink:#1a1f2b; --muted:#5b6472; --rule:#e2e6ea; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Segoe UI",-apple-system,Arial,sans-serif; color:var(--ink); }
  header { padding:12px 18px; border-bottom:1px solid var(--rule); display:flex;
           gap:16px; align-items:center; flex-wrap:wrap; }
  header h1 { font-size:16px; margin:0; }
  #search { padding:6px 10px; border:1px solid var(--rule); border-radius:6px; font-size:13px; }
  #legend { display:flex; gap:14px; flex-wrap:wrap; font-size:12px; color:var(--muted); }
  .sw { display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:5px; vertical-align:-1px; }
  #wrap { display:flex; height:calc(100vh - 58px); }
  #stage { flex:1; background:#fbfcfd; overflow:hidden; cursor:grab; }
  #stage:active { cursor:grabbing; }
  #panel { width:300px; border-left:1px solid var(--rule); padding:16px; overflow:auto;
           font-size:13px; line-height:1.5; }
  #panel h2 { font-size:15px; margin:0 0 4px; }
  #panel .cl { color:var(--muted); font-size:12px; margin-bottom:10px; }
  #panel .hint { color:var(--muted); font-style:italic; }
  .edge { stroke:#c2cad3; stroke-width:1.2; }
  .edge.lit { stroke:#1a1f2b; stroke-width:2; }
  .node circle { stroke:#fff; stroke-width:2; cursor:pointer; }
  .node text { font-size:12px; fill:var(--ink); pointer-events:none; }
  .dim { opacity:0.15; }
  .elabel { font-size:9px; fill:var(--muted); pointer-events:none; }
</style></head>
<body>
<header>
  <h1 id="title"></h1>
  <input id="search" placeholder="Search ideas…" autocomplete="off">
  <div id="legend"></div>
</header>
<div id="wrap">
  <div id="stage"><svg id="svg" width="100%" height="100%"><g id="vp"></g></svg></div>
  <div id="panel"><p class="hint">Click an idea to see how it connects. Drag to pan, scroll to zoom.</p></div>
</div>
<script>
const DATA = __GRAPH_DATA__;
document.getElementById('title').textContent = DATA.title;
document.title = DATA.title;
const vp = document.getElementById('vp'), svg = document.getElementById('svg');
const NS = 'http://www.w3.org/2000/svg';
const byId = {}; DATA.nodes.forEach(n => byId[n.id] = n);
const nbr = {}; DATA.nodes.forEach(n => nbr[n.id] = new Set());
DATA.edges.forEach(e => { if(nbr[e.source]&&nbr[e.target]){nbr[e.source].add(e.target); nbr[e.target].add(e.source);} });

// edges
const edgeEls = DATA.edges.map(e => {
  const a = byId[e.source], b = byId[e.target];
  if(!a||!b) return null;
  const g = document.createElementNS(NS,'g');
  const ln = document.createElementNS(NS,'line');
  ln.setAttribute('x1',a.x); ln.setAttribute('y1',a.y);
  ln.setAttribute('x2',b.x); ln.setAttribute('y2',b.y);
  ln.setAttribute('class','edge'); g.appendChild(ln);
  if(e.label){
    const t = document.createElementNS(NS,'text');
    t.setAttribute('x',(a.x+b.x)/2); t.setAttribute('y',(a.y+b.y)/2);
    t.setAttribute('class','elabel'); t.setAttribute('text-anchor','middle');
    t.textContent = e.label; g.appendChild(t);
  }
  vp.appendChild(g); return {e, g, ln};
}).filter(Boolean);

// nodes
const nodeEls = {};
DATA.nodes.forEach(n => {
  const g = document.createElementNS(NS,'g'); g.setAttribute('class','node');
  const r = 8 + Math.min(n.degree||0,8)*2.2;
  const c = document.createElementNS(NS,'circle');
  c.setAttribute('cx',n.x); c.setAttribute('cy',n.y); c.setAttribute('r',r);
  c.setAttribute('fill',n.color);
  const t = document.createElementNS(NS,'text');
  t.setAttribute('x',n.x+r+3); t.setAttribute('y',n.y+4); t.textContent = n.label;
  g.appendChild(c); g.appendChild(t);
  g.addEventListener('click',ev=>{ev.stopPropagation(); focus(n.id);});
  vp.appendChild(g); nodeEls[n.id] = {g,c,t,n};
});

// legend
document.getElementById('legend').innerHTML = DATA.clusters.map(c =>
  `<span><span class="sw" style="background:${c.color}"></span>${c.name}</span>`).join('');

// pan / zoom
let tx=0, ty=0, s=1;
function apply(){ vp.setAttribute('transform',`translate(${tx},${ty}) scale(${s})`); }
function fit(){
  const xs=DATA.nodes.map(n=>n.x), ys=DATA.nodes.map(n=>n.y);
  const minX=Math.min(...xs)-60,maxX=Math.max(...xs)+160,minY=Math.min(...ys)-40,maxY=Math.max(...ys)+40;
  const r=svg.getBoundingClientRect();
  s=Math.min(r.width/(maxX-minX), r.height/(maxY-minY), 1.6);
  tx=-minX*s + (r.width-(maxX-minX)*s)/2; ty=-minY*s + (r.height-(maxY-minY)*s)/2; apply();
}
let drag=null;
svg.addEventListener('mousedown',e=>{drag={x:e.clientX,y:e.clientY,tx,ty};});
window.addEventListener('mousemove',e=>{if(drag){tx=drag.tx+(e.clientX-drag.x);ty=drag.ty+(e.clientY-drag.y);apply();}});
window.addEventListener('mouseup',()=>drag=null);
svg.addEventListener('wheel',e=>{e.preventDefault();
  const r=svg.getBoundingClientRect(), mx=e.clientX-r.left, my=e.clientY-r.top;
  const ns=Math.min(4,Math.max(0.2, s*(e.deltaY<0?1.1:0.9)));
  tx=mx-(mx-tx)*(ns/s); ty=my-(my-ty)*(ns/s); s=ns; apply();
},{passive:false});
svg.addEventListener('click',()=>clearFocus());

function focus(id){
  const keep=new Set([id,...nbr[id]]);
  DATA.nodes.forEach(n=>nodeEls[n.id].g.classList.toggle('dim',!keep.has(n.id)));
  edgeEls.forEach(o=>{
    const on = o.e.source===id||o.e.target===id;
    o.g.classList.toggle('dim',!on); o.ln.classList.toggle('lit',on);
  });
  const n=byId[id];
  const conns=[...nbr[id]].map(x=>byId[x].label).join(', ')||'<span class="hint">no connections — an orphan idea</span>';
  document.getElementById('panel').innerHTML =
    `<h2>${n.label}</h2><div class="cl">${n.cluster||''}</div>`+
    (n.summary?`<p>${n.summary}</p>`:'')+
    `<p><b>Connects to:</b><br>${conns}</p>`;
}
function clearFocus(){
  DATA.nodes.forEach(n=>nodeEls[n.id].g.classList.remove('dim'));
  edgeEls.forEach(o=>{o.g.classList.remove('dim'); o.ln.classList.remove('lit');});
  document.getElementById('panel').innerHTML='<p class="hint">Click an idea to see how it connects. Drag to pan, scroll to zoom.</p>';
}
document.getElementById('search').addEventListener('input',e=>{
  const q=e.target.value.toLowerCase().trim();
  DATA.nodes.forEach(n=>{
    const hit = q && n.label.toLowerCase().includes(q);
    nodeEls[n.id].g.classList.toggle('dim', q && !hit);
    nodeEls[n.id].c.setAttribute('stroke', hit?'#1a1f2b':'#fff');
  });
});
fit(); window.addEventListener('resize',fit);
</script>
</body></html>
"""


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        sys.exit("Usage: python build_graph.py SPEC.json OUTPUT.html")
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out_html = Path(argv[1])
    stats = build(spec, out_html)
    out_mmd = out_html.with_suffix(".mmd")
    write_mermaid(spec, out_mmd)

    print(f"Wrote {out_html}  ({stats['nodes']} ideas, {stats['edges']} links)")
    print(f"Wrote {out_mmd}  (Mermaid source)")
    print("\n--- graph analytics (for your read-out) ---")
    print(f"Clusters ({len(stats['clusters'])}):")
    for name, members in stats["clusters"].items():
        print(f"  • {name}: {', '.join(members)}")
    print(f"Most-connected ideas: {', '.join(stats['hubs']) or '(none)'}")
    print(f"Orphan ideas (no links): {', '.join(stats['orphans']) or '(none)'}")
    print(f"Disconnected components: {stats['components']} "
          f"({'one connected web' if stats['components']==1 else 'the graph splits — possible gaps'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
