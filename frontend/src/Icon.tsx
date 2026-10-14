const paths = {
  code: 'm8 5-7 7 7 7m8-14 7 7-7 7m-3-17-2 20',
  book: 'M4 3h13a3 3 0 0 1 3 3v15H7a3 3 0 0 1-3-3V3Zm0 14h16M8 7h8M8 11h5',
  spark: 'm12 2 2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6L12 2Z',
  search: 'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0Z',
  sun: 'M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1 1m12 12 1 1M5 19l1-1M18 6l1-1M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  moon: 'M20 15a9 9 0 0 1-11-11 9 9 0 1 0 11 11Z',
  chevron: 'm8 10 4 4 4-4', check: 'm5 12 4 4L19 6',
  lock: 'M6 10h12v11H6V10Zm3 0V6a3 3 0 0 1 6 0v4',
  download: 'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',
  refresh: 'M20 7V3l-4 4M4 17v4l4-4M5 8a8 8 0 0 1 14-2M19 16A8 8 0 0 1 5 18',
  play: 'm8 4 12 8-12 8V4Z', alert: 'M12 3 2 21h20L12 3Zm0 6v5m0 3v1',
  menu: 'M3 6h18M3 12h18M3 18h18', external: 'M14 3h7v7m0-7L10 14M10 3H3v18h18v-7',
} as const
export default function Icon({ name, size = 18 }: { name: keyof typeof paths; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]} /></svg>
}
