export function useStatusLabel() {
  const map: Record<string, { label: string; cls: string }> = {
    CREATED: { label: 'Создана', cls: 'bg-slate-800 text-slate-200 ring-1 ring-white/10' },
    AWAITING_PAYMENT: { label: 'Ожидает оплату', cls: 'bg-amber-500/15 text-amber-300 ring-1 ring-amber-500/30' },
    PROCESSING: { label: 'Обработка', cls: 'bg-sky-500/15 text-sky-300 ring-1 ring-sky-500/30' },
    COMPLETED: { label: 'Выполнено', cls: 'bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/30' },
    CANCELED: { label: 'Отменено', cls: 'bg-rose-500/15 text-rose-300 ring-1 ring-rose-500/30' },
    EXPIRED: { label: 'Истёк срок', cls: 'bg-slate-700/60 text-slate-300 ring-1 ring-white/10' },
  }
  return (code?: string) => map[code ?? ''] || { label: code || '—', cls: 'bg-slate-800 text-slate-200 ring-1 ring-white/10' }
}
