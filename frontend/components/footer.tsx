"use client"

export function Footer() {
  return (
    <footer className="w-full px-4 md:px-12 py-14 border-t border-border">
      <div className="max-w-[1600px] mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10">
          <div className="md:col-span-5">
            <h2 className="font-serif text-3xl mb-3 text-paper">
              Shape is enough
            </h2>
            <p className="text-sm leading-relaxed text-muted-foreground max-w-sm">
              Every identification here comes from hand-engineered descriptors —
              geometry, moments, Fourier contours, margin periodicity, venation and
              texture. Nothing is learned end-to-end, so every number in a result
              can be traced back to something measurable on the leaf.
            </p>
          </div>

          <div className="md:col-span-3 md:col-start-7">
            <p className="label mb-3">Reference collection</p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Flavia — 1,907 scans across 32 species, collected by Wu et al. One
              scan fails segmentation and is excluded.
            </p>
          </div>

          <div className="md:col-span-3">
            <p className="label mb-3">Classifiers</p>
            <dl className="space-y-1 font-mono text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">SVM (RBF)</dt>
                <dd className="text-leaf-bright tabular-nums">98.2%</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">Random forest</dt>
                <dd className="text-leaf-bright tabular-nums">95.8%</dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="mt-20 flex justify-between items-end gap-6">
          <span className="font-serif text-[11vw] leading-[0.8] opacity-[0.07] select-none pointer-events-none">
            LEAFPRINT
          </span>
          <button
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
            className="label hover:text-paper transition-colors shrink-0"
            type="button"
          >
            Back to top ↑
          </button>
        </div>
      </div>
    </footer>
  )
}
