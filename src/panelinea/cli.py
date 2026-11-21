"""Interfaccia a riga di comando del programma."""

from __future__ import annotations

import argparse
from pathlib import Path

from .instance import carica_istanza,verifica_coerenza_csv
from .search import cerca_esattamente
from .output import esporta


def run(argv: list[str] | None=None) -> int:
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description='Ricerca esatta dei percorsi per PaneLinea Nord Milano')
    parser.add_argument('--istanza',type=Path,default=root/'dati'/'istanza_ferrara.json',help='Percorso JSON della Fase 1')
    parser.add_argument('--output',type=Path,default=root/'risultati',help='Cartella degli output CSV e JSON')
    parser.add_argument('--salta-controllo-csv',action='store_true',help='Usare solo il JSON (per test con dati modificati)')
    args=parser.parse_args(argv)
    inst=carica_istanza(args.istanza)
    if not args.salta_controllo_csv:
        check=verifica_coerenza_csv(inst,args.istanza.parent)
        print(f"Coerenza dati: {check['nodi']} nodi, {check['archi']} archi direzionali, fonti e CSV allineati.")
    results=cerca_esattamente(inst)
    report=esporta(inst,results,args.output)
    for label in ('scenario_A','scenario_B'):
        s=report[label]
        print(f"{label}: {s['km_totali']:.1f} km; {s['costi_base']['totale_euro']:.2f} EUR")
        for g in s['percorsi']:
            print(f"  {' -> '.join(g['comuni'])} | {g['kg_consegnati']} kg | {g['km']:.1f} km")
    print(f"Enumerati: {results.statistiche['permutazioni_valutate_scenario_A']} itinerari A e {results.statistiche['coppie_di_rotte_valutate_scenario_B']} combinazioni B.")
    print('Risultati salvati in:',args.output.resolve())
    return 0
