# Dati logistici - Simone Efrem Ferrara

**Comune del deposito:** Sesto San Giovanni (MI)  
**Clienti:** Cinisello Balsamo, Bresso, Cologno Monzese, Brugherio e Monza  
**Impresa simulata:** PaneLinea Nord Milano  
**Domanda giornaliera:** 780 kg  
**Scenari:** un mezzo da 900 kg; due mezzi da 450 kg ciascuno.

## Distanze stradali utilizzate

I 30 valori della matrice sono presi da pagine pubbliche che riportano itinerari **in automobile su strada** tra i centri urbani dei sei comuni, con una fonte distinta per ciascuna delle trenta direzioni. Non vengono utilizzate distanze in linea d’aria né coefficienti moltiplicativi. La distanza del ritorno è registrata autonomamente e non ricopiata da quella di andata.

Le località di partenza e destinazione sono **centri urbani**, come identificati dai portali stradali. Le sedi dei municipi riportate nella documentazione costituiscono riferimenti territoriali, **non** coordinate per le quali si rivendichi la misura civico-civico. I luoghi commerciali dell'istanza sono simulati; per conoscere la percorrenza porta-a-porta di un'impresa reale sarebbero necessari i suoi indirizzi effettivi.

Fonti: `dati/fonti_distanze_direzionali.csv`, con URL, origine, destinazione, km e data di consultazione per ogni arco. La matrice è in `dati/matrice_distanze_direzionale_km.csv` e nel JSON `dati/istanza_ferrara.json`.

La precisione apparente dei dati segue quella delle fonti (nella maggior parte dei casi chilometri interi, talvolta un decimale). Le rotte possono cambiare in funzione delle restrizioni di circolazione o delle alternative scelte dal navigatore. I km non sono stati inventati e non sono presentati come misure certificate dei civici degli eventuali clienti.

## Distinzione fra fonti e ipotesi

Le distanze provengono dai servizi stradali elencati. Sono invece **parametri del caso aziendale simulato**, non osservazioni di mercato, la domanda di 780 kg, le capacità dei furgoni, noleggi, costi chilometrici, salari, tempi di carico e velocità media. Questo è normale in un modello di confronto economico, purché tali parametri siano dichiarati separatamente dai dati geografici.

## Struttura dei file

- `dati/istanza_ferrara.json`: configurazione integrale per l'applicativo Python;
- `dati/matrice_distanze_direzionale_km.csv`: matrice direzionale 6 × 6;
- `dati/fonti_distanze_direzionali.csv`: 30 archi e 30 link verificabili;
- `dati/clienti.csv`: cinque clienti e quantità;
- `dati/nodi_territoriali.csv`: distinzione fra centro urbano e riferimento amministrativo;
- `dati/parametri_economici.csv`: parametri per le successive fasi;
- `controlli/verifica_istanza.py`: verifica automatica di integrità e vincoli;
- `documentazione/Scheda_Distanze_Stradali.pdf`: relazione di supporto.

## Esecuzione dei controlli

```bash
python controlli/verifica_istanza.py
```

Per la programmazione: usare gli indici in `ordine_nodi`, non riorganizzare l'ordine della matrice e **non imporre la simmetria**. L'ottimizzazione verrà eseguita nella Fase 2; nessun percorso ottimo viene anticipato.
