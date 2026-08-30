"use client"

import { motion } from "framer-motion"
import type { Analysis, Species } from "@/lib/api"
import { staticUrl } from "@/lib/api"

const GROUP_NAMES: Record<string, string> = {
  geometric: "Geometry",
  moments: "Moments",
  contour: "Contour",
  margin: "Margin",
  veins: "Venation",
  texture: "Texture",
  color: "Colour",
}

const GROUP_NOTES: Record<string, string> = {
  geometric: "Area, perimeter, solidity, elongation, circularity",
  moments: "Hu invariants and Zernike polynomials",
  contour: "Elliptic Fourier and centroid-distance descriptors",
  margin: "Tooth depth and periodicity along the edge",
  veins: "Vein density and branching relative to blade area",
  texture: "Grey-level co-occurrence and local binary patterns",
  color: "Channel statistics inside the mask",
}

function Confidence({ value }: { value: number }) {
  const ticks = 40
  const lit = Math.round(value * ticks)
  const low = value < 0.5

  return (
    <div className="flex items-center gap-4">
      <div className="flex gap-[2px]" aria-hidden="true">
        {Array.from({ length: ticks }, (_, i) => (
          <span
            key={i}
            className={`w-[3px] h-6 ${
              i < lit ? (low ? "bg-tone" : "bg-leaf-bright") : "bg-line"
            }`}
          />
        ))}
      </div>
      <span
        className={`font-mono text-lg tabular-nums ${low ? "text-tone" : "text-leaf-bright"}`}
      >
        {(value * 100).toFixed(1)}%
      </span>
    </div>
  )
}

