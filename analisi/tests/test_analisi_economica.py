import json
import sys
import unittest
from pathlib import Path
from decimal import Decimal as D
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from analisi_economica import build,check,cent,load,scenario,total_cost

class TestAnalisiEconomica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.i,cls.r=load(ROOT)
        cls.data=build(ROOT,ROOT/'risultati')
        cls.a=cls.data[2];cls.b=cls.data[3]

    def test_01_dati_e_percorsi(self):self.assertTrue(check(self.i,self.r))
    def test_02_dati_indipendenti_da_precedenti(self):
        self.assertEqual(self.r['identificazione']['studente'],'Simone Efrem Ferrara')
        self.assertEqual(self.r['identificazione']['matricola'],'0312300147')
    def test_03_km_scenari(self):
        self.assertEqual(self.a['km'],D('31'))
        self.assertEqual(self.b['km'],D('40.8'))
    def test_04_capacita_e_quantita(self):
        self.assertEqual(sum(n['kg'] for n in self.i['nodi']),780)
        self.assertEqual([x['kg_consegnati'] for x in self.r['scenario_B']['percorsi']],[430,350])
    def test_05_costi_A(self):self.assertEqual(cent(self.a['totale']),D('172.86'))
    def test_06_costi_B(self):self.assertEqual(cent(self.b['totale']),D('196.76'))
    def test_07_costo_autisti_sommato(self):
        self.assertEqual(self.b['ore_autista_somma'],sum(self.b['durate']))
        self.assertGreater(self.b['ore_autista_somma'],self.b['ore_completamento'])
    def test_08_tempo_operativo(self):
        self.assertEqual(self.a['ore_autista_somma'],D(31)/D(26)+D(80)/D(60))
        self.assertEqual(self.b['ore_autista_somma'],D('40.8')/D(26)+D(100)/D(60))
    def test_09_composizione_costi(self):
        self.assertEqual(self.a['componenti']['noleggio'],D(105))
        self.assertEqual(self.a['componenti']['chilometrico'],D('21.39'))
        self.assertEqual(self.b['componenti']['noleggio'],D(116))
        self.assertEqual(self.b['componenti']['chilometrico'],D('21.216'))
    def test_10_differenza_totale(self):self.assertEqual(cent(self.b['totale']-self.a['totale']),D('23.89'))
    def test_11_soglia_km(self):
        x=(self.b['totale']-self.a['componenti']['noleggio']-self.a['componenti']['autisti'])/self.a['km']
        self.assertTrue(abs(total_cost(1,105,x,31,D('18.4'),self.a['ore_autista_somma'])-self.b['totale'])<D('0.0000000000001'))
        self.assertGreater(x,D('1.46'));self.assertLess(x,D('1.47'))
    def test_12_soglia_noleggio_B(self):
        x=(self.a['totale']-self.b['componenti']['chilometrico']-self.b['componenti']['autisti'])/D(2)
        self.assertTrue(abs(total_cost(2,x,D('.52'),D('40.8'),D('18.4'),self.b['ore_autista_somma'])-self.a['totale'])<D('0.0000000000001'))
        self.assertGreater(x,D('46'));self.assertLess(x,D('47'))
    def test_13_sensibilita_monotona(self):
        out=self.data[5]
        costs=[total_cost(1,105,x,31,D('18.4'),self.a['ore_autista_somma']) for x in out]
        self.assertEqual(len(costs),29)
        self.assertTrue(all(a<b for a,b in zip(costs,costs[1:])))
    def test_14_tabella_prezzo_km(self):
        rows=(ROOT/'risultati'/'sensibilita_costo_km_A.csv').read_text(encoding='utf-8-sig').splitlines()
        self.assertEqual(len(rows),30)
    def test_15_tabella_noleggio_B(self):
        rows=(ROOT/'risultati'/'sensibilita_noleggio_B.csv').read_text(encoding='utf-8-sig').splitlines()
        self.assertEqual(len(rows),42)
    def test_16_due_variabili(self):
        combos=self.data[7];self.assertEqual(len(combos),80)
        self.assertTrue(any(x['piu_conveniente']=='A' for x in combos))
        self.assertTrue(any(x['piu_conveniente']=='B' for x in combos))
    def test_17_esempio_prezzi(self):
        x=total_cost(1,105,D('1.60'),31,D('18.4'),self.a['ore_autista_somma'])
        self.assertGreater(x,self.b['totale'])
    def test_18_test_schema_json(self):
        doc=json.loads((ROOT/'risultati'/'analisi_economica.json').read_text(encoding='utf-8'))
        self.assertEqual(doc['scenario_A']['totale_euro'],172.86)
        self.assertEqual(doc['scenario_B']['totale_euro'],196.76)

if __name__=='__main__':unittest.main()
