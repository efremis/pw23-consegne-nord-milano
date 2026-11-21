"""Verifica esaustivita, ottimalita e vincoli."""

import itertools
import math
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from src.panelinea.instance import carica_istanza
from src.panelinea.search import crea_giro,cerca_esattamente,distanza_giro

ROOT=Path(__file__).resolve().parents[1]


def riferimento_indipendente(instance):
    """Ricerca indipendente con assegnazioni etichettate di due mezzi."""
    clients=instance.clienti
    def d(seq):
        p=(0,*seq,0)
        return sum((instance.matrice[a][b] for a,b in zip(p,p[1:])),Decimal(0))
    best_a=min(d(perm) for perm in itertools.permutations(clients))
    feasible=[]
    for bits in itertools.product((0,1),repeat=len(clients)):
        g1=tuple(i for i,side in zip(clients,bits) if side==0)
        g2=tuple(i for i,side in zip(clients,bits) if side==1)
        if not g1 or not g2:continue
        if sum(instance.domande[i] for i in g1)>instance.scenario_b.capacita_kg:continue
        if sum(instance.domande[i] for i in g2)>instance.scenario_b.capacita_kg:continue
        for p1 in itertools.permutations(g1):
            for p2 in itertools.permutations(g2):
                feasible.append(d(p1)+d(p2))
    return best_a,min(feasible),len(feasible)


class TestRicerca(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance=carica_istanza(ROOT/'dati'/'istanza_ferrara.json')
        cls.r=cerca_esattamente(cls.instance)

    def test_completa_un_veicolo(self):
        self.assertEqual(len(self.r.permutazioni_a),120)
        self.assertEqual(len(set(x['percorso'] for x in self.r.permutazioni_a)),120)
        self.assertEqual(self.r.statistiche['permutazioni_valutate_scenario_A'],math.factorial(5))

    def test_partizioni_due_veicoli(self):
        self.assertEqual(len(self.r.partizioni),15)
        self.assertEqual(sum(x['ammissibile'] for x in self.r.partizioni),4)
        self.assertEqual(len(self.r.permutazioni_b),48)

    def test_scenario_a_ottimo(self):
        g=self.r.migliore_a
        self.assertEqual(g.km,Decimal('31.0'))
        self.assertEqual(g.kg,780)
        self.assertEqual(g.nodi,(0,3,4,5,1,2,0))

    def test_scenario_b_ottimo(self):
        a,b=self.r.migliore_b
        self.assertEqual(a.km+b.km,Decimal('40.8'))
        self.assertEqual(a.kg,430)
        self.assertEqual(b.kg,350)
        self.assertEqual(a.nodi,(0,2,1,3,0))
        self.assertEqual(b.nodi,(0,4,5,0))

    def test_riferimento_indipendente(self):
        a,b,n=riferimento_indipendente(self.instance)
        self.assertEqual(a,self.r.migliore_a.km)
        self.assertEqual(b,sum((g.km for g in self.r.migliore_b),Decimal(0)))
        self.assertEqual(n,96) # mezzo A/B etichettati: ogni sequenza contata due volte

    def test_nessun_cliente_mancante_duplicato(self):
        r=self.r
        self.assertEqual(set(r.migliore_a.clienti),set(self.instance.clienti))
        a,b=r.migliore_b
        self.assertEqual(set(a.clienti)|set(b.clienti),set(self.instance.clienti))
        self.assertFalse(set(a.clienti)&set(b.clienti))

    def test_matrice_non_simmetrica(self):
        self.assertEqual(distanza_giro(self.instance,(1,)),Decimal('11.0'))
        self.assertEqual(distanza_giro(self.instance,(4,)),Decimal('15.3'))

    def test_rifiuta_rotte_duplicate_e_vuote(self):
        with self.assertRaises(ValueError):crea_giro(self.instance,())
        with self.assertRaises(ValueError):crea_giro(self.instance,(1,1))
        with self.assertRaises(ValueError):crea_giro(self.instance,(10,))

    def test_tempo_corrisponde_distanza_e_scarico(self):
        a=self.r.migliore_a
        expected=a.km/self.instance.velocita_kmh + Decimal(80)/60
        self.assertEqual(a.durata_ore,expected)

    def test_determinismo(self):
        r2=cerca_esattamente(self.instance)
        self.assertEqual(self.r.migliore_a,r2.migliore_a)
        self.assertEqual(self.r.migliore_b,r2.migliore_b)
