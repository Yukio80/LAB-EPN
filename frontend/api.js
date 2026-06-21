const API = window.API_URL || ''
const FALLBACK = 'http://localhost:8765'

async function falar(url, opts) {
  const resp = await fetch(url, opts).catch(() => null)
  if (resp && resp.ok) return resp.json()
  if (!url.startsWith(FALLBACK)) {
    const fallbackUrl = FALLBACK + url.slice(API.length)
    const resp2 = await fetch(fallbackUrl, opts).catch(() => null)
    if (resp2 && resp2.ok) return resp2.json()
    if (resp2) { const e = new Error('fetch failed'); e.response = resp2; throw e }
  }
  if (resp) { const e = new Error('fetch failed'); e.response = resp; throw e }
  throw new Error('Failed to fetch')
}

export default {
  listar: () => falar(API + '/propostas'),
  obter: (id) => falar(API + `/propostas/${id}`),
  criar: (dados) => falar(API + '/propostas', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(dados) }),
  simular: (id) => falar(API + `/propostas/${id}/simular`, { method:'POST' }),
  publicar: (id) => falar(API + `/propostas/${id}/publicar`, { method:'POST' }),

  votacao: {
    listar: () => falar(API + '/votacao/propostas'),
    votar: (id, voto, creditos) => falar(API + `/votacao/propostas/${id}/votar?voto=${voto}&creditos=${creditos}`, { method:'POST' }),
    resultado: (id) => falar(API + `/votacao/propostas/${id}/resultado`),
  },

  admin: {
    dashboard: () => falar(API + '/admin/dashboard'),
    pesos: () => falar(API + '/admin/pesos'),
    atualizarPesos: (ods_id, pesos, justificativa) => falar(API + '/admin/pesos', { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ods_id, pesos, justificativa}) }),
    auditoria: () => falar(API + '/admin/auditoria'),
    pendentes: () => falar(API + '/admin/propostas/pendentes'),
    validar: (id, decisao, parecer) => falar(API + `/admin/propostas/${id}/validar`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({decisao, parecer}) }),
    votacoes: () => falar(API + '/admin/votacoes'),
  }
}
