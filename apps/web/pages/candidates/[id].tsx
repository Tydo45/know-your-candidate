import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import type { Candidate, Stance } from "@know/types"

export default function CandidateProfile() {
  const router = useRouter()
  const { id } = router.query
  const [candidate, setCandidate] = useState<Candidate | null>(null)

  useEffect(() => {
    if (!id) return

    fetch(`http://localhost:8000/candidates/${id}`)
      .then(res => res.json())
      .then(setCandidate)
      .catch(err => console.error("Failed to load candidate", err))
  }, [id])

  if (!candidate) return <p className="p-6">Loading...</p>

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-10">

      {/* Header */}
      <div className="flex flex-col sm:flex-row items-center gap-6">
        {candidate.photo_url ? (
          <img
            src={candidate.photo_url}
            alt={`Photo of ${candidate.name}`}
            className="w-28 h-28 object-cover rounded-full border"
          />
        ) : (
          <div className="w-28 h-28 rounded-full bg-gray-200 flex items-center justify-center text-xl text-gray-500 font-semibold">
            {candidate.name.split(" ").map(n => n[0]).join("")}
          </div>
        )}

        <div className="flex-1">
          <h1 className="text-3xl font-bold">{candidate.name}</h1>
          <p className="text-gray-600">{candidate.office}</p>
          <p className="text-sm text-gray-500">{candidate.party}</p>
          {candidate.is_incumbent && (
            <span className="inline-block mt-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
              Incumbent
            </span>
          )}
        </div>

        {/* Social Links */}
        {candidate.social_links?.length > 0 && (
          <div className="flex flex-col gap-1 text-blue-600 text-sm">
            {candidate.social_links.map((link, i) => (
              <a key={i} href={link} target="_blank" rel="noopener noreferrer" className="underline">
                {new URL(link).hostname.replace("www.", "")}
              </a>
            ))}
          </div>
        )}
      </div>

      {/* Quick Info Panel */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-white shadow rounded-lg p-6">
        {candidate.age && <p><strong>Age:</strong> {candidate.age}</p>}
        {candidate.gender && <p><strong>Gender:</strong> {candidate.gender}</p>}
        {candidate.race && <p><strong>Race:</strong> {candidate.race}</p>}
        {candidate.marital_status && <p><strong>Marital Status:</strong> {candidate.marital_status}</p>}
        {candidate.state && <p><strong>State:</strong> {candidate.state}</p>}
        {candidate.district && <p><strong>District:</strong> {candidate.district}</p>}
        {candidate.past_positions?.length > 0 && (
          <p className="sm:col-span-2">
            <strong>Past Positions:</strong> {candidate.past_positions.join(", ")}
          </p>
        )}
      </div>

      {/* Stance Summary */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">Positions on Key Issues</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {candidate.stance_summary.map((stance, idx) => (
            <div key={idx} className="bg-white shadow rounded p-4">
              <p className="font-semibold text-gray-800">{stance.issue}</p>
              <p className="text-sm text-gray-600 mt-1">{stance.position}</p>
              {stance.source_url && (
                <a
                  href={stance.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 underline mt-2 inline-block"
                >
                  Source
                </a>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Biography */}
      {candidate.bio_text && (
        <div className="bg-white shadow rounded-lg">
          <h2 className="text-2xl font-semibold p-6 border-b">About {candidate.name}</h2>
          <p className="p-6 text-gray-700 whitespace-pre-line">{candidate.bio_text}</p>
        </div>
      )}
    </div>
  )
}