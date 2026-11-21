"""Enumerazione esaustiva delle rotte per uno e due veicoli."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from itertools import permutations, combinations, product
from math import factorial

from .instance import Instance


@dataclass(frozen=True)
class Giro:
    clienti: tuple[int,...]
    kg: int
    km: Decimal
    durata_ore: Decimal

    @property
    def nodi(self) -> tuple[int,...]:
        return (0,*self.clienti,0)


@dataclass(frozen=True)
class Ricerca:
    giria: tuple[Giro,...]
    girib: tuple[Giro,...]
    migliore_a: Giro
    migliore_b: tuple[Giro,Giro]
    partizioni: tuple[dict,...]
    permutazioni_a: tuple[dict,...]
    permutazioni_b: tuple[dict,...]
    statistiche: dict


def distanza_giro(instance: Instance, clienti: tuple[int,...]) -> Decimal:
    nodi=(0,*clienti,0)
    return sum((instance.matrice[a][b] for a,b in zip(nodi,nodi[1:])),Decimal('0'))


def crea_giro(instance: Instance, clienti: tuple[int,...]) -> Giro:
    if not clienti:
        raise ValueError('Non sono consentiti veicoli inutilizzati')
    if len(clienti)!=len(set(clienti)) or not set(clienti).issubset(set(instance.clienti)):
        raise ValueError('Clienti duplicati oppure non validi')
    kg=sum(instance.domande[i] for i in clienti)
    km=distanza_giro(instance,clienti)
    ore=(km/instance.velocita_kmh + Decimal(len(clienti)*instance.minuti_scarico+instance.minuti_carico)/60)
    return Giro(clienti,kg,km,ore)


def _chiave_ordinamento(giro: Giro) -> tuple:
    return (giro.km,giro.clienti)


def _row_a(instance: Instance,g: Giro) -> dict:
    return {'percorso': ' -> '.join(instance.ids[i] for i in g.nodi),'km':float(g.km),'kg':g.kg,'ore':round(float(g.durata_ore),5)}


def _row_b(instance: Instance,a:Giro,b:Giro) -> dict:
    return {'mezzo_1':' -> '.join(instance.ids[i] for i in a.nodi),
            'mezzo_2':' -> '.join(instance.ids[i] for i in b.nodi),
            'km_mezzo_1':float(a.km),'km_mezzo_2':float(b.km),
            'km_totali':float(a.km+b.km),'kg_mezzo_1':a.kg,'kg_mezzo_2':b.kg,
            'ore_1':round(float(a.durata_ore),5),'ore_2':round(float(b.durata_ore),5)}


def cerca_esattamente(instance: Instance) -> Ricerca:
    """Esamina ogni permutazione ammissibile senza euristiche o solutori."""
    cs=instance.clienti
    # Un veicolo: tutte le 5! permutazioni, con ritorno al deposito.
    one=[crea_giro(instance,p) for p in permutations(cs)]
    if not one or any(g.kg>instance.scenario_a.capacita_kg for g in one):
        raise ValueError('Scenario A non ammissibile')
    best_a=min(one,key=_chiave_ordinamento)
    
    # Due furgoni identici: C1 viene assegnato sempre al mezzo 1.
    # Eliminare lo scambio (mezzo 1, mezzo 2) dimezza soltanto duplicati.
    # Ogni partizione ammissibile viene enumerata in tutte le permutazioni
    # di entrambi i giri, non soltanto nel giro localmente migliore.
    two=[]
    partitions=[]
    count_all=0
    count_ok=0
    total= sum(instance.domande[i] for i in cs)
    for k in range(1,len(cs)):
        for extra in combinations(cs[1:],k-1):
            group_a=(cs[0],*extra)
            group_b=tuple(i for i in cs if i not in group_a)
            kg_a=sum(instance.domande[i] for i in group_a)
            kg_b=total-kg_a
            count_all+=1
            feasible=(kg_a<=instance.scenario_b.capacita_kg and kg_b<=instance.scenario_b.capacita_kg)
            partitions.append({'clienti_mezzo_1':','.join(instance.ids[i] for i in group_a),
                               'clienti_mezzo_2':','.join(instance.ids[i] for i in group_b),
                               'kg_1':kg_a,'kg_2':kg_b,'ammissibile':feasible,
                               'motivo':'OK' if feasible else 'Capacita superata'})
            if not feasible:
                continue
            count_ok+=1
            seq_a=[crea_giro(instance,p) for p in permutations(group_a)]
            seq_b=[crea_giro(instance,p) for p in permutations(group_b)]
            for a,b in product(seq_a,seq_b):
                two.append((a,b))
    if not two:
        raise ValueError('Nessuna partizione ammissibile per lo scenario B')
    best_b=min(two,key=lambda item: (item[0].km+item[1].km,item[0].clienti,item[1].clienti))
    # Controlli invarianti sui risultati trovati.
    if (set(best_b[0].clienti) | set(best_b[1].clienti))!=set(cs) or (set(best_b[0].clienti) & set(best_b[1].clienti)):
        raise AssertionError('Clienti mancanti o duplicati nel risultato B')
    if best_b[0].kg>instance.scenario_b.capacita_kg or best_b[1].kg>instance.scenario_b.capacita_kg:
        raise AssertionError('Capacita violata nel risultato B')
    if len(one)!=factorial(len(cs)):
        raise AssertionError('Permutazioni scenario A incomplete')
    stats={
        'numero_clienti':len(cs),
        'permutazioni_valutate_scenario_A':len(one),
        'partizioni_non_vuote_non_equivalenti_scenario_B':count_all,
        'partizioni_ammissibili_scenario_B':count_ok,
        'coppie_di_rotte_valutate_scenario_B':len(two),
        'duplicazioni_per_scambio_veicoli_eliminate':True,
        'criterio': 'minimizzazione della distanza stradale complessiva su matrice direzionale',
        'tie_break': 'ordinamento lessicografico degli ID dei clienti a pari distanza',
    }
    return Ricerca(tuple(one),tuple(g for pair in two for g in pair),best_a,best_b,tuple(partitions),
                   tuple(_row_a(instance,x) for x in one),
                   tuple(_row_b(instance,*x) for x in two), stats)
