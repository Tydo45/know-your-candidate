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
    <div className="max-w-4xl mx-auto mt-8">
      <h1 className="text-2xl font-bold">{candidate.name}</h1>
      <p className="text-gray-600">{candidate.office}</p>
      <p className="text-gray-500">{candidate.party?.value}</p>

      <div className="mt-4">
        <h2 className="text-lg font-semibold">Bio</h2>
        <p className="p-6 text-gray-700 whitespace-pre-line">
          {candidate.bio_text?.value}
        </p>
      </div>

      {candidate.past_positions?.length > 0 && (
        <p className="sm:col-span-2">
          <strong>Past Positions:</strong>{" "}
          {candidate.past_positions.map(p => p.value).join(", ")}
        </p>
      )}

      <div className="mt-4">
        <h2 className="text-lg font-semibold">Stances</h2>
        <ul className="list-disc pl-5 text-gray-700">
          {candidate.stance_summary.map((stance, idx) => (
            <li key={idx}>
              <strong>{stance.issue}:</strong> {stance.position}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
