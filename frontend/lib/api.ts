export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export type Prediction = { label: string; confidence: number }

export type Species = {
  id: string
  common_name: string
  scientific_name: string
  family: string | null
  margin_type: string | null
  notes: string | null
}

export type Analysis = {
  id: string
  filename: string
  created_at: string
  model_key: string | null
  prediction: Prediction | null
  top_k: Prediction[]
  margin_type: string | null
  feature_groups: Record<string, Record<string, number>>
  feature_count: number
  meta: Record<string, unknown>
  stage_urls: Record<string, string>
}

/** Stage keys in the order the pipeline produces them. */
export const STAGES = [
  { key: "original", caption: "Resized to the working frame" },
  { key: "mask_raw", caption: "Leaf separated from background" },
  { key: "mask_final", caption: "Petiole removed, axis rotated upright" },
  { key: "descriptors", caption: "Contour, hull, fitted ellipse and lobe notches" },
] as const

export const staticUrl = (path: string) => `${API_BASE}${path}`

async function post<T>(path: string, body: FormData): Promise<T> {
  let res: Response
  try {
    res = await fetch(`${API_BASE}${path}`, { method: "POST", body })
  } catch {
    throw new Error(
      `Can't reach the analysis service at ${API_BASE}. Start it with: uvicorn backend.app.main:app --port 8000`,
    )
  }
  if (!res.ok) {
    // FastAPI puts the readable reason in `detail`.
    const detail = await res.json().catch(() => null)
    throw new Error(detail?.detail ?? `Analysis failed (${res.status}).`)
  }
  return res.json()
}

export function analyse(file: File, model?: string) {
  const form = new FormData()
  form.append("file", file)
  const query = model ? `?model=${encodeURIComponent(model)}&top_k=5` : "?top_k=5"
  return post<Analysis>(`/api/analyze${query}`, form)
}

export async function fetchSpecies(): Promise<Record<string, Species>> {
  try {
    const res = await fetch(`${API_BASE}/api/species`)
    if (!res.ok) return {}
    const list: Species[] = await res.json()
    return Object.fromEntries(list.map((s) => [s.id, s]))
  } catch {
    return {}
  }
}
