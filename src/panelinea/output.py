"""Esportazione dei percorsi, dei confronti operativi e dei costi base."""

from __future__ import annotations

import csv
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from .instance import Instance
from .search import Giro,Ricerca
from .diagrammi import crea_diagrammi


def _f(v: Decimal, posizioni: int=4) -> float:
    scale=Decimal('1').scaleb(-posizioni)
    return float(v.quantize(scale,rounding=ROUND_HALF_UP))


def _eur(v: Decimal) -> float:
    return _f(v,2)


def _descr_giro(inst: Instance, g: Giro) -> dict:
    return {
        'nodi': [inst.ids[i] for i in g.nodi],
        'comuni': [inst.nome(i) for i in g.nodi],
        'numero_clienti':len(g.clienti),
        'kg_consegnati':g.kg,
        'km':_f(g.km,2),
        'ore_impegnate_inclusi_carico_e_scarico':_f(g.durata_ore,5),
        'minuti_impegnati':_f(g.durata_ore*60,2),
    }


def _costi(inst:Instance,km:Decimal,ore:Decimal,numero_mezzi:int, s) -> dict:
    noleggio=s.noleggio_giornaliero*numero_mezzi
    chilometri=s.costo_km*km
    autisti=s.costo_ora*ore
    return {'noleggio_euro':_eur(noleggio),
            'chilometrico_euro':_eur(chilometri),
            'autisti_euro':_eur(autisti),
            'totale_euro':_eur(noleggio+chilometri+autisti),
            'totale_non_arrotondato_euro':str(noleggio+chilometri+autisti),
            'formula':'noleggio per veicolo x numero veicoli + costo/km x km totali + costo/h x ore-autista sommate'}


def riepilogo(inst:Instance,res:Ricerca) -> dict:
    a=res.migliore_a
    b1,b2=res.migliore_b
    kmb=b1.km+b2.km
    ore_b=b1.durata_ore+b2.durata_ore
    completion=max(b1.durata_ore,b2.durata_ore)
    return {
      'identificazione':{'studente':'Simone Efrem Ferrara','matricola':'0312300147',
                          'impresa':inst.raw['azienda']['denominazione'],
                          'deposito':inst.comuni[0],
                          'clienti':[{ 'id':inst.ids[i],'comune':inst.comuni[i],'domanda_kg':inst.domande[i]} for i in inst.clienti],
                          'domanda_totale_kg':inst.domanda_totale},
      'obiettivo':'distanza stradale complessiva minima (matrice direzionale Fase 1)',
      'origine_dati':'dati/istanza_ferrara.json; fonti per i 30 archi in dati/fonti_distanze_direzionali.csv',
      'parametri_operativi':inst.raw['parametri_operativi'],
      'scenario_A':{
          'veicoli':inst.scenario_a.veicoli,'capacita_per_veicolo_kg':inst.scenario_a.capacita_kg,
          'percorsi':[_descr_giro(inst,a)],'km_totali':_f(a.km,2),
          'ore_autista_somma':_f(a.durata_ore,5),
          'ore_fino_ultima_consegna_e_rientro':_f(a.durata_ore,5),
          'costi_base':_costi(inst,a.km,a.durata_ore,1,inst.scenario_a)},
      'scenario_B':{
          'veicoli':inst.scenario_b.veicoli,'capacita_per_veicolo_kg':inst.scenario_b.capacita_kg,
          'percorsi':[_descr_giro(inst,b1),_descr_giro(inst,b2)],
          'km_totali':_f(kmb,2),'ore_autista_somma':_f(ore_b,5),
          'ore_fino_ultima_consegna_e_rientro':_f(completion,5),
          'costi_base':_costi(inst,kmb,ore_b,2,inst.scenario_b)},
      'confronto':{
          'differenza_km_B_meno_A':_f(kmb-a.km,2),
          'differenza_costo_B_meno_A_euro':_eur((inst.scenario_b.noleggio_giornaliero*2+inst.scenario_b.costo_km*kmb+inst.scenario_b.costo_ora*ore_b)-(inst.scenario_a.noleggio_giornaliero+inst.scenario_a.costo_km*a.km+inst.scenario_a.costo_ora*a.durata_ore)),
          'risparmio_ore_makespan_B_vs_A':_f(a.durata_ore-completion,5),
          'nota':'Ore-autista sommate per il costo; tempo del giro piu lungo per la fine delle operazioni con due furgoni in parallelo.'},
      'enumerazione':res.statistiche,
      'precisazione':'Distanze stradali tra centri urbani prese dalle fonti documentate della Fase 1; parametri economici e operativi riferiti al caso aziendale simulato.',
    }


def _csv(path:Path,rows:list[dict]|tuple[dict,...]) -> None:
    if not rows:return
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()),delimiter=';')
        writer.writeheader();writer.writerows(rows)


def esporta(inst:Instance,res:Ricerca,dest:Path) -> dict:
    dest.mkdir(parents=True,exist_ok=True)
    report=riepilogo(inst,res)
    (dest/'soluzioni_ottime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    _csv(dest/'permutazioni_scenario_A.csv',res.permutazioni_a)
    _csv(dest/'combinazioni_scenario_B.csv',res.permutazioni_b)
    _csv(dest/'partizioni_scenario_B.csv',res.partizioni)
    crea_diagrammi(inst,res,dest)
    a,b=report['scenario_A'],report['scenario_B']
    lines=[
        '# Percorsi ottimi - PaneLinea Nord Milano',
        '',
        '**Studente:** Simone Efrem Ferrara - Matricola 0312300147',
        '',
        f"**Deposito:** {inst.comuni[0]} | **Consegne:** {inst.domanda_totale} kg a cinque clienti",
        '',
        '## Scenario A - un furgone da 900 kg',
        '',
        f"Percorso: {' -> '.join(a['percorsi'][0]['comuni'])}",
        '',
        f"Distanza: **{a['km_totali']:.1f} km** | Carico: **{a['percorsi'][0]['kg_consegnati']} kg** | Costo base: **{a['costi_base']['totale_euro']:.2f} EUR**",
        '',
        '## Scenario B - due furgoni da 450 kg',
        '',
    ]
    for i,g in enumerate(b['percorsi'],start=1):
        lines.extend([f"Mezzo {i}: {' -> '.join(g['comuni'])}",
                      f"Km: {g['km']:.1f} | Carico: {g['kg_consegnati']} kg",''])
    lines.extend([f"Distanza complessiva: **{b['km_totali']:.1f} km** | Costo base: **{b['costi_base']['totale_euro']:.2f} EUR**",'',
                  f"Enumerazione: {res.statistiche['permutazioni_valutate_scenario_A']} percorsi A; {res.statistiche['partizioni_ammissibili_scenario_B']} partizioni B ammissibili e {res.statistiche['coppie_di_rotte_valutate_scenario_B']} coppie di rotte B.",'',
                  "Le distanze derivano dalla matrice direzionale documentata della Fase 1. I costi sono quelli dell'istanza aziendale e saranno approfonditi nella Fase 3."])
    (dest/'RIEPILOGO.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return report
