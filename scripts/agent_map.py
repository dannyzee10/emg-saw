#!/usr/bin/env python3
"""
Agent World-Map — overlays SAW agent ownership on graphify's code graph and renders
a zoomable "world map": each agent is a continent (hull boundary + fill), each code
node is a glowing city, and dependencies are arcing light-trails between them.

    python scripts/agent_map.py            # reads graphify-out/graph.json + AGENT_OWNERSHIP.yml
                                           # writes agent_map.html (and opens it)

Zoom out = continents (agents) + cross-agent trails; zoom in = the cities (functions/
classes) each agent owns. Cross-agent edges = coordination hotspots.
"""
import json, os, sys, fnmatch, webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graphify-out", "graph.json")
OWN = os.path.join(ROOT, "AGENT_OWNERSHIP.yml")
OUT = os.path.join(ROOT, "agent_map.html")
DROP_TYPES = {"concept", "rationale"}      # graphify semantic nodes -> noise for this map


def load_ownership():
    import yaml
    with open(OWN, encoding="utf-8") as f:
        y = yaml.safe_load(f)
    return y["agents"]


def owner_of(src, agents):
    if not src:
        return None
    src = src.replace("\\", "/")
    for name, spec in agents.items():                 # exact file overrides win
        for f in spec.get("files", []) or []:
            if src == f.replace("\\", "/"):
                return name
    for name, spec in agents.items():                 # then globs
        for gpat in spec.get("globs", []) or []:
            if fnmatch.fnmatch(src, gpat) or fnmatch.fnmatch(src, gpat.rstrip("/*") + "/*") \
               or src.startswith(gpat.rstrip("/*") + "/"):
                return name
    return None


def main():
    agents = load_ownership()
    g = json.load(open(GRAPH, encoding="utf-8"))
    raw_nodes = g["nodes"]
    raw_links = g.get("links", g.get("edges", []))

    # assign + filter
    nodes, keep = [], set()
    deg = {}
    for n in raw_nodes:
        if n.get("file_type") in DROP_TYPES:
            continue
        a = owner_of(n.get("source_file"), agents)
        if a is None:
            a = "systems-architect"                   # unowned -> governance by default
        nid = n["id"]
        keep.add(nid)
        deg[nid] = 0
        nodes.append({
            "id": nid, "label": n.get("label", nid), "agent": a,
            "file": n.get("source_file", ""), "loc": n.get("source_location", ""),
            "ftype": n.get("file_type", "code"),
        })

    links = []
    for e in raw_links:
        s, t = e.get("source"), e.get("target")
        if s in keep and t in keep and s != t:
            deg[s] += 1; deg[t] += 1
            links.append({"source": s, "target": t, "relation": e.get("relation", "")})

    # radius by degree; mark god nodes (top by degree)
    by_deg = sorted(nodes, key=lambda n: deg[n["id"]], reverse=True)
    god = {n["id"] for n in by_deg[:14]}
    for n in nodes:
        d = deg[n["id"]]
        n["deg"] = d
        n["r"] = round(4 + min(16, d * 1.4), 1)
        n["god"] = n["id"] in god
    agent_of = {n["id"]: n["agent"] for n in nodes}
    for l in links:
        l["cross"] = agent_of[l["source"]] != agent_of[l["target"]]

    present = [a for a in agents if any(n["agent"] == a for n in nodes)]
    agent_list = [{"id": a, "color": agents[a]["color"], "role": agents[a].get("role", ""),
                   "count": sum(1 for n in nodes if n["agent"] == a),
                   "cross": sum(1 for l in links if l["cross"] and
                                (agent_of[l["source"]] == a or agent_of[l["target"]] == a))}
                  for a in present]

    data = {"nodes": nodes, "links": links, "agents": agent_list}
    html = HTML.replace("__DATA__", json.dumps(data)).replace("__COMMIT__",
             str(g.get("built_at_commit", "?"))[:8])
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"agent_map.html written: {len(nodes)} cities, {len(links)} trails, "
          f"{len(agent_list)} continents -> {OUT}")
    try:
        webbrowser.open("file://" + OUT.replace("\\", "/"))
    except Exception:
        pass


