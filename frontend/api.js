const API = window.API_URL || ''

export default {
  listar: () => fetch(API + '/propostas').then(r => r.json()),
  obter: (id) => fetch(API + `/propostas/${id}`).then(r => r.json()),
  criar: (dados) => fetch(API + '/propostas', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados) }).then(r => { if(!r.ok) throw r; return r.json() }),
  simular: (id) => fetch(API + `/propostas/${id}/simular`, { method:'POST' }).then(r => { if(!r.ok) throw r; return r.json() }),
  publicar: (id) => fetch(API + `/propostas/${id}/publicar`, { method:'POST' }).then(r => { if(!r.ok) throw r; return r.json() }),

  votacao: {
    listar: () => fetch(API + '/votacao/propostas').then(r => r.json()),
    votar: (id, voto, creditos) => fetch(API + `/votacao/propostas/${id}/votar?voto=${voto}&creditos=${creditos}`, { method:'POST' }).then(r => { if(!r.ok) throw r; return r.json() }),
    resultado: (id) => fetch(API + `/votacao/propostas/${id}/resultado`).then(r => r.json()),
  },

  admin: {
    dashboard: () => fetch(API + '/admin/dashboard').then(r => r.json()),
    pesos: () => fetch(API + '/admin/pesos').then(r => r.json()),
    atualizarPesos: (ods_id, pesos, justificativa) => fetch(API + '/admin/pesos', { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ods_id, pesos, justificativa}) }).then(r => { if(!r.ok) throw r; return r.json() }),
    auditoria: () => fetch(API + '/admin/auditoria').then(r => r.json()),
    pendentes: () => fetch(API + '/admin/propostas/pendentes').then(r => r.json()),
    validar: (id, decisao, parecer) => fetch(API + `/admin/propostas/${id}/validar`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({decisao, parecer}) }).then(r => { if(!r.ok) throw r; return r.json() }),
    votacoes: () => fetch(API + '/admin/votacoes').then(r => r.json()),
  }
}
