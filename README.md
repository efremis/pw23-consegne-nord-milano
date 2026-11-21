# Pianificazione delle consegne agroalimentari — PaneLinea Nord Milano

**Project Work · Tema 1, Traccia 23**  
**Studente:** Simone Efrem Ferrara · **Matricola:** 0312300147  
**CdS:** Informatica per le Aziende Digitali (L-31), Università Telematica Pegaso

## Contesto

Il progetto analizza la distribuzione giornaliera di prodotti da forno confezionati per l'impresa simulata **PaneLinea Nord Milano**, con deposito a **Sesto San Giovanni (MI)** e consegne in **Cinisello Balsamo, Bresso, Cologno Monzese, Brugherio e Monza**. La domanda giornaliera complessiva è di **780 kg**.

L'istanza impiega una matrice direzionale di distanze stradali riferite ai centri urbani, con le fonti disponibili in `dati/fonti_distanze_direzionali.csv`. Le quantità, la velocità media e i costi unitari sono parametri del caso aziendale simulato.

## Scenari e risultati

| Indicatore | Un furgone (A) | Due furgoni (B) |
|:--|--:|--:|
| Capacità di ciascun mezzo | 900 kg | 450 kg |
| Distanza totale minima | **31 km** | **40,8 km** |
| Costo giornaliero iniziale | **172,86 €** | **196,76 €** |
| Tempo fino al rientro finale | **151,54 min** | **104,46 min** |

L'enumerazione completa valuta le permutazioni dei cinque clienti nello scenario A e tutte le ripartizioni ammissibili nei due veicoli dello scenario B. I vincoli di capacità sono verificati prima di confrontare le rotte. L'obiettivo primario è minimizzare la distanza totale; l'analisi dei costi valuta successivamente i due scenari.

## Struttura del progetto

| Cartella o file | Contenuto |
|:--|:--|
| `main.py`, `src/panelinea/` | Programma Python ed enumerazione completa |
| `dati/` | Istanza JSON, matrice stradale CSV, clienti, prezzi e 30 fonti direzionali |
| `risultati/` | Percorsi ottimi, permutazioni, combinazioni e grafi SVG/PNG |
| `analisi/` | Calcoli economici, analisi di sensibilità, Excel, grafici e test |
| `docs/` | Sito HTML completo da pubblicare con GitHub Pages |
| `web/` | Versione del sito consultabile anche localmente |
| `Sito_Offline_Apri_Questo.html` | Pagina autonoma senza dipendenze esterne |
| `tests/` | Test del motore Python e della pagina HTML |
| `documentazione/` | Relazioni tecniche, fonti e documenti delle quattro fasi |

## Esecuzione

È richiesto **Python 3.10 o successivo**. Per i calcoli si utilizza la libreria standard, senza solutori TSP/VRP esterni.

```bash
python main.py
python -m unittest discover -s tests -v
python analisi/src/analisi_economica.py
python -m unittest discover -s analisi/tests -v
```

Per aprire la pagina dal computer, usare `Sito_Offline_Apri_Questo.html` oppure `web/index.html`. La cartella `docs/` contiene la versione destinata a GitHub Pages.

## Pubblicazione del sito

Nelle impostazioni della repository aprire **Settings → Pages**, scegliere **Deploy from a branch**, ramo **main**, cartella **/docs** e salvare. La pubblicazione è possibile quando tutti i file sono stati caricati nella repository.

## Modello e limiti

Le distanze sono riportate come chilometri di itinerari stradali fra località, non come rilevazioni di traffico in tempo reale tra specifiche aziende. I clienti e l'impresa sono simulati; il materiale distingue le informazioni geografiche dai parametri operativi ed economici adottati per lo studio. L'analisi di sensibilità mantiene i percorsi fissi mentre modifica i costi unitari e mostra le condizioni di convenienza dei due scenari.