HTML = r"""<!doctype html><html><head><meta charset="utf-8">
<title>EMG SAW — Agent World Map</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  html,body{margin:0;height:100%;background:radial-gradient(1200px 800px at 50% 40%,#0e1626 0%,#070a12 70%);
            color:#cdd8ea;font-family:'Segoe UI',Arial;overflow:hidden}
  #map{width:100vw;height:100vh;display:block}
  #hud{position:fixed;top:14px;left:14px;background:rgba(12,18,30,.82);
       border:1px solid #1e2c44;border-radius:10px;padding:12px 14px;max-width:290px;backdrop-filter:blur(4px)}
  #hud h1{margin:0 0 2px;font-size:15px;color:#fff}
  #hud .sub{font-size:11px;color:#8aa0c0;margin-bottom:8px}
  .leg{display:flex;align-items:center;gap:8px;padding:3px 4px;border-radius:6px;cursor:pointer;font-size:12px}
  .leg:hover{background:#16233a}
  .dot{width:11px;height:11px;border-radius:50%}
  .leg .cnt{margin-left:auto;color:#7f93b2;font-size:11px}
  #tip{position:fixed;pointer-events:none;background:rgba(10,16,26,.95);border:1px solid #2b3f60;
       border-radius:6px;padding:6px 9px;font-size:12px;color:#e6eefc;opacity:0;transition:opacity .1s}
  #foot{position:fixed;bottom:10px;left:14px;font-size:11px;color:#61748f}
</style></head><body>
<svg id="map"></svg>
<div id="hud"><h1>EMG SAW — Agent World Map</h1>
  <div class="sub">continents = agents · cities = code · trails = dependencies · scroll to zoom</div>
  <div id="legend"></div></div>
<div id="tip"></div>
<div id="foot">graph @ __COMMIT__ · click a continent to isolate · drag a city to move</div>
<script>
const D = __DATA__;
const W = innerWidth, H = innerHeight;
const svg = d3.select("#map").attr("viewBox",[0,0,W,H]);
const defs = svg.append("defs");
const gl = defs.append("filter").attr("id","glow").attr("x","-60%").attr("y","-60%").attr("width","220%").attr("height","220%");
gl.append("feGaussianBlur").attr("stdDeviation",3.2).attr("result","b");
const fm = gl.append("feMerge"); fm.append("feMergeNode").attr("in","b"); fm.append("feMergeNode").attr("in","SourceGraphic");
const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.15,7]).on("zoom",e=>g.attr("transform",e.transform)));

const agents = D.agents, byId = Object.fromEntries(agents.map(a=>[a.id,a]));
const R = Math.min(W,H)*0.33;
agents.forEach((a,i)=>{const ang=(i/agents.length)*2*Math.PI-Math.PI/2; a.ax=W/2+R*Math.cos(ang); a.ay=H/2+R*Math.sin(ang);});
D.nodes.forEach(n=>{const a=byId[n.agent]||{ax:W/2,ay:H/2}; n.x=a.ax+(Math.random()-0.5)*90; n.y=a.ay+(Math.random()-0.5)*90;});

const hullL=g.append("g"), linkL=g.append("g"), nodeL=g.append("g"), labL=g.append("g");
const hull = hullL.selectAll("path").data(agents).join("path")
  .attr("fill",d=>d.color).attr("fill-opacity",.06).attr("stroke",d=>d.color)
  .attr("stroke-opacity",.55).attr("stroke-width",1.6).attr("stroke-linejoin","round");
const link = linkL.selectAll("path").data(D.links).join("path").attr("fill","none")
  .attr("stroke",d=>d.cross?"#63c9ff":"#274063")
  .attr("stroke-width",d=>d.cross?1.2:.6).attr("stroke-opacity",d=>d.cross?.55:.22);
const node = nodeL.selectAll("circle").data(D.nodes).join("circle")
  .attr("r",d=>d.r).attr("fill",d=>(byId[d.agent]||{color:"#889"}).color)
  .attr("stroke","#0a0e14").attr("stroke-width",.6).attr("filter","url(#glow)")
  .style("cursor","pointer")
  .on("mousemove",(e,d)=>{const t=d3.select("#tip");
     t.style("left",(e.clientX+14)+"px").style("top",(e.clientY+12)+"px").style("opacity",1)
      .html(`<b>${d.label}</b><br><span style='color:#8aa0c0'>${d.agent}</span><br>${d.file}${d.loc?":"+d.loc:""} · deg ${d.deg}`);})
  .on("mouseout",()=>d3.select("#tip").style("opacity",0))
  .call(d3.drag().on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y;})
     .on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y;}).on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null;}));
const glab = labL.selectAll("text.g").data(D.nodes.filter(n=>n.god)).join("text").attr("class","g")
  .text(d=>d.label).attr("font-size",11).attr("fill","#dfe9fb").attr("text-anchor","middle").style("pointer-events","none");
const alab = labL.selectAll("text.a").data(agents).join("text").attr("class","a")
  .text(d=>d.id.replace(/-/g," ").toUpperCase()).attr("font-size",18).attr("font-weight",800)
  .attr("letter-spacing","1.5px").attr("fill",d=>d.color)
  .attr("text-anchor","middle").attr("opacity",.92).style("pointer-events","none")
  .style("text-shadow","0 0 12px currentColor");

const sim = d3.forceSimulation(D.nodes)
  .force("link",d3.forceLink(D.links).id(d=>d.id).distance(d=>d.cross?130:42).strength(.18))
  .force("charge",d3.forceManyBody().strength(-34))
  .force("x",d3.forceX(d=>(byId[d.agent]||{ax:W/2}).ax).strength(.13))
  .force("y",d3.forceY(d=>(byId[d.agent]||{ay:H/2}).ay).strength(.13))
  .force("collide",d3.forceCollide().radius(d=>d.r+3.5))
  .on("tick",tick);

function expand(h){const cx=d3.mean(h,p=>p[0]),cy=d3.mean(h,p=>p[1]),pad=26;
  return h.map(p=>{const dx=p[0]-cx,dy=p[1]-cy,l=Math.hypot(dx,dy)||1;return[p[0]+dx/l*pad,p[1]+dy/l*pad];});}
function tick(){
  link.attr("d",d=>{const s=d.source,t=d.target,dr=Math.hypot(t.x-s.x,t.y-s.y)*1.7;
     return `M${s.x},${s.y}A${dr},${dr} 0 0,1 ${t.x},${t.y}`;});
  node.attr("cx",d=>d.x).attr("cy",d=>d.y);
  glab.attr("x",d=>d.x).attr("y",d=>d.y-d.r-4);
  hull.attr("d",a=>{const pts=D.nodes.filter(n=>n.agent===a.id).map(n=>[n.x,n.y]);
     if(pts.length<3){if(!pts.length)return null;const cx=d3.mean(pts,p=>p[0]),cy=d3.mean(pts,p=>p[1]),r=46;
       return `M${cx-r},${cy}a${r},${r} 0 1,0 ${2*r},0a${r},${r} 0 1,0 ${-2*r},0`;}
     return "M"+expand(d3.polygonHull(pts)).map(p=>p.join(",")).join("L")+"Z";});
  alab.attr("x",a=>{const p=D.nodes.filter(n=>n.agent===a.id);return p.length?d3.mean(p,n=>n.x):a.ax;})
      .attr("y",a=>{const p=D.nodes.filter(n=>n.agent===a.id);return p.length?d3.min(p,n=>n.y)-30:a.ay;});
}
// legend + isolate
let iso=null;
const leg=d3.select("#legend");
agents.forEach(a=>{const row=leg.append("div").attr("class","leg").on("click",()=>{iso=(iso===a.id?null:a.id);apply();});
  row.append("div").attr("class","dot").style("background",a.color);
  row.append("div").html(`${a.id}<br><span style='color:#6f84a4;font-size:10px'>${a.role}</span>`);
  row.append("div").attr("class","cnt").text(a.count);});
function apply(){const on=x=>iso===null||x===iso;
  node.attr("opacity",d=>on(d.agent)?1:.08);
  hull.attr("opacity",a=>on(a.id)?1:.06);
  alab.attr("opacity",a=>on(a.id)?.9:.12);
  glab.attr("opacity",d=>on(d.agent)?1:.05);
  link.attr("opacity",d=>iso===null?1:((d.source.agent||agentOf(d.source))===iso||(d.target.agent||agentOf(d.target))===iso?.9:.04));}
function agentOf(x){return typeof x==='object'?x.agent:(D.nodes.find(n=>n.id===x)||{}).agent;}
</script></body></html>"""


if __name__ == "__main__":
    main()
