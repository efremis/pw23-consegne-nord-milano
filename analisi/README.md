# PaneLinea Nord Milano - Confronto economico dei percorsi di consegna

**Studente:** Simone Efrem Ferrara · **Matricola:** 0312300147  
**Corso:** Informatica per le Aziende Digitali (L-31) · **Project Work, traccia 23**  
**Deposito:** Sesto San Giovanni (MI)  
**Impresa del caso di studio:** PaneLinea Nord Milano, distribuzione di prodotti da forno confezionati.

## Risultati della giornata tipo

| Indicatore | Scenario A: un furgone | Scenario B: due furgoni |
|---|---:|---:|
| Capacità | 900 kg | 450 kg + 450 kg |
| Merce distribuita | 780 kg | 780 kg |
| Distanza complessiva | 31,0 km | 40,8 km |
| Ore-autista complessive | 2,52564 ore | 3,23590 ore |
| Tempo di completamento | 151,54 min | 104,46 min |
| Noleggio giornaliero | 105,00 € | 116,00 € |
| Costi chilometrici | 21,39 € | 21,22 € |
| Costo degli autisti | 46,47 € | 59,54 € |
| **Costo giornaliero totale** | **172,86 €** | **196,76 €** |

Il costo supplementare dei due furgoni è **23,89 €** calcolando la differenza prima di arrotondare i risultati. La sottrazione dei due importi già arrotondati a centesimi restituisce **23,90 €**: la differenza di un centesimo è soltanto dovuta alla convenzione di arrotondamento. Lo scenario B conclude le operazioni **47,08 minuti prima**, ma impiega due autisti.

## Soglie di pareggio

Si sono variati due prezzi, mantenendo ferme le altre componenti:

- **Costo chilometrico del veicolo A:** soglia di 1,460797 €/km, a fronte di 0,69 €/km nel caso base. Al di sopra della soglia è più economico lo scenario B.
- **Noleggio unitario del veicolo B:** soglia di 46,052641 €/furgone/giorno, a fronte di 58,00 € nel caso base. Al di sotto della soglia è più economico lo scenario B.

La matrice a due variabili esamina le conseguenze di cambiamenti simultanei delle due tariffe.

## File e struttura

| Percorso | Funzione |
|---|---|
| `dati/istanza_ferrara.json` | Distanze direzionali, domande, veicoli, costi e tempi |
| `dati/soluzioni_ottime.json` | Rotte e risultati dell'enumerazione completa della Fase 2 |
| `dati/fonti_distanze_direzionali.csv` | Riferimenti dei 30 archi stradali |
| `src/analisi_economica.py` | Script per ricalcolo dei costi, delle soglie, delle tabelle e dei grafici SVG |
| `tests/test_analisi_economica.py` | 18 verifiche su dati, vincoli, risultati, costi e sensibilità |
| `risultati/analisi_economica.json` | Dati principali, formule e valori precisi, pronti per la pagina HTML |
| `risultati/costi_scenari.csv` | Confronto delle componenti di costo |
| `risultati/sensibilita_costo_km_A.csv` | 29 valori del costo chilometrico del furgone grande |
| `risultati/sensibilita_noleggio_B.csv` | 41 valori del canone di noleggio dei furgoni piccoli |
| `risultati/sensibilita_combinata.csv` | 80 combinazioni di tariffe, con costo e soluzione economicamente conveniente |
| `risultati/grafici/` | Grafici PNG ad alta risoluzione e SVG vettoriali |
| `Analisi_Economica_Ferrara.xlsx` | Modello Excel con formule riferite ai parametri |
| `documentazione/Relazione_Analisi_Economica.pdf` | Rapporto tecnico con grafici, spiegazioni e conclusioni |
| `documentazione/Metodo_e_fonti.md` | Dati, perimetro di calcolo, ipotesi e arrotondamenti |

## Esecuzione e controlli

È sufficiente **Python 3.10 o successivo**, senza dipendenze esterne per il calcolo:

```bash
python src/analisi_economica.py
python -m unittest discover -s tests -v
```

Lo script ricostruisce le ore effettive dalle rotte e dai parametri della Fase 1, controlla le distanze tratta per tratta, verifica i vincoli e genera nuovamente JSON, CSV e grafici SVG. I PNG e il PDF sono allegati come materiali di rappresentazione. Il file Excel consente di modificare le ipotesi e osservare l'effetto sui costi con formule, anziché importi statici.

## Criterio di lettura

Per il **costo del lavoro** si sommano le durate dei due autisti. Per il **tempo necessario a completare il servizio** nello scenario B si utilizza invece la durata del più lento dei due percorsi eseguiti contemporaneamente. I due indicatori non sono intercambiabili.

Le distanze sono quelle degli itinerari stradali tra centri urbani documentati nei file della Fase 1; le tariffe, la velocità media e i tempi operativi sono ipotesi dello scenario aziendale. Non sono preventivi commerciali né misure di traffico in tempo reale. IVA esclusa; pedaggi non previsti nel modello.
