/* PaneLinea Nord Milano — confronto economico dei percorsi. */
(() => {
  'use strict';
  const dataset = window.PANELINEA_DATA;
  if (!dataset) {
    document.body.insertAdjacentHTML('afterbegin', '<p role="alert" style="padding:16px;background:#ffe3d7;color:#622e1e">Impossibile caricare i dati del progetto.</p>');
    return;
  }
  const { istanza, soluzioni, economia } = dataset;
  const $ = id => document.getElementById(id);
  const eur = new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR', minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const dec = (n, digits = 2) => new Intl.NumberFormat('it-IT', {minimumFractionDigits: digits, maximumFractionDigits: digits}).format(n);
  const safe = v => String(v).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

  function setupTables() {
    const tbody = $('client-table');
    istanza.nodi.slice(1).forEach(c => {
      const tr = document.createElement('tr');
      const id = document.createElement('td');id.textContent = c.id;
      const name = document.createElement('td');name.textContent = c.comune;
      const qty = document.createElement('td');qty.className = 'align-right';qty.textContent = dec(c.kg, 0) + ' kg';
      tr.append(id, name, qty);tbody.appendChild(tr);
    });
    $('matrix-head').innerHTML = '<tr><th scope="col">Da / A</th>' + istanza.ordine_nodi.map(n => '<th scope="col">'+safe(n)+'</th>').join('') + '</tr>';
    istanza.matrice_distanze_km.forEach((row, i) => {
      const tr = document.createElement('tr');
      tr.innerHTML = '<th scope="row">' + safe(istanza.ordine_nodi[i]) + '</th>' + row.map((d,j) => '<td class="' + (i === j ? 'diagonal' : 'value') + '">' + (i === j ? '—' : dec(d, d%1===0?0:1)) + '</td>').join('');
      $('matrix-body').appendChild(tr);
    });
  }

  function setupRoutes() {
    const tabs = document.querySelectorAll('[data-route]');
    tabs.forEach(tab => tab.addEventListener('click', () => {
      const selected = tab.dataset.route;
      tabs.forEach(t => {const active = t.dataset.route === selected;t.classList.toggle('is-active',active);t.setAttribute('aria-pressed', String(active));});
      $('route-panel-a').hidden = selected !== 'a';
      $('route-panel-b').hidden = selected !== 'b';
    }));
  }

  const kmA = Number(soluzioni.scenario_A.km_totali);
  const kmB = Number(soluzioni.scenario_B.km_totali);
  const hrA = Number(economia.scenario_A.ore_autista_somma);
  const hrB = Number(economia.scenario_B.ore_autista_somma);
  const fixedA = Number(istanza.scenari_veicoli.scenario_A.noleggio_euro_giorno_per_veicolo);
  const kmPriceB = Number(istanza.scenari_veicoli.scenario_B.costo_euro_km);
  const defaults = Object.freeze({ perKmA: Number(istanza.scenari_veicoli.scenario_A.costo_euro_km), rentB: Number(istanza.scenari_veicoli.scenario_B.noleggio_euro_giorno_per_veicolo), wage: Number(istanza.scenari_veicoli.scenario_A.costo_autista_euro_ora) });
  const controls = { perKmA: $('tariff-a'), rentB: $('rent-b'), wage: $('wage') };

  function calculate(perKmA, rentB, wage) {
    const a = { rent:fixedA, km:kmA * perKmA, labor:hrA * wage };
    const b = { rent:2 * rentB, km:kmB * kmPriceB, labor:hrB * wage };
    a.total = a.rent + a.km + a.labor;
    b.total = b.rent + b.km + b.labor;
    return {a,b,delta:b.total-a.total,
      thresholdKmA: (b.total-fixedA-hrA*wage)/kmA,
      thresholdRentB: (a.total-kmB*kmPriceB-hrB*wage)/2};
  }

  function breakdownRow(label, values) {
    const segs = [['Noleggio','rent','bar-rent'],['Km','km','bar-km'],['Autisti','labor','bar-wage']];
    return '<div class="breakdown-row"><div class="breakdown-top"><strong>'+label+'</strong><span>'+eur.format(values.total)+'</span></div><div class="breakdown-bar" aria-label="Ripartizione percentuale: '+segs.map(([name,k])=>name+' '+dec(values[k]/values.total*100,0)+'%').join(', ')+'">'+segs.map(([name,k,cls])=>'<span class="'+cls+'" style="width:'+Math.max(0,values[k]/values.total*100).toFixed(4)+'%" title="'+name+': '+eur.format(values[k])+'"></span>').join('')+'</div><div class="breakdown-detail">'+segs.map(([name,k])=>'<span>'+name+': '+eur.format(values[k])+'</span>').join('')+'</div></div>';
  }

  function lineChart(root, options) {
    const W=570,H=302,L=65,R=20,T=18,B=52;
    const xMin=options.xMin,xMax=options.xMax,xSpan=xMax-xMin;
    const xTo=v=> L + (v-xMin)/xSpan*(W-L-R);
    const seq=[];
    for(let i=0;i<=70;i++) { const x=xMin + i*xSpan/70;const vals=options.price(x);seq.push({x,a:vals.a,b:vals.b}); }
    const minimum=Math.min(...seq.map(p=>Math.min(p.a,p.b)));
    const maximum=Math.max(...seq.map(p=>Math.max(p.a,p.b)));
    const pad=Math.max(6,(maximum-minimum)*.13);
    const yMin=Math.max(0,minimum-pad),yMax=maximum+pad;
    const yTo=v=>T+(yMax-v)/(yMax-yMin)*(H-T-B);
    const colorA='#2e8579',colorB='#c78655';
    const linePath=key=>seq.map((d,i)=>(i===0?'M':'L')+xTo(d.x).toFixed(2)+' '+yTo(d[key]).toFixed(2)).join(' ');
    let axis='';
    for(let i=0;i<=4;i++) {
      const val=yMin+(yMax-yMin)*i/4;
      const y=yTo(val);
      axis+='<line x1="'+L+'" y1="'+y.toFixed(1)+'" x2="'+(W-R)+'" y2="'+y.toFixed(1)+'" stroke="#e3e9e2" stroke-width="1"/>';
      axis+='<text x="'+(L-11)+'" y="'+(y+4).toFixed(1)+'" text-anchor="end" fill="#718176" font-size="11">'+dec(val,0)+' €</text>';
      const x=xMin+(xMax-xMin)*i/4;
      axis+='<text x="'+xTo(x).toFixed(1)+'" y="'+(H-23)+'" text-anchor="middle" fill="#718176" font-size="11">'+dec(x,options.xDigits)+'</text>';
    }
    let active='';
    const vx=options.currentX;
    if (vx>=xMin&&vx<=xMax) {
      const cur=options.price(vx),pX=xTo(vx);
      active='<line x1="'+pX+'" y1="'+T+'" x2="'+pX+'" y2="'+(H-B)+'" stroke="#718a7e" stroke-dasharray="3 4" stroke-width="1.3"/>'+
       '<circle cx="'+pX+'" cy="'+yTo(cur.a)+'" r="5" fill="'+colorA+'" stroke="white" stroke-width="2"/>'+
       '<circle cx="'+pX+'" cy="'+yTo(cur.b)+'" r="5" fill="'+colorB+'" stroke="white" stroke-width="2"/>';
    }
    let breakLine='';
    if(options.threshold >= xMin && options.threshold <= xMax) {
      const tx=xTo(options.threshold);
      breakLine='<line x1="'+tx+'" x2="'+tx+'" y1="'+T+'" y2="'+(H-B)+'" stroke="#c5ab79" stroke-dasharray="5 5" stroke-width="1.4"/>'+
      '<text x="'+Math.min(W-R-4,Math.max(L+4,tx+5))+'" y="'+(T+13)+'" fill="#9b8154" font-size="10">Pari costi</text>';
    }
    root.innerHTML = '<svg viewBox="0 0 '+W+' '+H+'" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'+axis+
      '<path d="'+linePath('a')+'" fill="none" stroke="'+colorA+'" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'+
      '<path d="'+linePath('b')+'" fill="none" stroke="'+colorB+'" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'+
      breakLine+active+
      '<text x="'+((L+W-R)/2)+'" y="'+(H-1)+'" text-anchor="middle" fill="#6d7a72" font-size="12" font-weight="600">'+safe(options.xLabel)+'</text></svg>';
  }

  function refresh() {
    const perKmA=Number(controls.perKmA.value);
    const rentB=Number(controls.rentB.value);
    const wage=Number(controls.wage.value);
    const costs=calculate(perKmA,rentB,wage);
    $('val-a').textContent=dec(perKmA,2)+' €/km';
    $('val-b').textContent=dec(rentB,2)+' €/giorno';
    $('val-w').textContent=dec(wage,2)+' €/ora';
    $('total-a').textContent=eur.format(costs.a.total);
    $('total-b').textContent=eur.format(costs.b.total);
    const m=Math.max(costs.a.total,costs.b.total,0.001);
    $('progress-a').style.width=dec(costs.a.total/m*100,2).replace(',','.')+'%';
    $('progress-b').style.width=dec(costs.b.total/m*100,2).replace(',','.')+'%';
    if(Math.abs(costs.delta)<.005) {
      $('winner-label').textContent='Parità economica';
      $('winner-saving').textContent=eur.format(0);
      $('winner-copy').textContent='I due scenari hanno praticamente lo stesso costo giornaliero con le tariffe selezionate.';
    } else {
      const best=costs.delta>0?'A · Un furgone':'B · Due furgoni';
      $('winner-label').textContent=best;
      $('winner-saving').textContent=eur.format(Math.abs(costs.delta));
      $('winner-copy').textContent='di differenza economica a favore dello scenario '+(costs.delta>0?'A':'B')+'.';
    }
    $('cost-breakdown').innerHTML=breakdownRow('Scenario A',costs.a)+breakdownRow('Scenario B',costs.b);
    $('breakeven-km').textContent=dec(costs.thresholdKmA,3)+' €/km';
    lineChart($('chart-a'),{ xMin:.40,xMax:1.80,xDigits:2,xLabel:'Costo chilometrico del furgone A (€/km)',currentX:perKmA,threshold:costs.thresholdKmA,price:x=>calculate(x,rentB,wage) });
    lineChart($('chart-b'),{ xMin:35,xMax:75,xDigits:0,xLabel:'Noleggio giornaliero di ciascun furgone B (€)',currentX:rentB,threshold:costs.thresholdRentB,price:x=>calculate(perKmA,x,wage) });
    $('chart-a').setAttribute('aria-label','Sensibilità del costo chilometrico A: costo A '+eur.format(costs.a.total)+', costo B '+eur.format(costs.b.total)+', pareggio a '+dec(costs.thresholdKmA,3)+' euro al km.');
    $('chart-b').setAttribute('aria-label','Sensibilità del noleggio B: costo A '+eur.format(costs.a.total)+', costo B '+eur.format(costs.b.total)+', pareggio a '+dec(costs.thresholdRentB,2)+' euro per furgone al giorno.');
  }

  function setupControls(){
    Object.values(controls).forEach(el=>el.addEventListener('input',refresh));
    $('reset-prices').addEventListener('click',()=>{controls.perKmA.value=defaults.perKmA;controls.rentB.value=defaults.rentB;controls.wage.value=defaults.wage;refresh()});
    refresh();
  }
  setupTables();
  setupRoutes();
  setupControls();
})();
