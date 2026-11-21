"""Schemi SVG dei percorsi ottimali (grafici non in scala geografica)."""

from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from .instance import Instance
from .search import Ricerca


def _simbolo(percorso: tuple[int,...], inst:Instance, y:int, maincolor:str, width:int=1210) -> str:
    n=len(percorso)
    places=[(i,100+i*(width-200)/(n-1)) for i in range(n)]
    out=[]
    for (i,x1),(j,x2) in zip(places,places[1:]):
        v=inst.matrice[percorso[i]][percorso[j]]
        out.append(f'<line x1="{x1+25:.1f}" y1="{y}" x2="{x2-25:.1f}" y2="{y}" stroke="{maincolor}" stroke-width="3" marker-end="url(#arrow)"/>')
        out.append(f'<text x="{(x1+x2)/2:.1f}" y="{y-18}" font-size="16" font-weight="600" text-anchor="middle" fill="#334155">{str(v)} km</text>')
    for (i,x) in places:
        v=percorso[i]
        isdepot=(v==0)
        name=inst.nome(v)
        if len(name)>17:
            fragments=name.split(' ')
            first=' '.join(fragments[:1]);last=' '.join(fragments[1:])
            name=f'{first} / {last}'
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="27" fill="{maincolor if isdepot else "#ffffff"}" stroke="{maincolor}" stroke-width="3"/>')
        out.append(f'<text x="{x:.1f}" y="{y+6}" text-anchor="middle" font-size="17" font-weight="bold" fill="{"#ffffff" if isdepot else maincolor}">{escape(inst.ids[v])}</text>')
        out.append(f'<text x="{x:.1f}" y="{y+55}" text-anchor="middle" font-size="14" fill="#172033">{escape(name)}</text>')
    return '\n'.join(out)


def _base(titolo:str,body:str,height:int) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1210" height="{height}" viewBox="0 0 1210 {height}">
<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7 z" fill="#64748b"/></marker></defs>
<rect width="1210" height="{height}" fill="#f8fafc"/>
<text x="55" y="45" font-size="24" font-family="DejaVu Sans, sans-serif" font-weight="bold" fill="#0f172a">{escape(titolo)}</text>
<text x="55" y="76" font-size="15" font-family="DejaVu Sans, sans-serif" fill="#475569">Grafo diretto: i percorsi partono dal deposito D0 e vi ritornano. Schema non in scala geografica.</text>
<g font-family="DejaVu Sans, sans-serif">{body}</g></svg>'''


def crea_diagrammi(inst:Instance,ric:Ricerca,cartella:Path) -> list[Path]:
    cartella.mkdir(parents=True,exist_ok=True)
    a=ric.migliore_a
    b,c=ric.migliore_b
    diagramma_a=_base(f'Scenario A  |  un veicolo da {inst.scenario_a.capacita_kg} kg  |  {a.km} km',_simbolo(a.nodi,inst,155,'#124e80'),278)
    diagramma_b=_base(f'Scenario B  |  due veicoli da {inst.scenario_b.capacita_kg} kg  |  {str(b.km+c.km).replace(".",",")} km',
       f'<text x="55" y="117" fill="#124e80" font-weight="bold" font-size="18">Mezzo 1 - {b.kg} kg</text>'+ _simbolo(b.nodi,inst,185,'#124e80')+
       f'<text x="55" y="325" fill="#9d4b14" font-weight="bold" font-size="18">Mezzo 2 - {c.kg} kg</text>'+ _simbolo(c.nodi,inst,385,'#9d4b14'),509)
    paths=[]
    for name,data in [('Grafo_percorso_A.svg',diagramma_a),('Grafo_percorsi_B.svg',diagramma_b)]:
        path=cartella/name
        path.write_text(data,encoding='utf-8')
        paths.append(path)
    return paths
