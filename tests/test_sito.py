"""Test di coerenza e integrità del sito PaneLinea Nord Milano."""
from __future__ import annotations
import csv
import json
import math
from pathlib import Path
from unittest import TestCase

ROOT=Path(__file__).resolve().parents[1]
WEB=ROOT/'web'
DOCS=ROOT/'docs'


def read_json(name):
    return json.loads((WEB/'dati'/name).read_text(encoding='utf-8'))


class TestContenuto(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inst=read_json('istanza_ferrara.json')
        cls.sol=read_json('soluzioni_ottime.json')
        cls.eco=read_json('analisi_economica.json')
        cls.nodes={n['id']:n for n in cls.inst['nodi']}
        cls.order=cls.inst['ordine_nodi']
        cls.matrix=cls.inst['matrice_distanze_km']

    def route_km(self, nodes):
        return sum(self.matrix[self.order.index(a)][self.order.index(b)] for a,b in zip(nodes,nodes[1:]))

    def test_identita(self):
        self.assertEqual(self.inst['studente']['nome'],'Simone Efrem')
        self.assertEqual(self.inst['studente']['cognome'],'Ferrara')
        self.assertEqual(self.inst['studente']['matricola'],'0312300147')

    def test_comune_deposito(self):
        self.assertEqual(self.nodes['D0']['comune'],'Sesto San Giovanni')

    def test_cinque_clienti(self):
        self.assertEqual(len(self.inst['nodi']),6)
        self.assertEqual(len([n for n in self.inst['nodi'] if n['id']!='D0']),5)

    def test_domanda(self):
        self.assertEqual(sum(n['kg'] for n in self.inst['nodi']),780)

    def test_matrice_completa(self):
        self.assertEqual(len(self.matrix),6)
        self.assertTrue(all(len(row)==6 for row in self.matrix))
        self.assertTrue(all(x>0 for i,row in enumerate(self.matrix) for j,x in enumerate(row) if i!=j))
        self.assertTrue(all(self.matrix[i][i]==0 for i in range(6)))

    def test_matrice_direzionale(self):
        self.assertNotEqual(self.matrix[0][1],self.matrix[1][0])
        self.assertNotEqual(self.matrix[0][4],self.matrix[4][0])

    def test_30_fonti(self):
        with (WEB/'dati/fonti_distanze_direzionali.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),30)

    def test_combinazioni(self):
        e=self.sol['enumerazione']
        self.assertEqual(e['permutazioni_valutate_scenario_A'],120)
        self.assertEqual(e['partizioni_non_vuote_non_equivalenti_scenario_B'],15)
        self.assertEqual(e['partizioni_ammissibili_scenario_B'],4)
        self.assertEqual(e['coppie_di_rotte_valutate_scenario_B'],48)

    def test_giro_unico(self):
        r=self.sol['scenario_A']['percorsi'][0]
        self.assertEqual(r['nodi'],['D0','C3','C4','C5','C1','C2','D0'])
        self.assertAlmostEqual(self.route_km(r['nodi']),31.0)
        self.assertAlmostEqual(r['km'],31)
        self.assertLessEqual(r['kg_consegnati'],900)

    def test_giri_doppi(self):
        rr=self.sol['scenario_B']['percorsi']
        self.assertEqual(len(rr),2)
        self.assertAlmostEqual(sum(r['km'] for r in rr),40.8)
        for r in rr:
            self.assertAlmostEqual(self.route_km(r['nodi']),r['km'])
            self.assertLessEqual(r['kg_consegnati'],450)
            self.assertEqual(r['nodi'][0],'D0')
            self.assertEqual(r['nodi'][-1],'D0')

    def test_ogni_cliente_una_volta(self):
        all_clients=[]
        for r in self.sol['scenario_B']['percorsi']:
            all_clients.extend(r['nodi'][1:-1])
        self.assertEqual(sorted(all_clients),['C1','C2','C3','C4','C5'])

    def test_tempi_A(self):
        expected=31/26 + 5*12/60 + 20/60
        self.assertAlmostEqual(self.eco['scenario_A']['ore_autista_somma'],expected)

    def test_tempi_B(self):
        expected=40.8/26 + 5*12/60 + 2*20/60
        self.assertAlmostEqual(self.eco['scenario_B']['ore_autista_somma'],expected)

    def test_costi_A(self):
        a=self.eco['scenario_A']
        expected=105+31*.69+a['ore_autista_somma']*18.4
        self.assertAlmostEqual(float(a['totale_preciso_euro']),expected)
        self.assertEqual(round(expected,2),172.86)

    def test_costi_B(self):
        b=self.eco['scenario_B']
        expected=2*58+40.8*.52+b['ore_autista_somma']*18.4
        self.assertAlmostEqual(float(b['totale_preciso_euro']),expected)
        self.assertEqual(round(expected,2),196.76)

    def test_soglia_kmA(self):
        a=self.eco['scenario_A'];b=self.eco['scenario_B']
        price=(float(b['totale_preciso_euro'])-105-a['ore_autista_somma']*18.4)/31
        self.assertAlmostEqual(price,1.46079735318,places=8)
        self.assertAlmostEqual(price,float(self.eco['soglie']['costo_km_A_pareggio_euro_km']),places=8)

    def test_soglia_rentB(self):
        a=self.eco['scenario_A'];b=self.eco['scenario_B']
        price=(float(a['totale_preciso_euro'])-40.8*.52-b['ore_autista_somma']*18.4)/2
        self.assertAlmostEqual(price,46.05264102564,places=8)
        self.assertAlmostEqual(price,float(self.eco['soglie']['noleggio_B_pareggio_euro_veicolo_giorno']),places=8)

    def test_durata_parallelismo(self):
        t=[r['minuti_impegnati'] for r in self.sol['scenario_B']['percorsi']]
        self.assertAlmostEqual(max(t),104.46,places=2)
        self.assertLess(max(t),self.sol['scenario_A']['percorsi'][0]['minuti_impegnati'])

    def test_dati_embedded(self):
        js=(WEB/'assets/project-data.js').read_text(encoding='utf-8')
        self.assertIn('window.PANELINEA_DATA = ',js)
        payload=json.loads(js.partition('window.PANELINEA_DATA = ')[2].rstrip(' \n;'))
        self.assertEqual(payload['istanza'],self.inst)
        self.assertEqual(payload['soluzioni'],self.sol)
        self.assertEqual(payload['economia'],self.eco)

    def test_sito_offline(self):
        html=(WEB/'index.html').read_text(encoding='utf-8')
        self.assertIn('assets/project-data.js',html)
        self.assertIn('assets/app.js',html)
        self.assertNotIn('https://cdn.',html)
        self.assertNotIn('http://',html)

    def test_link_download(self):
        for name in ['istanza_ferrara.json','soluzioni_ottime.json','analisi_economica.json','fonti_distanze_direzionali.csv','matrice_distanze_direzionale_km.csv']:
            self.assertTrue((WEB/'dati'/name).is_file())
            self.assertIn('dati/'+name,(WEB/'index.html').read_text(encoding='utf-8'))

    def test_svg(self):
        for n in ('a','b'):
            p=WEB/'assets'/f'grafo-{n}.svg'
            self.assertTrue(p.exists())
            self.assertIn('<svg',p.read_text())

    def test_sito_duplicato_per_pages(self):
        files=[p.relative_to(WEB) for p in WEB.rglob('*') if p.is_file()]
        self.assertGreaterEqual(len(files),11)
        for rel in files:
            self.assertEqual((WEB/rel).read_bytes(),(DOCS/rel).read_bytes(),str(rel))

    def test_nessuna_contaminazione_dal_progetto_precedente(self):
        forbidden=['inserisci qui il testo','nome da compilare','lorem ipsum','placeholder student']
        for p in WEB.rglob('*'):
            if p.is_file() and p.suffix.lower() in ('.json','.js','.html','.css','.csv'):
                txt=p.read_text(encoding='utf-8').lower()
                self.assertFalse(any(w in txt for w in forbidden),str(p))

    def test_scenari_base_in_html(self):
        text=(WEB/'index.html').read_text(encoding='utf-8')
        for phrase in ('Simone Efrem Ferrara','0312300147','PaneLinea Nord Milano','31 km','40,8 km','780 kg','900 kg','450 kg'):
            self.assertIn(phrase,text)

    def test_ripetibilita_formula(self):
        calcA=105+31*0.69+18.4*(31/26 + 80/60)
        calcB=116+40.8*.52+18.4*(40.8/26 + 100/60)
        self.assertEqual(round(calcA,2),172.86)
        self.assertEqual(round(calcB,2),196.76)
