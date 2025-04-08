import { useEffect, useState } from "react"
import type { Candidate } from "@know/types"
import CandidateCard from "@/components/CandidateCard"

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([])

  useEffect(() => {
    fetch("http://localhost:8000/candidates/")
      .then(res => res.json())
      .then(setCandidates)
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 p-4">Candidate Directory</h1>

      {candidates.length === 0 ? (
        <p className="text-gray-500">No candidates found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {candidates.map(c => (
            <CandidateCard
              key={c.id}
              id={c.id}
              name={c.name}
              office={c.office}
              party={c.party}
              photo_url={c.photo_url}
            />
          ))}
        </div>
      )}
    </div>
  )
}
