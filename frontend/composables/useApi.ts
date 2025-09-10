export function useApi() {
  const cfg = useRuntimeConfig()
  const base = cfg.public.apiBase || '/api'
  return {
    get: (url: string, opts?: any) => $fetch(base + url, opts),
    post: (url: string, body: any, opts?: any) => $fetch(base + url, { method: 'POST', body, ...opts })
  }
}