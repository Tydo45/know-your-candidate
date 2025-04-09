import Link from "next/link"

type Props = {
  id: string
  name: string
  office: string
  party?: {
    value: string
    source_url: string
  }
  photo_url?: string
}

export default function CandidateCard(props: Props) {
  const { id, name, office, party, photo_url } = props

  return (
    <Link href={`/candidates/${id}`}>
      <div className="p-4 border rounded-md hover:shadow-md transition duration-200">
        <img
          src={photo_url || "https://placehold.co/200x200?text=Candidate"}
          alt={`${name}'s photo`}
          className="w-full h-48 object-cover rounded"
        />
        <h2 className="text-lg font-semibold mt-2">{name}</h2>
        <p className="text-sm text-gray-600">{office}</p>
        <p className="text-sm text-gray-400">{party?.value}</p>
      </div>
    </Link>
  )
}
