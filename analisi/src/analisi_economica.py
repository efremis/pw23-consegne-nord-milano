"""Confronto economico verificabile dei percorsi di PaneLinea Nord Milano.

Lettura diretta dell'istanza e degli itinerari ottimi della ricerca esaustiva.
Nessun valore di costo è trascritto manualmente nel codice.
Richiede soltanto Python 3.10+ e la libreria standard.
"""
from __future__ import annotations
import argparse
import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

D=Decimal
CENT=D('0.01')

def dec(v):
    return D(str(v))

def cent(v):
    return v.quantize(CENT, rounding=ROUND_HALF_UP)

def load(base: Path):
    instance=json.loads((base/'dati'/'istanza_ferrara.json').read_text(encoding='utf-8'))
    routes=json.loads((base/'dati'/'soluzioni_ottime.json').read_text(encoding='utf-8'))
    return instance,routes

def check(instance, routes):
    nodes=instance['ordine_nodi']; mat=[[dec(x) for x in row] for row in instance['matrice_distanze_km']]
    assert len(nodes)==6 and all(len(row)==6 for row in mat)
    demands={n['id']:int(n['kg']) for n in instance['nodi'] if n['id']!='D0'}
    assert sum(demands.values())==780
    cfg=instance['scenari_veicoli']
    params=instance['parametri_operativi']
    velocity=dec(params['velocita_media_km_h'])
    unload=int(params['minuti_scarico_per_cliente']); load_min=int(params['minuti_carico_deposito_per_veicolo'])
    seen={}
    for name in ('scenario_A','scenario_B'):
        block=routes[name]
        selected=block['percorsi']
        assert len(selected)==cfg[name]['numero_veicoli']
        seen[name]=[]
        for route in selected:
            ids=route['nodi']; assert ids[0]==ids[-1]=='D0'
            visited=ids[1:-1]; assert len(visited)==len(set(visited))
            kg=sum(demands[n] for n in visited)
            assert kg==int(route['kg_consegnati'])
            assert kg<=cfg[name]['capacita_kg_per_veicolo']
            km=sum((mat[nodes.index(i)][nodes.index(j)] for i,j in zip(ids,ids[1:])),D(0))
            assert abs(km-dec(route['km']))<D('0.000001')
            hours=km/velocity + dec(unload*len(visited)+load_min)/D(60)
            assert abs(hours-dec(route['ore_impegnate_inclusi_carico_e_scarico']))<=D('0.00001')
            seen[name]+=visited
        assert set(seen[name])==set(demands) and len(seen[name])==len(demands)
        assert sum(dec(x['km']) for x in selected)==dec(block['km_totali'])
    assert len(routes['scenario_B']['percorsi'])==2
    assert routes['enumerazione']['permutazioni_valutate_scenario_A']==120
    assert routes['enumerazione']['coppie_di_rotte_valutate_scenario_B']==48
    return True

def total_cost(vehicles, rent, rate_km, km, rate_hour, driver_hours):
    return dec(vehicles)*dec(rent)+dec(rate_km)*dec(km)+dec(rate_hour)*dec(driver_hours)

def scenario(instance, routes, key):
    v=instance['scenari_veicoli'][key]; ops=instance['parametri_operativi']
    speed=dec(ops['velocita_media_km_h']); unloading=int(ops['minuti_scarico_per_cliente']); loading=int(ops['minuti_carico_deposito_per_veicolo'])
    km=dec(routes[key]['km_totali'])
    tours=routes[key]['percorsi']
    durations=[dec(x['km'])/speed+dec(int(x['numero_clienti'])*unloading+loading)/D(60) for x in tours]
    h=sum(durations,D(0))
    n=int(v['numero_veicoli']); rent=dec(v['noleggio_euro_giorno_per_veicolo']); kmprice=dec(v['costo_euro_km']); hourly=dec(v['costo_autista_euro_ora'])
    parts={'noleggio':dec(n)*rent,'chilometrico':km*kmprice,'autisti':h*hourly}
    total=sum(parts.values(),D(0))
    assert cent(total)==dec(routes[key]['costi_base']['totale_euro']),f'Costo non coincidente per {key}'
    return {'veicoli':n,'km':km,'durate':durations,'ore_autista_somma':h,'ore_completamento':max(durations),'noleggio_veicolo':rent,'costo_km':kmprice,'costo_ora':hourly,'componenti':parts,'totale':total}

