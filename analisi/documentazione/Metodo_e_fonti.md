# Analisi dei costi - Metodo e fonti

**Simone Efrem Ferrara · 0312300147**  
**PaneLinea Nord Milano, deposito di Sesto San Giovanni**

## Origine degli input

Gli itinerari e i dati dei mezzi sono contenuti in `dati/istanza_ferrara.json` e in `dati/soluzioni_ottime.json`. La matrice stradale è direzionale e comprende 30 tratte, ognuna associata a una fonte nel file `dati/fonti_distanze_direzionali.csv` della Fase 1. L'ottimizzazione dei chilometri è stata effettuata nella Fase 2 con enumerazione completa dei percorsi e verifica dei vincoli di capacità.

La domanda è di 780 kg presso cinque clienti. Nello scenario A il mezzo da 900 kg serve tutti i clienti (31,0 km). Nello scenario B il primo furgone da 450 kg serve 430 kg e percorre 21,0 km; il secondo serve 350 kg e percorre 19,8 km. I due mezzi percorrono quindi 40,8 km complessivi.

## Formule

Per ogni giro:  
`ore = km/26 + (20 + 12*numero_clienti)/60`

Per il costo:  
`C = numero_veicoli*noleggio_unitario + km_totali*tariffa_km + somma_ore_autista*18.40`

Le ore-autista sono 2,5256410256 per lo scenario A e 3,2358974359 per lo scenario B. Il tempo di completamento con due mezzi è il massimo tra le due durate, non la loro somma. In condizioni base il differenziale di completamento è di 47,076923 minuti.

Le componenti base prima degli arrotondamenti sono:

- A: noleggio 105,00 €; chilometrico 21,39 €; autisti 46,4717948718 €; costo totale 172,8617948718 €.
- B: noleggio 116,00 €; chilometrico 21,216 €; autisti 59,5405128205 €; costo totale 196,7565128205 €.

La differenza tra importi non arrotondati è `196,7565128205 − 172,8617948718 = 23,8947179487 €`, arrotondata a **23,89 €**. Se si sottraggono invece i due totali già arrotondati a due decimali, `196,76 − 172,86 = 23,90 €`: lo scarto di 0,01 € è dovuto alla scelta di non arrotondare gli importi intermedi. Il programma applica arrotondamento HALF_UP soltanto per la visualizzazione.

## Soglie di convenienza

Con noleggio A e costo del personale invariati, il prezzo chilometrico A di pareggio è:

`x = (C_B_base - C_noleggio_A - C_autisti_A)/km_A = 1,4607973532 €/km`

Con tariffa chilometrica B e ore-autista B invariate, il noleggio unitario B di pareggio è:

`y = (C_A_base - C_chilometrico_B - C_autisti_B)/2 = 46,0526410256 €/veicolo/giorno`

Si calcolano due curve a singola variabile e una matrice bidimensionale di 80 combinazioni. La matrice espone `C_B - C_A`: positivo significa convenienza di A, negativo significa convenienza di B.

## Limiti dei risultati

Le distanze sono itinerari stradali pubblicati tra centri urbani e non rilievi porta-a-porta di stabilimenti reali. La società e i clienti sono simulati. I costi sono assunzioni esplicite del modello: non esprimono offerte vincolanti, retribuzioni aziendali certificate o costo netto del carburante aggiornato giornalmente. Non sono modellati IVA, pedaggi, congestionamento dinamico, finestre di consegna, tariffe a scaglioni o costi straordinari. Il confronto misura le due configurazioni nelle ipotesi specificate e mantiene costanti gli itinerari ottimi della Fase 2.
