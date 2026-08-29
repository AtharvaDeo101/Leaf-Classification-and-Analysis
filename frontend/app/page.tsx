"use client"

import { useEffect, useRef, useState } from "react"
import { MotionConfig } from "framer-motion"
import { Hero } from "@/components/hero"
import { SpecimenSheet } from "@/components/specimen-sheet"
import { Method } from "@/components/method"
import { Footer } from "@/components/footer"
import { analyse, fetchSpecies, type Analysis, type Species } from "@/lib/api"

export default function Page() {
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [species, setSpecies] = useState<Record<string, Species>>({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sheet = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fetchSpecies().then(setSpecies)
  }, [])

  const handleFile = async (file: File) => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyse(file)
      setAnalysis(result)
      requestAnimationFrame(() =>
        sheet.current?.scrollIntoView({ behavior: "smooth", block: "start" }),
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed.")
      setAnalysis(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSample = async () => {
    try {
      const blob = await (await fetch("/sample-leaf.jpg")).blob()
      await handleFile(new File([blob], "sample-japanese-maple.jpg", { type: "image/jpeg" }))
    } catch {
      setError("Couldn't load the sample leaf.")
    }
  }

  return (
    // Reveals start at opacity 0, so anyone who suppresses motion must be
    // dropped straight at the final state rather than left with a blank page.
    <MotionConfig reducedMotion="user">
      <main className="min-h-screen bg-background text-foreground">
        <Hero
          onFile={handleFile}
          onSample={handleSample}
          loading={loading}
          error={error}
        />
        <div ref={sheet}>
          {analysis && <SpecimenSheet analysis={analysis} species={species} />}
        </div>
        <Method analysis={analysis} />
        <Footer />
      </main>
    </MotionConfig>
  )
}
