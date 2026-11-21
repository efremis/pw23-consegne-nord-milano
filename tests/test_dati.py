"""Integrita dei dati di input e delle fonti stradali."""

import copy
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from src.panelinea.instance import carica_istanza, verifica_coerenza_csv

ROOT=Path(__file__).resolve().parents[1]
INSTANCE=ROOT/'dati'/'istanza_ferrara.json'


class TestDati(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.instance=carica_istanza(INSTANCE)

    def test_anagrafica(self):
        raw=self.instance.raw
        self.assertEqual(raw['studente']['nome'],'Simone Efrem')
        self.assertEqual(raw['studente']['cognome'],'Ferrara')
        self.assertEqual(raw['studente']['matricola'],'0312300147')
        self.assertEqual(raw['studente']['residenza_comune'],'Sesto San Giovanni')

    def test_azienda_e_deposito(self):
        self.assertEqual(self.instance.comuni[0],'Sesto San Giovanni')
        self.assertEqual(self.instance.raw['azienda']['denominazione'],'PaneLinea Nord Milano')

    def test_nodi_e_domande(self):
        self.assertEqual(self.instance.ids,('D0','C1','C2','C3','C4','C5'))
        self.assertEqual(self.instance.domande,(0,170,115,145,190,160))
        self.assertEqual(self.instance.domanda_totale,780)

    def test_matrice_direzionale(self):
        self.assertEqual(self.instance.matrice[0][1],6)
        self.assertEqual(self.instance.matrice[1][0],5)
        self.assertNotEqual(self.instance.matrice[0][4],self.instance.matrice[4][0])
        self.assertEqual(self.instance.matrice[2][4],Decimal('12.2'))

    def test_tutte_fonti_e_csv_coerenti(self):
        check=verifica_coerenza_csv(self.instance,ROOT/'dati')
        self.assertEqual(check['archi'],30)
        self.assertTrue(check['csv_json_coerenti'])

    def test_capacita(self):
        self.assertGreaterEqual(self.instance.scenario_a.capacita_kg,self.instance.domanda_totale)
        self.assertLess(self.instance.scenario_b.capacita_kg,self.instance.domanda_totale)
        self.assertGreaterEqual(2*self.instance.scenario_b.capacita_kg,self.instance.domanda_totale)

    def test_scarta_matrice_non_valida(self):
        bad=copy.deepcopy(self.instance.raw)
        bad['matrice_distanze_km'][0][1]=-1
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json'
            p.write_text(json.dumps(bad),encoding='utf-8')
            with self.assertRaises(ValueError):carica_istanza(p)

    def test_scarta_matricola_altrui(self):
        bad=copy.deepcopy(self.instance.raw)
        bad['studente']['matricola']='99999999'
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json'
            p.write_text(json.dumps(bad),encoding='utf-8')
            with self.assertRaises(ValueError):carica_istanza(p)

    def test_scarta_capacita_incoerente(self):
        bad=copy.deepcopy(self.instance.raw)
        bad['scenari_veicoli']['scenario_B']['capacita_kg_per_veicolo']=100
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json'
            p.write_text(json.dumps(bad),encoding='utf-8')
            with self.assertRaises(ValueError):carica_istanza(p)

    def test_scarta_distanze_csv_alterate(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)
            for name in ['matrice_distanze_direzionale_km.csv','fonti_distanze_direzionali.csv']:
                (dest/name).write_bytes((ROOT/'dati'/name).read_bytes())
            file=dest/'matrice_distanze_direzionale_km.csv'
            file.write_text(file.read_text(encoding='utf-8-sig').replace('D0;0;6.0;', 'D0;0;999.0;'),encoding='utf-8')
            with self.assertRaises(ValueError):verifica_coerenza_csv(self.instance,dest)
