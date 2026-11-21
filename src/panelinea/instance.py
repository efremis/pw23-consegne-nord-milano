"""Lettura e validazione dell'istanza stradale della Fase 1."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


def dec(value: object) -> Decimal:
    """Converte un valore di input in Decimal senza passare da float."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Valore numerico non valido: {value!r}") from exc
    if not d.is_finite():
        raise ValueError(f"Valore numerico non finito: {value!r}")
    return d


@dataclass(frozen=True)
class Scenario:
    nome: str
    veicoli: int
    capacita_kg: int
    noleggio_giornaliero: Decimal
    costo_km: Decimal
    costo_ora: Decimal


@dataclass(frozen=True)
class Instance:
    raw: dict
    path: Path
    ids: tuple[str, ...]
    comuni: tuple[str, ...]
    domande: tuple[int, ...]
    matrice: tuple[tuple[Decimal, ...], ...]
    scenario_a: Scenario
    scenario_b: Scenario
    velocita_kmh: Decimal
    minuti_scarico: int
    minuti_carico: int

    @property
    def clienti(self) -> tuple[int, ...]:
        return tuple(range(1, len(self.ids)))

    @property
    def domanda_totale(self) -> int:
        return sum(self.domande[1:])

    def nome(self, indice: int) -> str:
        return self.comuni[indice]


def _positivo(d: Decimal, nome: str, *, zero: bool = False) -> None:
    if (d < 0 and zero) or (d <= 0 and not zero):
        raise ValueError(f"{nome} non valido: {d}")


def _scenario(obj: dict, nome: str) -> Scenario:
    s = Scenario(
        nome=nome,
        veicoli=int(obj['numero_veicoli']),
        capacita_kg=int(obj['capacita_kg_per_veicolo']),
        noleggio_giornaliero=dec(obj['noleggio_euro_giorno_per_veicolo']),
        costo_km=dec(obj['costo_euro_km']),
        costo_ora=dec(obj['costo_autista_euro_ora']),
    )
    if s.veicoli < 1 or s.capacita_kg < 1:
        raise ValueError(f"Scenario {nome}: numero/capacita veicoli non valido")
    for k, v in [('noleggio',s.noleggio_giornaliero),('costo/km',s.costo_km),('costo/h',s.costo_ora)]:
        _positivo(v,f"{nome} - {k}",zero=True)
    return s


