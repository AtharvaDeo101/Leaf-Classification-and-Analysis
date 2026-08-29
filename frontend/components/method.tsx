"use client"

import { motion } from "framer-motion"
import type { Analysis } from "@/lib/api"
import { STAGES, staticUrl } from "@/lib/api"

/*
  A vertical rail rather than four cards: each stage consumes the previous
  one's output, so the numbering and the connector carry real information.
  Thumbnails only appear once there is a specimen — an empty box repeated four
  times says nothing.
*/
export function Method({ analysis }: { analysis: Analysis | null }) {
  return (
    <section className="w-full px-4 md:px-12 py-20 border-t border-border">
      <div className="max-w-[1100px] mx-auto">
        <div className="flex items-baseline justify-between flex-wrap gap-3 mb-12">
          <h2 className="font-serif text-4xl md:text-5xl text-paper">
            How the measurement is made
          </h2>
          <p className="label">
            {analysis ? "This specimen, stage by stage" : "Four stages"}
          </p>
        </div>

        <ol>
          {STAGES.map((stage, i) => {
            const url = analysis?.stage_urls?.[stage.key]
            const last = i === STAGES.length - 1

            return (
              <motion.li
                key={stage.key}
                className="grid grid-cols-[2.5rem_1fr] md:grid-cols-[2.5rem_1fr_9rem] gap-x-5 gap-y-4 pb-10 last:pb-0"
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                {/* Rail: node, then the connector down to the next stage. */}
                <div className="row-span-full flex flex-col items-center">
                  <span className="w-10 h-10 shrink-0 border border-leaf/60 flex items-center justify-center font-mono text-xs text-leaf-bright tabular-nums">
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  {!last && (
                    <span className="flex-1 w-px min-h-8 bg-line mt-2" aria-hidden="true" />
                  )}
                </div>

                <div className="min-w-0">
                  <h3 className="font-serif text-2xl text-paper capitalize leading-tight">
                    {stage.key.replace("_", " ")}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground max-w-xl">
                    {stage.caption}
                  </p>
                </div>

                {url && (
                  <div className="col-start-2 md:col-start-3 md:row-start-1 w-36 aspect-square border border-line bg-bark/40 overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={staticUrl(url)}
                      alt={stage.caption}
                      className="w-full h-full object-contain"
                    />
                  </div>
                )}
              </motion.li>
            )
          })}
        </ol>
      </div>
    </section>
  )
}
