"""Rigenera i dati incorporati nel sito e sincronizza la cartella docs."""
from __future__ import annotations
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web'
DOCS = ROOT / 'docs'
MAPPING = {
    'istanza':'istanza_ferrara.json',
    'soluzioni':'soluzioni_ottime.json',
    'economia':'analisi_economica.json',
}


def build() -> None:
    payload={key:json.loads((WEB/'dati'/name).read_text(encoding='utf-8')) for key,name in MAPPING.items()}
    assert payload['istanza']['studente']['matricola'] == '0312300147'
    assert payload['soluzioni']['scenario_A']['km_totali'] == 31.0
    assert payload['soluzioni']['scenario_B']['km_totali'] == 40.8
    assert payload['economia']['scenario_A']['totale_euro'] == 172.86
    assert payload['economia']['scenario_B']['totale_euro'] == 196.76
    encoded=json.dumps(payload, ensure_ascii=False, separators=(',',':')).replace('</','<\\/')
    (WEB/'assets'/'project-data.js').write_text('/* Dati generati dai file JSON verificati nelle Fasi 1–3. */\nwindow.PANELINEA_DATA = '+encoded+';\n',encoding='utf-8')
    if DOCS.exists(): shutil.rmtree(DOCS)
    shutil.copytree(WEB,DOCS)
    print('Sito aggiornato: web/ e docs/ sono identici.')

if __name__ == '__main__':build()
