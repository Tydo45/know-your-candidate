import { useRouter } from "next/router"
import useSWR from "swr"
import { Candidate } from "@know/types"

const fetcher = async (url: string) => {
  const res = await fetch(url)
  if (!res.ok) {
    const error = new Error("Failed to fetch data")
    ;(error as any).status = res.status
    throw error
  }
  return res.json()
}

export default function CandidateProfile() {
  const router = useRouter()
  const { id } = router.query
  const { data: candidate, error } = useSWR<Candidate>(
    id ? `http://localhost:8000/candidates/${id}` : null,
    fetcher
  )

  if (error) {
    return (
      <div className="text-red-500 max-w-2xl mx-auto mt-10">
        Failed to load candidate. Error: {error.message}
      </div>
    )
  }

  if (!candidate) return <div className="mt-10 text-center">Loading...</div>

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      {/* Header */}
      <div className="space-y-1">
        <h1 className="text-3xl font-bold">{candidate.name}</h1>
        <p className="text-gray-600">{candidate.office}</p>
        <p className="text-sm text-gray-500">{candidate.party?.value}</p>
      </div>

      {/* Meta Info */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-white rounded-lg shadow p-4 text-sm text-gray-700">
        {candidate.state && <p><strong>State:</strong> {candidate.state}</p>}
        {candidate.district && <p><strong>District:</strong> {candidate.district}</p>}
        <p><strong>Incumbent:</strong> {candidate.is_incumbent ? "Yes" : "No"}</p>
        {candidate.age && <p><strong>Age:</strong> {candidate.age}</p>}
        {candidate.gender && <p><strong>Gender:</strong> {candidate.gender}</p>}
        {candidate.race && <p><strong>Race:</strong> {candidate.race}</p>}
        {candidate.marital_status && <p><strong>Marital Status:</strong> {candidate.marital_status}</p>}
      </div>

      {/* Bio */}
      {candidate.bio_text && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Bio</h2>
          <p className="whitespace-pre-line text-gray-700">{candidate.bio_text.value}</p>
          {candidate.bio_text.source_url && (
            <a
              href={candidate.bio_text.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 underline mt-2 block"
            >
              Source
            </a>
          )}
        </div>
      )}

      {/* Past Positions */}
      {candidate.past_positions?.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Past Positions</h2>
          <ul className="list-disc pl-5 text-gray-700 space-y-1">
            {candidate.past_positions.map((pos, idx) => (
              <li key={idx}>
                {pos.value}
                {pos.source_url && (
                  <a
                    href={pos.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 text-sm ml-2 underline"
                  >
                    source
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Social Links */}
      {candidate.social_links?.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Social Links</h2>
          <ul className="space-y-1 text-blue-600 text-sm">
            {candidate.social_links.map((url, i) => (
              <li key={i}>
                <a href={url} target="_blank" rel="noopener noreferrer" className="underline">
                  {url}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Stances */}
      {candidate.stance_summary.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Stances</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {candidate.stance_summary.map((stance, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                <h3 className="text-md font-semibold text-gray-800 mb-1">{stance.issue}</h3>
                <p className="text-gray-700">{stance.position}</p>
                {stance.source_url && (
                  <a
                    href={stance.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 underline mt-2 block"
                  >
                    Source
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
