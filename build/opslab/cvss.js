// CVSS v3.1 Base score, per the FIRST specification (section 7 formulas, Appendix A Roundup).
var CVSS = (function(){
  var W = {AV:{N:0.85,A:0.62,L:0.55,P:0.2}, AC:{L:0.77,H:0.44}, UI:{N:0.85,R:0.62},
           C:{H:0.56,L:0.22,N:0}, I:{H:0.56,L:0.22,N:0}, A:{H:0.56,L:0.22,N:0}};
  function pr(v, s){ return v==='N' ? 0.85 : v==='L' ? (s==='C' ? 0.68 : 0.62) : (s==='C' ? 0.5 : 0.27); }
  function roundup(x){ var i = Math.round(x * 100000); return i % 10000 === 0 ? i / 100000 : (Math.floor(i / 10000) + 1) / 10; }
  function parse(vec){
    var m = {}, ok = /^CVSS:3\.1\//.test(vec);
    (vec.replace(/^CVSS:3\.[01]\//,'')).split('/').forEach(function(p){ var kv = p.split(':'); if(kv.length===2) m[kv[0]] = kv[1]; });
    var need = {AV:'NALP',AC:'LH',PR:'NLH',UI:'NR',S:'UC',C:'HLN',I:'HLN',A:'HLN'};
    for (var k in need){ if(!m[k] || need[k].indexOf(m[k]) < 0) return null; }
    return m;
  }
  function score(m){
    var iss = 1 - (1-W.C[m.C])*(1-W.I[m.I])*(1-W.A[m.A]);
    var imp = m.S==='U' ? 6.42*iss : 7.52*(iss-0.029) - 3.25*Math.pow(iss-0.02, 15);
    var exp = 8.22*W.AV[m.AV]*W.AC[m.AC]*pr(m.PR, m.S)*W.UI[m.UI];
    var base = imp <= 0 ? 0 : m.S==='U' ? roundup(Math.min(imp+exp, 10)) : roundup(Math.min(1.08*(imp+exp), 10));
    return {base:base, impact:imp, exploit:exp, iss:iss, sev:sev(base)};
  }
  function sev(b){ return b===0 ? 'None' : b<4 ? 'Low' : b<7 ? 'Medium' : b<9 ? 'High' : 'Critical'; }
  function vector(m){ return 'CVSS:3.1/' + ['AV','AC','PR','UI','S','C','I','A'].map(function(k){ return k+':'+m[k]; }).join('/'); }
  return {parse:parse, score:score, sev:sev, vector:vector, roundup:roundup, prw:pr, W:W};
})();
if (typeof module !== 'undefined') module.exports = CVSS;
