/** Refer brand mark: an ink R on a highlighter stroke. Same paths as src/app/icon.svg. */
export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" className="shrink-0">
      <path
        fill="#FFE45C"
        d="M5.9 3.5H29.4c.8 0 1.1.4 1 1.1L27.6 27.4c-.1.7-.6 1.1-1.3 1.1H2.6c-.8 0-1.1-.4-1-1.1L4.6 4.6c.1-.7.6-1.1 1.3-1.1Z"
      />
      <path
        fill="#18233A"
        fillRule="evenodd"
        d="M9.5 7.5h7.6c3.5 0 5.6 2 5.6 5 0 2.2-1.1 3.8-3 4.5l3.6 7.5h-4.9l-3.1-6.8h-1.1v6.8H9.5Zm4.7 3.5v3.8h2.6c1.3 0 2-.7 2-1.9s-.7-1.9-2-1.9Z"
      />
    </svg>
  );
}

export function Logo() {
  return (
    <span className="flex items-center gap-2.5">
      <LogoMark />
      <span className="text-[1.35rem] font-bold leading-none tracking-[-0.035em]">Refer</span>
    </span>
  );
}
