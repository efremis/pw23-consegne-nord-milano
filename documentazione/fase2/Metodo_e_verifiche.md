# Modello, dati e verifica della ricerca esatta

## Struttura del grafo

Si utilizza un grafo completo orientato con sei nodi, un deposito `D0` e cinque clienti. Ciascun arco `i -> j` possiede il peso `d_ij` tratto dalla matrice stradale direzionale della Fase 1; `d_ij` non viene sostituito automaticamente con `d_ji`. I 30 archi hanno una fonte documentata, e il programma esamina ogni itinerario ammesso.

Per un percorso che visita i clienti `c1,...,ck`, la distanza è `d(0,c1)+d(c1,c2)+...+d(ck,0)`.

## Scenario A

Cinque clienti e un solo furgone da 900 kg: la domanda complessiva di 780 kg rispetta la capacità. Si enumerano tutte le `5! = 120` permutazioni. Non si abbrevia la ricerca con tecniche euristiche.

## Scenario B

La capacità di un mezzo è 450 kg: poiché il totale è 780 kg, entrambi i mezzi devono partire. Ogni cliente deve essere assegnato a uno soltanto dei due furgoni. Con due mezzi identici, fissare il cliente `C1` nel primo mezzo evita di esaminare due volte la stessa ripartizione con veicoli scambiati. Restano `2^(5-1)-1 = 15` partizioni non vuote non equivalenti, poi si scartano quelle con carico superiore a 450 kg per almeno un furgone. Per ogni ripartizione restante, vengono esaminate **tutte** le permutazioni nei due gruppi.

Questa procedura produce l'ottimo globale per la distanza totale perché nessuna soluzione ammissibile e distinta viene esclusa; lo scambio fra veicoli non cambia la distanza complessiva.

## Tempi e costi

Con velocità media `v`, tempo di scarico `t_s` e tempo di carico iniziale `t_c`:

`ore_veicolo = km_veicolo/v + (numero_clienti*t_s+t_c)/60`.

`costo = numero_mezzi*noleggio + km_totali*costo_unitario_km + ore_autista_totali*costo_orario`.

Lo scenario B riporta sia la somma delle ore dei due autisti (impiegata nel costo) sia il massimo delle due durate (tempo necessario a completare tutti i giri se i mezzi partono contemporaneamente). La velocità è una media operativa dello studio; le distanze restano quelle stradali documentate.

## Controlli

Il programma verifica le corrispondenze JSON/CSV, tutte le 30 fonti, la positività degli archi e la diagonale nulla. Rifiuta istanze incompatibili con i vincoli di capacità e percorsi contenenti clienti duplicati. I test controllano la ricerca completa anche con una matrice piccola e asimmetrica, così da verificare l'algoritmo senza dipendere soltanto dal risultato dell'istanza principale.