def csv_write(path,columns,rows):
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=columns,delimiter=';');w.writeheader()
        for row in rows:w.writerow({key:row.get(key,'') for key in columns})

def f(v,places=2):
    return str(dec(v).quantize(D(1).scaleb(-places),rounding=ROUND_HALF_UP))

def fmt(v):
    return f(v,2)

def build(base: Path, out: Path):
    inst,routes=load(base); check(inst,routes)
    a=scenario(inst,routes,'scenario_A');b=scenario(inst,routes,'scenario_B')
    out.mkdir(parents=True,exist_ok=True);(out/'grafici').mkdir(exist_ok=True)
    margin=b['totale']-a['totale']
    saved=a['ore_completamento']-b['ore_completamento']
    crossover_A=(b['totale']-a['componenti']['noleggio']-a['componenti']['autisti'])/a['km']
    crossover_rent_B=(a['totale']-b['componenti']['chilometrico']-b['componenti']['autisti'])/dec(b['veicoli'])
    crossover_rent_A=b['totale']-a['componenti']['chilometrico']-a['componenti']['autisti']
    values_A=[D(40+i*5)/100 for i in range(29)] # 0.40...1.80
    sensitivity_A=[]
    for price in values_A:
        ta=total_cost(a['veicoli'],a['noleggio_veicolo'],price,a['km'],a['costo_ora'],a['ore_autista_somma'])
        sensitivity_A.append({'prezzo_A_euro_km':fmt(price),'costo_A_euro':fmt(ta),'costo_B_euro':fmt(b['totale']),'differenza_B_meno_A_euro':fmt(b['totale']-ta),'piu_conveniente':'A' if ta<b['totale'] else ('B' if ta>b['totale'] else 'pari')})
    rent_values_B=[D(35+i) for i in range(41)] # 35..75 EUR/mezzo/giorno
    sensitivity_B=[]
    for rent in rent_values_B:
        tb=total_cost(b['veicoli'],rent,b['costo_km'],b['km'],b['costo_ora'],b['ore_autista_somma'])
        sensitivity_B.append({'noleggio_B_euro_veicolo_giorno':fmt(rent),'costo_A_euro':fmt(a['totale']),'costo_B_euro':fmt(tb),'differenza_B_meno_A_euro':fmt(tb-a['totale']),'piu_conveniente':'A' if a['totale']<tb else ('B' if a['totale']>tb else 'pari')})
    combos=[]
    for rent in [D(x) for x in [40,45,50,55,58,60,65,70]]:
        for price in [D(x)/100 for x in [55,65,75,85,95,110,125,140,155,170]]:
            ta=total_cost(a['veicoli'],a['noleggio_veicolo'],price,a['km'],a['costo_ora'],a['ore_autista_somma'])
            tb=total_cost(b['veicoli'],rent,b['costo_km'],b['km'],b['costo_ora'],b['ore_autista_somma'])
            combos.append({'prezzo_A_euro_km':fmt(price),'noleggio_B_euro_veicolo_giorno':fmt(rent),'costo_A_euro':fmt(ta),'costo_B_euro':fmt(tb),'delta_B_meno_A_euro':fmt(tb-ta),'piu_conveniente':'A' if ta<tb else ('B' if ta>tb else 'pari')})
    def serial_scenario(s):
        return {'veicoli':s['veicoli'],'km_totali':float(s['km']),'ore_autista_somma':float(s['ore_autista_somma']),'ore_completamento':float(s['ore_completamento']),'minuti_completamento':float(s['ore_completamento']*60),
                'minuti_percorrenza':float(s['km']/dec(inst['parametri_operativi']['velocita_media_km_h'])*60),
                'noleggio_euro':float(cent(s['componenti']['noleggio'])),'chilometrico_euro':float(cent(s['componenti']['chilometrico'])),
                'autisti_euro':float(cent(s['componenti']['autisti'])),'totale_euro':float(cent(s['totale'])),
                'totale_preciso_euro':str(s['totale']),'noleggio_euro_veicolo_giorno':float(s['noleggio_veicolo']),'tariffa_euro_km':float(s['costo_km']),'tariffa_euro_ora':float(s['costo_ora'])}
    payload={'studente':'Simone Efrem Ferrara','matricola':'0312300147','impresa':inst['azienda']['denominazione'],
             'modello':'C = n × F + c_km × km totali + c_h × somma ore-autista',
             'scenario_A':serial_scenario(a),'scenario_B':serial_scenario(b),
             'confronto':{'differenza_B_meno_A_euro':float(cent(margin)),'differenza_B_meno_A_precisa_euro':str(margin),
                          'differenza_km_B_meno_A':float(b['km']-a['km']),'risparmio_minuti_completamento_B':float(saved*60),
                          'sovraccosto_B_per_minuto_risparmiato':float(cent(margin/(saved*60)))},
             'soglie':{'costo_km_A_pareggio_euro_km':str(crossover_A),'noleggio_B_pareggio_euro_veicolo_giorno':str(crossover_rent_B),
                      'noleggio_A_pareggio_euro_giorno':str(crossover_rent_A)},
             'variabili_sensibilita':{'costo_km_A':'0,40-1,80 €/km a incrementi di 0,05','noleggio_B':'35-75 €/veicolo/giorno a incrementi di 1',
                                     'altre_voci':'ferme ai valori base'},
             'nota':'Distanze da itinerari stradali tra centri urbani come documentate nella Fase 1; costi e parametri operativi sono ipotesi aziendali del caso. IVA esclusa.'}
    (out/'analisi_economica.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows=[{'indicatore':k,'scenario_A':fmt(va),'scenario_B':fmt(vb)} for k,va,vb in [
        ('Noleggio EUR',a['componenti']['noleggio'],b['componenti']['noleggio']),
        ('Costo chilometrico EUR',a['componenti']['chilometrico'],b['componenti']['chilometrico']),
        ('Costo autisti EUR',a['componenti']['autisti'],b['componenti']['autisti']),
        ('Costo totale EUR',a['totale'],b['totale']),('Km percorsi',a['km'],b['km']),
        ('Ore autista sommate',a['ore_autista_somma'],b['ore_autista_somma']),
        ('Ore di completamento',a['ore_completamento'],b['ore_completamento'])]]
    csv_write(out/'costi_scenari.csv',['indicatore','scenario_A','scenario_B'],rows)
    csv_write(out/'sensibilita_costo_km_A.csv',list(sensitivity_A[0]),sensitivity_A)
    csv_write(out/'sensibilita_noleggio_B.csv',list(sensitivity_B[0]),sensitivity_B)
    csv_write(out/'sensibilita_combinata.csv',list(combos[0]),combos)
    # Vettoriali SVG riproducibili senza dipendenze esterne.
    def svg_graph(filename,points,x_name,y_name,labels,vertical=None):
        width,height=940,470;left,right,top,bottom=90,32,45,83
        w=width-left-right;h=height-top-bottom
        xs=[float(p[0]) for p in points];ys=[float(x) for p in points for x in p[1:]]
        xmin,xmax=min(xs),max(xs);ymin=min(ys)-8;ymax=max(ys)+8
        px=lambda x:left+(x-xmin)/(xmax-xmin)*w
        py=lambda y:top+(ymax-y)/(ymax-ymin)*h
        esc=lambda s:str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        pieces=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(filename)}">','<rect width="940" height="470" fill="white"/>']
        for i in range(6):
            y=ymin+(ymax-ymin)*i/5
            pieces.append(f'<line x1="{left}" y1="{py(y):.1f}" x2="{width-right}" y2="{py(y):.1f}" stroke="#e1e7ec" stroke-width="1"/>')
            pieces.append(f'<text x="{left-12}" y="{py(y)+4:.1f}" font-size="12" text-anchor="end" fill="#344054">{y:.0f}</text>')
        for i in range(6):
            x=xmin+(xmax-xmin)*i/5
            pieces.append(f'<text x="{px(x):.1f}" y="{height-bottom+23}" text-anchor="middle" font-size="12" fill="#344054">{x:.2f}</text>')
        for series,color in enumerate(['#087e8b','#c76233']):
            coords=' '.join(f'{px(float(p[0])):.1f},{py(float(p[1+series])):.1f}' for p in points)
            pieces.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="3.5" stroke-linejoin="round"/>')
            pieces.append(f'<rect x="{580+series*175}" y="18" width="12" height="12" fill="{color}"/><text x="{598+series*175}" y="29" font-size="14" fill="#182c40">{esc(labels[series])}</text>')
        if vertical is not None:
            x=float(vertical)
            pieces.append(f'<line x1="{px(x):.1f}" y1="{top}" x2="{px(x):.1f}" y2="{height-bottom}" stroke="#48576b" stroke-width="1.5" stroke-dasharray="7 5"/>')
            pieces.append(f'<text x="{px(x)+7:.1f}" y="{top+18}" font-size="12" fill="#344054">Pareggio: {x:.3f}</text>')
        pieces.append(f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-size="15" fill="#182c40">{esc(x_name)}</text>')
        pieces.append(f'<text transform="translate(24 {height/2}) rotate(-90)" text-anchor="middle" font-size="15" fill="#182c40">{esc(y_name)}</text>')
        pieces.append('</svg>')
        (out/'grafici'/filename).write_text('\n'.join(pieces),encoding='utf-8')
    svg_graph('sensibilita_costo_km_A.svg',[(x, total_cost(a['veicoli'],a['noleggio_veicolo'],x,a['km'],a['costo_ora'],a['ore_autista_somma']),b['totale']) for x in values_A],
              'Costo km furgone A (EUR/km)','Costo giornaliero (EUR)',('A - un furgone','B - due furgoni'),crossover_A)
    svg_graph('sensibilita_noleggio_B.svg',[(x, a['totale'],total_cost(b['veicoli'],x,b['costo_km'],b['km'],b['costo_ora'],b['ore_autista_somma'])) for x in rent_values_B],
              'Noleggio furgone B (EUR/mezzo/giorno)','Costo giornaliero (EUR)',('A - un furgone','B - due furgoni'),crossover_rent_B)
    return inst,routes,a,b,payload,values_A,rent_values_B,combos

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Analisi economica dei percorsi di PaneLinea Nord Milano')
    parser.add_argument('--base',type=Path,default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output',type=Path,default=None)
    args=parser.parse_args()
    out=args.output or args.base/'risultati'
    inst,routes,a,b,payload,*_ =build(args.base,out)
    print('Scenario A: %.2f EUR / %.1f km'%(cent(a['totale']),a['km']))
    print('Scenario B: %.2f EUR / %.1f km'%(cent(b['totale']),b['km']))
    print('Differenza B-A: %.2f EUR'%cent(b['totale']-a['totale']))
    print('Pareggio costo chilometrico A: %.6f EUR/km'%dec(payload['soglie']['costo_km_A_pareggio_euro_km']))
    print('Pareggio noleggio per veicolo B: %.6f EUR/giorno'%dec(payload['soglie']['noleggio_B_pareggio_euro_veicolo_giorno']))