def carica_istanza(percorso: str | Path) -> Instance:
    path = Path(percorso).resolve()
    raw = json.loads(path.read_text(encoding='utf-8'))
    nodes = raw['nodi']
    ids = tuple(raw['ordine_nodi'])
    if len(ids) != 6 or ids[0] != 'D0' or len(set(ids)) != len(ids):
        raise ValueError('Attesi D0 e cinque clienti con identificativi distinti')
    by_id = {n['id']: n for n in nodes}
    if len(by_id) != 6 or set(by_id) != set(ids):
        raise ValueError('Nodi e ordine_nodi non corrispondono')
    comuni = tuple(by_id[id]['comune'] for id in ids)
    domande = tuple(int(by_id[id]['kg']) for id in ids)
    if domande[0] != 0 or any(kg <= 0 for kg in domande[1:]):
        raise ValueError('Domande non valide: deposito 0 e clienti con kg positivi')
    if raw['studente']['matricola'] != '0312300147' or raw['studente']['residenza_comune'] != 'Sesto San Giovanni':
        raise ValueError('Intestazione non corrispondente al caso Simone Efrem Ferrara')
    if by_id['D0']['comune'] != 'Sesto San Giovanni':
        raise ValueError('Deposito non in Sesto San Giovanni')
    if int(raw['vincoli']['domanda_kg_totale']) != sum(domande):
        raise ValueError('Domanda totale incoerente')
    matrix_raw = raw['matrice_distanze_km']
    if len(matrix_raw) != len(ids) or any(len(row) != len(ids) for row in matrix_raw):
        raise ValueError('Matrice distanze di dimensione errata')
    mat = tuple(tuple(dec(x) for x in row) for row in matrix_raw)
    for i, row in enumerate(mat):
        for j, dist in enumerate(row):
            if i == j and dist != 0:
                raise ValueError(f'Diagonale non nulla: {ids[i]}')
            if i != j and dist <= 0:
                raise ValueError(f'Arco {ids[i]} -> {ids[j]} non positivo')
    raw_s = raw['scenari_veicoli']
    sa = _scenario(raw_s['scenario_A'], 'A')
    sb = _scenario(raw_s['scenario_B'], 'B')
    if sa.veicoli != 1 or sb.veicoli != 2:
        raise ValueError('La traccia richiede 1 mezzo (A) e 2 mezzi (B)')
    if sum(domande) > sa.capacita_kg or not sb.capacita_kg < sum(domande) <= 2*sb.capacita_kg:
        raise ValueError('Vincoli dei due scenari incoerenti con la domanda')
    if any(d > sb.capacita_kg for d in domande[1:]):
        raise ValueError('Cliente troppo grande per i mezzi dello scenario B')
    op = raw['parametri_operativi']
    velocita = dec(op['velocita_media_km_h'])
    minuti_scarico = int(op['minuti_scarico_per_cliente'])
    minuti_carico = int(op['minuti_carico_deposito_per_veicolo'])
    _positivo(velocita, 'Velocita media')
    if minuti_scarico < 0 or minuti_carico < 0:
        raise ValueError('Tempi di carico/scarico negativi')
    return Instance(raw,path,ids,comuni,domande,mat,sa,sb,velocita,minuti_scarico,minuti_carico)


def verifica_coerenza_csv(instanza: Instance, cartella_dati: str | Path) -> dict:
    """Controlla tutti gli archi rispetto a due file della Fase 1."""
    cartella = Path(cartella_dati)
    with (cartella/'matrice_distanze_direzionale_km.csv').open('r',encoding='utf-8-sig',newline='') as f:
        rows = list(csv.reader(f,delimiter=';'))
    if rows[0] != ['origine/destinazione',*instanza.ids] or len(rows) != len(instanza.ids)+1:
        raise ValueError('Intestazioni della matrice CSV non coerenti')
    for i, row in enumerate(rows[1:]):
        if row[0] != instanza.ids[i] or len(row) != len(instanza.ids)+1:
            raise ValueError('Ordine nodi della matrice CSV non coerente')
        for j,v in enumerate(row[1:]):
            if dec(v) != instanza.matrice[i][j]:
                raise ValueError(f'JSON/CSV diversi: {instanza.ids[i]} -> {instanza.ids[j]}')
    with (cartella/'fonti_distanze_direzionali.csv').open('r',encoding='utf-8-sig',newline='') as f:
        sources = list(csv.DictReader(f,delimiter=';'))
    lookup = {v:i for i,v in enumerate(instanza.ids)}
    counted: set[tuple[int,int]] = set()
    for s in sources:
        a,b = s['origine_id'],s['destinazione_id']
        if a not in lookup or b not in lookup or a == b:
            raise ValueError('Fonte con coppia di nodi non valida')
        key = (lookup[a],lookup[b])
        if key in counted:
            raise ValueError('Fonte duplicata per arco direzionale')
        counted.add(key)
        if dec(s['km_stradali']) != instanza.matrice[key[0]][key[1]]:
            raise ValueError(f'Fonte e matrice discordanti: {a} -> {b}')
        if not s['url'].startswith(('https://','http://')):
            raise ValueError(f'URL mancante per {a} -> {b}')
    expected = {(i,j) for i in range(len(instanza.ids)) for j in range(len(instanza.ids)) if i!=j}
    if counted != expected:
        raise ValueError(f'Fonti insufficienti: {len(counted)}/{len(expected)} archi')
    return {'nodi':len(instanza.ids),'clienti':len(instanza.clienti),'archi':len(counted),'csv_json_coerenti':True}
