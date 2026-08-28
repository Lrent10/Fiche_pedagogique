import { useEffect, useRef } from 'react'
import renderMathInElement from 'katex/contrib/auto-render'
import 'katex/dist/katex.min.css'

export function LatexPreview({ content, compact = false }: { content: string; compact?: boolean }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!ref.current) return
    ref.current.textContent = content
    renderMathInElement(ref.current, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
        { left: '\\[', right: '\\]', display: true },
      ],
      throwOnError: false,
    })
  }, [content])
  const hasTikz = content.includes('tikzpicture')
  return (
    <div className={`latex-preview ${compact ? 'compact' : ''}`}>
      <div ref={ref} />
      {hasTikz && <span className="tikz-note">Figure TikZ : rendu complet dans le PDF</span>}
    </div>
  )
}
