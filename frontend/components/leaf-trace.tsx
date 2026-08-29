"use client"

import { cn } from "@/lib/utils"

/*
  The outline the pipeline actually works from. Blade first, then midrib, then
  secondary veins — drawn in the order the algorithm derives them, so the
  animation is the method rather than decoration.
*/
const BLADE =
  "M100,18 C140,68 176,140 166,196 C159,242 126,270 100,282 C74,270 41,242 34,196 C24,140 60,68 100,18 Z"
const MIDRIB = "M100,300 L100,20"
const VEINS = [
  "M100,55 C112,60 126,72 136,88",
  "M100,55 C88,60 74,72 64,88",
  "M100,95 C120,100 140,115 152,135",
  "M100,95 C80,100 60,115 48,135",
  "M100,145 C122,153 142,173 152,195",
  "M100,145 C78,153 58,173 48,195",
  "M100,200 C118,210 132,228 140,248",
  "M100,200 C82,210 68,228 60,248",
]

type Props = {
  className?: string
  /** Repeat forever — used as the analysis loading state. */
  loop?: boolean
}

export function LeafTrace({ className, loop = false }: Props) {
  const anim = loop ? "trace-loop" : "trace"

  return (
    <svg
      viewBox="0 0 200 320"
      fill="none"
      aria-hidden="true"
      className={cn("overflow-visible", className)}
    >
      <path
        d={BLADE}
        stroke="var(--leaf-bright)"
        strokeWidth="1.25"
        strokeLinecap="round"
        className={anim}
        style={{ ["--trace-length" as string]: 900, animationDelay: "0ms" }}
      />
      <path
        d={MIDRIB}
        stroke="var(--leaf)"
        strokeWidth="1"
        strokeLinecap="round"
        className={anim}
        style={{ ["--trace-length" as string]: 300, animationDelay: "700ms" }}
      />
      {VEINS.map((d, i) => (
        <path
          key={d}
          d={d}
          stroke="var(--line)"
          strokeWidth="0.9"
          strokeLinecap="round"
          className={anim}
          style={{
            ["--trace-length" as string]: 120,
            animationDelay: `${1000 + i * 90}ms`,
          }}
        />
      ))}
    </svg>
  )
}
