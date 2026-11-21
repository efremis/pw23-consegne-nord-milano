# Pagina web — percorsi e analisi economica

Il sito PaneLinea Nord Milano comprende una rappresentazione schematica dei sei nodi, la matrice direzionale delle distanze, i percorsi minimi per uno e due furgoni, le voci di costo giornaliere e due grafici dinamici di sensibilità.

## Origine dei risultati

- **Dati e domande:** istanza e matrice direzionale della Fase 1.
- **Percorsi e grafi:** elaborazione esaustiva in Python della Fase 2. Un veicolo: 31 km; due veicoli: 40,8 km. Le sequenze dei nodi e i carichi sono riportati nei grafi SVG.
- **Analisi economica:** risultati della Fase 3, 172,86 € contro 196,76 € con tariffe iniziali.

## Soglie economiche

Fissate le altre tariffe al valore iniziale, il pareggio si raggiunge a un costo chilometrico A di circa **1,460797 €/km**; in alternativa, con una tariffa A iniziale, il noleggio di ogni furgone B dovrebbe scendere a circa **46,052641 €/giorno**. L'interfaccia calcola nuovamente queste soglie quando vengono cambiati gli altri parametri.

I grafici mostrano due funzioni di costo lineari. La funzione associata al parametro che si modifica è variabile, mentre quella dell'altro scenario resta fissa rispetto a tale parametro. I numeri visualizzati sono arrotondati al centesimo, ma le differenze sono calcolate prima dell'arrotondamento: la differenza di base è di circa **23,89 €**.

## Interazione e pubblicazione

I file del sito sono indipendenti da risorse esterne. `web/index.html` è apribile localmente; `docs/index.html` contiene la copia destinata alla pubblicazione su GitHub Pages. I dati accessibili dall'interfaccia sono incorporati da JSON in uno script statico, senza modificare i valori delle Fasi 1–3.

I grafi non sono carte geografiche: rappresentano gli archi nell'ordine di visita. La rete di partenza si basa su distanze stradali pubblicate fra centri urbani e sull'istanza simulata, con 30 collegamenti orientati.
