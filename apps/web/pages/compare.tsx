import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import type { Candidate } from "@know/types"

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
}

export default function ComparePage() {
  const router = useRouter()
  const { c1, c2 } = router.query
  const [candidates, setCandidates] = useState<(Candidate | null)[]>([null, null])
  const [allCandidates, setAllCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:8000/candidates/")
      .then(res => res.json())
      .then(setAllCandidates)
  }, [])

  useEffect(() => {
    if (!c1 || !c2) return

    setLoading(true)
    Promise.all([
      fetch(`http://localhost:8000/candidates/${c1}`).then(res => res.json()),
      fetch(`http://localhost:8000/candidates/${c2}`).then(res => res.json()),
    ])
      .then(([a, b]) => setCandidates([a, b]))
      .catch(err => console.error("Error loading candidates:", err))
      .finally(() => setLoading(false))
  }, [c1, c2])

  const handleSelect = (index: 0 | 1, id: string) => {
    const query = { ...router.query, [index === 0 ? "c1" : "c2"]: id }
    router.push({ pathname: "/compare", query })
  }

  const allIssues = candidates[0] && candidates[1]
    ? Array.from(new Set([
        ...candidates[0].stance_summary.map(s => s.issue),
        ...candidates[1].stance_summary.map(s => s.issue),
      ]))
    : []

  const getPosition = (candidate: Candidate, issue: string) =>
    candidate.stance_summary.find(s => s.issue === issue)?.position || "—"

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-10">
      <h1 className="text-3xl font-bold text-center mb-6">Compare Candidates</h1>

      {/* Candidate Selector */}
      <div className="grid grid-cols-3 gap-4 items-end">
        <div></div>
        {[0, 1].map((idx) => (
          <select
            key={idx}
            value={router.query[idx === 0 ? "c1" : "c2"] || ""}
            onChange={(e) => handleSelect(idx as 0 | 1, e.target.value)}
            className="border p-2 rounded w-full"
          >
            <option value="">Select candidate</option>
            {allCandidates.map(c => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        ))}
      </div>

      {/* Candidate Overview Cards */}
      <div className="grid grid-cols-2 gap-6">
        {candidates.map((c, i) =>
          c ? (
            <div key={i} className="bg-white shadow rounded-lg p-4 flex items-center gap-4">
              {c.photo_url ? (
                <img
                  src={c.photo_url}
                  alt={`${c.name} photo`}
                  className="w-16 h-16 rounded-full object-cover border"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-lg font-semibold">
                  {getInitials(c.name)}
                </div>
              )}
              <div>
                <h2 className="text-xl font-semibold">{c.name}</h2>
                <p className="text-sm text-gray-600">{c.office}</p>
                <p className="text-sm text-gray-500">{c.party?.value}</p>
                {c.is_incumbent && (
                  <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded mt-1 inline-block">
                    Incumbent
                  </span>
                )}
              </div>
            </div>
          ) : (
            <div key={i} className="text-gray-400 text-center italic p-4">No candidate selected</div>
          )
        )}
      </div>

      {/* Stance Comparison Cards */}
      {!loading && candidates[0] && candidates[1] && (
        <div className="space-y-6">
          {allIssues.map((issue, idx) => {
            const p1 = getPosition(candidates[0], issue)
            const p2 = getPosition(candidates[1], issue)
            const diff = p1 !== p2

            return (
              <div key={idx}>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{issue}</h3>
                <div className="grid grid-cols-2 gap-4">
                  {[p1, p2].map((position, i) => (
                    <div
                      key={i}
                      className={`rounded border p-4 bg-white shadow ${
                        diff ? "border-red-400" : "border-gray-200"
                      }`}
                    >
                      <p className="text-sm text-gray-700">{position}</p>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
