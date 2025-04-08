import Link from "next/link"

type Props = {
  id: string
  name: string
  office: string
  party: string
  photo_url?: string
}

function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
}

export default function CandidateCard({ id, name, office, party, photo_url }: Props) {
  return (
    <Link href={`/candidates/${id}`} className="block">
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer p-4 flex gap-4 items-center">
        {photo_url ? (
          <img
            src={photo_url}
            alt={`${name} photo`}
            className="w-16 h-16 object-cover rounded-full border"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-lg font-semibold">
            {getInitials(name)}
          </div>
        )}

        <div>
          <h2 className="text-lg font-semibold text-gray-800">{name}</h2>
          <p className="text-sm text-gray-600">{office}</p>
          <p className="text-sm text-gray-400">{party}</p>
        </div>
      </div>
    </Link>
  )
}