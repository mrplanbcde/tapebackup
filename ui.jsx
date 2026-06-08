/* global React */
const { useState, useEffect, useRef, useCallback } = React;

function Icon({ name, size = 20, stroke = 1.7 }) {
  const p = {
    width: size, height: size, viewBox: "0 0 24 24", fill: "none",
    stroke: "currentColor", strokeWidth: stroke, strokeLinecap: "round", strokeLinejoin: "round",
  };
  const paths = {
    chevron: <polyline points="6 9 12 15 18 9" />,
    arrow: <><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></>,
    left: <polyline points="15 18 9 12 15 6" />,
    right: <polyline points="9 18 15 12 9 6" />,
    search: <><circle cx="11" cy="11" r="7" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></>,
    check: <polyline points="20 6 9 17 4 12" />,
    database: <><ellipse cx="12" cy="5" rx="8" ry="3" /><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" /><path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" /></>,
    shield: <><path d="M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z" /><polyline points="9 12 11 14 15 10" /></>,
    leaf: <><path d="M11 20A7 7 0 0 1 4 13c0-5 5-9 16-9 0 7-3 16-9 16z" /><line x1="6" y1="18" x2="14" y2="10" /></>,
    menu: <><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" /></>,
    bolt: <polygon points="13 2 4 14 11 14 11 22 20 10 13 10 13 2" />,
    lock: <><rect x="4" y="11" width="16" height="9" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></>,
    globe: <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3c2.5 2.5 2.5 15.5 0 18M12 3c-2.5 2.5-2.5 15.5 0 18" /></>,
    tape: <><rect x="2" y="6" width="20" height="12" rx="3" /><circle cx="8" cy="12" r="2.5" /><circle cx="16" cy="12" r="2.5" /><line x1="10.5" y1="12" x2="13.5" y2="12" /></>,
  };
  return <svg {...p} aria-hidden="true">{paths[name]}</svg>;
}

function Social({ name, size = 18 }) {
  if (name === "in") return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M4.98 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-.95 1.83-1.95 3.77-1.95 4.03 0 4.78 2.5 4.78 5.76V21H19.6v-4.9c0-1.17-.02-2.67-1.7-2.67-1.7 0-1.96 1.27-1.96 2.58V21H9z" />
    </svg>
  );
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
      <path d="M18.24 2H21l-6.5 7.43L22 22h-6.1l-4.78-6.25L5.6 22H3l6.96-7.95L2 2h6.26l4.32 5.71zm-1.07 18h1.5L7.92 3.94H6.3z" />
    </svg>
  );
}

function Brand({ footer }) {
  return (
    <a className="brand" href="/" aria-label="TapeBackup.org home">
      <span className="mark">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="3" y="6" width="18" height="12" rx="3" stroke="#fff" strokeWidth="1.8" />
          <circle cx="8" cy="12" r="2.2" fill="#fff" />
          <circle cx="16" cy="12" r="2.2" fill="#fff" />
          <line x1="10.2" y1="12" x2="13.8" y2="12" stroke="#fff" strokeWidth="1.4" />
        </svg>
      </span>
      <span className="wm">
        <span className="t1">TapeBackup</span>
        <span className="t2">LTO Tape Info</span>
      </span>
    </a>
  );
}

Object.assign(window, { Icon, Social, Brand, useState, useEffect, useRef, useCallback });
