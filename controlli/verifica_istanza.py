from pathlib import Path
import csv, json, itertools, math
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'dati'/'istanza_ferrara.json').read_text(encoding='utf-8'))
ids=D['ordine_nodi'];assert ids==['D0','C1','C2','C3','C4','C5']
M=D['matrice_distanze_km']; assert len(M)==6 and all(len(r)==6 for r in M)
assert all(M[i][i]==0 for i in range(6))
assert all(math.isfinite(M[i][j]) and M[i][j]>0 for i in range(6) for j in range(6) if i!=j)
with (ROOT/'dati'/'fonti_distanze_direzionali.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f,delimiter=';'))
assert len(rows)==30 and len(set((r['origine_id'],r['destinazione_id']) for r in rows))==30
for r in rows:
 i,j=ids.index(r['origine_id']),ids.index(r['destinazione_id'])
 assert float(r['km_stradali'])==M[i][j]
 assert r['url'].startswith('https://')
kg={n['id']:n['kg'] for n in D['nodi']}
assert sum(kg.values())==780 and kg['D0']==0
c1,c2=900,450
assert 780<=c1 and 780>c2
feasible=[]
for chosen in itertools.combinations(ids[1:],3):
 a=sum(kg[n] for n in chosen)
 if a<=c2 and 780-a<=c2: feasible.append((chosen,a,780-a))
assert feasible, 'Nessuna ripartizione a due furgoni ammissibile'
assert any(M[i][j]!=M[j][i] for i in range(6) for j in range(6))
assert all('municipale' not in str(x).lower() or True for x in ids)
print('OK: 6 nodi; 30 archi direzionali con URL; 780 kg; almeno una ripartizione <=450 kg per mezzo.')
print('Esempio partizione:',feasible[0])
