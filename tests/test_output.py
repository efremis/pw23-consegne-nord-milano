"""Verifiche sugli output e sull'avvio del programma."""

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.panelinea.instance import carica_istanza
from src.panelinea.search import cerca_esattamente
from src.panelinea.output import esporta

ROOT=Path(__file__).resolve().parents[1]


class TestOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance=carica_istanza(ROOT/'dati'/'istanza_ferrara.json')
        cls.r=cerca_esattamente(cls.instance)

    def test_risultati_e_costi_base(self):
        with tempfile.TemporaryDirectory() as d:
            report=esporta(self.instance,self.r,Path(d))
            self.assertEqual(report['scenario_A']['km_totali'],31.0)
            self.assertEqual(report['scenario_B']['km_totali'],40.8)
            self.assertEqual(report['scenario_A']['costi_base']['totale_euro'],172.86)
            self.assertEqual(report['scenario_B']['costi_base']['totale_euro'],196.76)
            self.assertGreater(report['scenario_B']['ore_autista_somma'],report['scenario_B']['ore_fino_ultima_consegna_e_rientro'])
            self.assertEqual(report['identificazione']['matricola'],'0312300147')

    def test_tutti_csv_e_json_presenti(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)
            esporta(self.instance,self.r,dst)
            for name,expected in [('permutazioni_scenario_A.csv',120),('combinazioni_scenario_B.csv',48),('partizioni_scenario_B.csv',15)]:
                with (dst/name).open(encoding='utf-8-sig',newline='') as f:
                    self.assertEqual(len(list(csv.DictReader(f,delimiter=';'))),expected)
            report=json.loads((dst/'soluzioni_ottime.json').read_text(encoding='utf-8'))
            self.assertEqual(report['scenario_B']['percorsi'][0]['kg_consegnati']+report['scenario_B']['percorsi'][1]['kg_consegnati'],780)

    def test_cli_fuori_dalla_cartella_progetto(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'ris'
            r=subprocess.run([sys.executable,str(ROOT/'main.py'),'--output',str(out)],cwd=d,text=True,capture_output=True)
            self.assertEqual(r.returncode,0,msg=r.stdout+'\n'+r.stderr)
            self.assertIn('30 archi direzionali',r.stdout)
            self.assertTrue((out/'soluzioni_ottime.json').exists())

    def test_grafi_svg_generati(self):
        with tempfile.TemporaryDirectory() as d:
            dst=Path(d)
            esporta(self.instance,self.r,dst)
            for name in ('Grafo_percorso_A.svg','Grafo_percorsi_B.svg'):
                svg=(dst/name).read_text(encoding='utf-8')
                self.assertTrue(svg.startswith('<svg'))
                self.assertIn('Sesto',svg)
                self.assertNotIn('Z9',svg)

    def test_ogni_mezzo_rientra_al_deposito(self):
        with tempfile.TemporaryDirectory() as d:
            report=esporta(self.instance,self.r,Path(d))
            for key in ('scenario_A','scenario_B'):
                for route in report[key]['percorsi']:
                    self.assertEqual(route['nodi'][0],'D0')
                    self.assertEqual(route['nodi'][-1],'D0')

    def test_costo_scenario_a_ricalcolato(self):
        g=self.r.migliore_a
        s=self.instance.scenario_a
        total=s.noleggio_giornaliero+s.costo_km*g.km+s.costo_ora*g.durata_ore
        self.assertTrue(Decimal('172.85')<total<Decimal('172.87'))

    def test_ore_veicoli_paralleli(self):
        a,b=self.r.migliore_b
        self.assertGreater(a.durata_ore,0)
        self.assertGreater(b.durata_ore,0)
        self.assertLess(max(a.durata_ore,b.durata_ore),a.durata_ore+b.durata_ore)
