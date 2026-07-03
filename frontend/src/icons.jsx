// Crisp 1.6-weight stroke icons + brand mark. No emoji anywhere in the UI.
const base = {
  width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none',
  stroke: 'currentColor', strokeWidth: 1.6, strokeLinecap: 'round', strokeLinejoin: 'round',
}

export function Logo({ size = 30 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none" aria-hidden>
      <defs>
        <linearGradient id="lg" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
          <stop stopColor="#7C93FF" />
          <stop offset="1" stopColor="#5B6BFF" />
        </linearGradient>
      </defs>
      <rect x="2" y="2" width="36" height="36" rx="11" fill="url(#lg)" />
      <path d="M14.5 12.5a4 4 0 0 0 5.2 5.2l6.3 6.3a1.8 1.8 0 0 1-2.5 2.5l-6.3-6.3a4 4 0 0 1-5.2-5.2l2.4 2.4 1.8-1.8-1.7-2.9z"
        fill="#fff" fillOpacity="0.95" />
    </svg>
  )
}

export const IconGrid = (p) => (
  <svg {...base} {...p}><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>
)
export const IconCamera = (p) => (
  <svg {...base} {...p}><path d="M3 8.5A2.5 2.5 0 0 1 5.5 6h1.2a2 2 0 0 0 1.7-1l.5-.8a1.5 1.5 0 0 1 1.3-.7h3.6a1.5 1.5 0 0 1 1.3.7l.5.8a2 2 0 0 0 1.7 1h1.2A2.5 2.5 0 0 1 21 8.5v8A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5z"/><circle cx="12" cy="12" r="3.4"/></svg>
)
export const IconSearch = (p) => (
  <svg {...base} {...p}><circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/></svg>
)
export const IconBox = (p) => (
  <svg {...base} {...p}><path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>
)
export const IconPin = (p) => (
  <svg {...base} {...p}><path d="M20 10c0 5.2-8 12-8 12s-8-6.8-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="2.6"/></svg>
)
export const IconPlus = (p) => (
  <svg {...base} {...p}><path d="M12 5v14M5 12h14"/></svg>
)
export const IconLogout = (p) => (
  <svg {...base} {...p}><path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3M10 17l-5-5 5-5M4 12h11"/></svg>
)
export const IconCheck = (p) => (
  <svg {...base} {...p}><path d="M20 6 9 17l-5-5"/></svg>
)
export const IconArrow = (p) => (
  <svg {...base} {...p}><path d="M5 12h14M13 6l6 6-6 6"/></svg>
)
export const IconSpark = (p) => (
  <svg {...base} {...p}><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/><circle cx="12" cy="12" r="3"/></svg>
)
export const IconWrench = (p) => (
  <svg {...base} {...p}><path d="M15.3 8.7a4 4 0 0 1-5-5l2.7 2.7 2.3-.4.4-2.3-2.7-2.7a4 4 0 0 1 5 5l6 6a2 2 0 0 1-2.8 2.8z"/></svg>
)