export function SpecimenSheet({
  analysis,
  species,
}: {
  analysis: Analysis
  species: Record<string, Species>
}) {
  const top = analysis.prediction
  const named = top ? species[top.label] : undefined
  const offCollection = analysis.meta?.off_collection === true
  const distance = analysis.meta?.novelty_distance as number | undefined
  const threshold = analysis.meta?.novelty_threshold as number | undefined
  const alternates = analysis.top_k.slice(1)
  const groups = Object.entries(analysis.feature_groups).filter(
    ([, feats]) => Object.keys(feats).length > 0,
  )

  return (
    <motion.section
      className="w-full px-4 md:px-12 py-20"
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: "easeOut" }}
    >
      <div className="max-w-[1600px] mx-auto border-t border-l border-border">
        {/* Determination */}
        <div className="grid grid-cols-1 lg:grid-cols-12 border-r border-b border-border">
          <div className="lg:col-span-5 border-b lg:border-b-0 lg:border-r border-border p-6 md:p-8">
            <p className="label mb-4">Specimen</p>
            {/*
              Mounted like a herbarium sheet. The scan is left in true colour —
              colour is one of the measured feature families, so tinting it to
              suit the page would misrepresent the specimen.
            */}
            <div className="bg-paper p-3">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={staticUrl(analysis.stage_urls.upload)}
                alt={`Uploaded leaf, ${analysis.filename}`}
                className="w-full h-auto object-contain max-h-[420px] mx-auto"
              />
            </div>
            <p className="mt-3 font-mono text-[11px] text-muted-foreground break-all">
              {analysis.filename}
            </p>
          </div>

          <div className="lg:col-span-7 p-6 md:p-10 flex flex-col justify-center">
            <p className="label mb-5">Determination</p>

            {top && named ? (
              <>
                <h2 className="font-serif text-5xl md:text-6xl italic leading-[0.95] text-paper">
                  {named.scientific_name}
                </h2>
                <p className="mt-3 text-xl text-wash">{named.common_name}</p>

                <div className="mt-7">
                  <Confidence value={top.confidence} />
                </div>

                <dl className="mt-8 grid grid-cols-2 sm:grid-cols-3 gap-6 border-t border-border pt-6">
                  <div>
                    <dt className="label">Family</dt>
                    <dd className="mt-1 font-mono text-sm text-paper">
                      {named.family ?? "—"}
                    </dd>
                  </div>
                  <div>
                    <dt className="label">Margin measured</dt>
                    <dd className="mt-1 font-mono text-sm text-paper">
                      {analysis.margin_type ?? "—"}
                    </dd>
                  </div>
                  <div>
                    <dt className="label">Model</dt>
                    <dd className="mt-1 font-mono text-sm text-paper">
                      {analysis.model_key ?? "—"}
                    </dd>
                  </div>
                </dl>

                {named.notes && (
                  <p className="mt-6 text-sm leading-relaxed text-muted-foreground max-w-lg">
                    {named.notes}
                  </p>
                )}
              </>
            ) : offCollection ? (
              <>
                <h2 className="font-serif text-4xl md:text-5xl italic text-tone leading-tight">
                  Not a leaf in this collection
                </h2>
                <p className="mt-4 text-sm leading-relaxed text-muted-foreground max-w-lg">
                  The shape measured here sits further from all 32 reference species
                  than any real leaf does, so naming one would be a guess. Either the
                  photograph isn&apos;t a leaf, or the leaf couldn&apos;t be separated
                  cleanly from its background.
                </p>
                {distance != null && threshold != null && (
                  <dl className="mt-7 flex gap-10 border-t border-border pt-6">
                    <div>
                      <dt className="label">Distance from collection</dt>
                      <dd className="mt-1 font-mono text-lg text-tone tabular-nums">
                        {distance.toFixed(1)}
                      </dd>
                    </div>
                    <div>
                      <dt className="label">Accepted below</dt>
                      <dd className="mt-1 font-mono text-lg text-paper tabular-nums">
                        {threshold.toFixed(1)}
                      </dd>
                    </div>
                  </dl>
                )}
                <p className="mt-6 text-sm text-muted-foreground">
                  Try a single leaf, flat against a plain background.
                </p>
              </>
            ) : (
              <>
                <h2 className="font-serif text-4xl italic text-wash">
                  Measured, not identified
                </h2>
                <p className="mt-3 text-sm text-muted-foreground max-w-md">
                  The pipeline extracted {analysis.feature_count} descriptors but no
                  model is loaded, so there is nothing to match them against. Train
                  one with <span className="font-mono">python -m src.training.train</span>{" "}
                  and restart the service.
                </p>
              </>
            )}
          </div>
        </div>

        {/* Alternates */}
        {alternates.length > 0 && (
          <div className="border-r border-b border-border p-6 md:p-8">
            <p className="label mb-5">Also considered</p>
            <ol className="divide-y divide-border/60">
              {alternates.map((alt) => {
                const s = species[alt.label]
                return (
                  <li
                    key={alt.label}
                    className="flex items-baseline justify-between gap-4 py-3"
                  >
                    <span className="font-serif text-lg italic text-wash">
                      {s?.scientific_name ?? `Class ${alt.label}`}
                    </span>
                    <span className="hidden sm:block flex-1 mx-4 border-b border-dotted border-line/50" />
                    <span className="text-sm text-muted-foreground shrink-0">
                      {s?.common_name}
                    </span>
                    <span className="font-mono text-sm tabular-nums text-leaf-bright shrink-0 w-16 text-right">
                      {(alt.confidence * 100).toFixed(1)}%
                    </span>
                  </li>
                )
              })}
            </ol>
          </div>
        )}

        {/* Measurements. Hidden on a refusal: the numbers describe whatever
            was segmented, and showing them next to "not a leaf" invites
            reading meaning into figures that have none. */}
        {!offCollection && (
        <div className="border-r border-b border-border p-6 md:p-8">
          <div className="flex items-baseline justify-between flex-wrap gap-2 mb-6">
            <p className="label">Measurements</p>
            <p className="font-mono text-[11px] text-muted-foreground">
              {analysis.feature_count} descriptors · {groups.length} families
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-px bg-border">
            {groups.map(([key, feats]) => {
              const entries = Object.entries(feats)
              return (
                <details key={key} className="group bg-background p-5">
                  <summary className="cursor-pointer list-none">
                    <div className="flex items-baseline justify-between">
                      <h3 className="font-serif text-2xl text-paper">
                        {GROUP_NAMES[key] ?? key}
                      </h3>
                      <span className="font-mono text-sm text-leaf-bright tabular-nums">
                        {entries.length}
                      </span>
                    </div>
                    <p className="mt-2 text-xs leading-relaxed text-muted-foreground">
                      {GROUP_NOTES[key]}
                    </p>
                    <span className="label mt-3 inline-block group-open:hidden">
                      Show values
                    </span>
                    <span className="label mt-3 hidden group-open:inline-block">
                      Hide values
                    </span>
                  </summary>

                  <dl className="mt-4 max-h-64 overflow-y-auto border-t border-border pt-3 space-y-1">
                    {entries.map(([name, value]) => (
                      <div key={name} className="flex justify-between gap-3 text-[11px]">
                        <dt className="font-mono text-muted-foreground truncate">
                          {name}
                        </dt>
                        <dd className="font-mono tabular-nums text-paper shrink-0">
                          {Math.abs(value) >= 1000 || (value !== 0 && Math.abs(value) < 0.01)
                            ? value.toExponential(2)
                            : value.toFixed(3)}
                        </dd>
                      </div>
                    ))}
                  </dl>
                </details>
              )
            })}
          </div>
        </div>
        )}
      </div>
    </motion.section>
  )
}
