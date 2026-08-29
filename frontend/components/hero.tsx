"use client"

import { useRef, useState } from "react"
import { motion } from "framer-motion"
import { LeafTrace } from "@/components/leaf-trace"

type Props = {
  onFile: (file: File) => void
  onSample: () => void
  loading: boolean
  error: string | null
}

const FACTS = [
  ["32", "species"],
  ["155", "descriptors"],
  ["1,906", "reference scans"],
  ["98.2%", "held-out accuracy"],
]

export function Hero({ onFile, onSample, loading, error }: Props) {
  const input = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) onFile(file)
  }

  return (
    <section className="relative min-h-screen w-full flex flex-col justify-center px-4 md:px-12 pt-28 pb-16 overflow-hidden">
      <div className="absolute inset-0 plate-grid pointer-events-none" />

      <div className="relative z-10 w-full max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-8 items-center">
        <motion.div
          className="lg:col-span-7"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
        >
          <p className="label mb-6">Leafprint · classical computer vision</p>
          <h1 className="font-serif text-[13vw] lg:text-[7.5vw] leading-[0.88] tracking-[-0.03em] text-paper">
            Thirty-two
            <br />
            species from
            <br />
            <span className="italic font-light text-leaf-bright">one outline.</span>
          </h1>
          <p className="mt-8 max-w-md text-[15px] font-light leading-relaxed text-muted-foreground">
            Photograph a leaf against a plain background. The pipeline separates it
            from the page, straightens it, and takes 155 measurements of shape,
            margin, vein and texture — then matches them against a reference
            collection. No neural network anywhere in the chain.
          </p>

          <dl className="mt-10 flex flex-wrap gap-x-10 gap-y-4 border-t border-border pt-6 max-w-lg">
            {FACTS.map(([value, label]) => (
              <div key={label}>
                <dt className="font-mono text-xl text-leaf-bright">{value}</dt>
                <dd className="label mt-1">{label}</dd>
              </div>
            ))}
          </dl>
        </motion.div>

        <motion.div
          className="lg:col-span-5"
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.25, ease: "easeOut" }}
        >
          <div
            onDragOver={(e) => {
              e.preventDefault()
              setOver(true)
            }}
            onDragLeave={() => setOver(false)}
            onDrop={handleDrop}
            className={`relative border transition-colors ${
              over ? "border-leaf-bright bg-bark/70" : "border-line bg-bark/40"
            }`}
          >
            {/* Plate corner marks — a specimen sheet's registration crops. */}
            {[
              "top-0 left-0 border-t border-l",
              "top-0 right-0 border-t border-r",
              "bottom-0 left-0 border-b border-l",
              "bottom-0 right-0 border-b border-r",
            ].map((pos) => (
              <span
                key={pos}
                className={`absolute w-5 h-5 border-leaf/70 pointer-events-none ${pos}`}
              />
            ))}

            <div className="px-8 py-14 flex flex-col items-center text-center">
              <LeafTrace className="w-28 h-44" loop={loading} />

              <p className="mt-8 font-serif text-2xl text-paper">
                {loading ? "Measuring the specimen" : "Drop a leaf photograph"}
              </p>
              <p className="mt-2 text-sm text-muted-foreground max-w-[15rem]">
                {loading
                  ? "Segmenting, straightening, then measuring."
                  : "JPEG, PNG, BMP or TIFF up to 10 MB. Plain background works best."}
              </p>

              <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
                <button
                  type="button"
                  onClick={() => input.current?.click()}
                  disabled={loading}
                  className="px-7 py-3 font-mono text-[11px] uppercase tracking-[0.18em] bg-leaf-bright text-ink hover:bg-leaf transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {loading ? "Working" : "Choose a file"}
                </button>

                <button
                  type="button"
                  onClick={onSample}
                  disabled={loading}
                  className="px-7 py-3 font-mono text-[11px] uppercase tracking-[0.18em] border border-line text-paper hover:border-leaf-bright hover:text-leaf-bright transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Try a sample leaf
                </button>
              </div>

              <input
                ref={input}
                type="file"
                accept="image/jpeg,image/png,image/bmp,image/tiff,image/webp"
                className="sr-only"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) onFile(file)
                  e.target.value = ""
                }}
              />
            </div>

            {error && (
              <p
                role="alert"
                className="border-t border-tone/50 bg-tone/10 px-6 py-4 text-sm text-tone"
              >
                {error}
              </p>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
