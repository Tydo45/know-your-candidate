export type Stance = {
  issue: string
  position: string
  source_url?: string
}

export type Candidate = {
  id: string
  name: string
  office: string
  party: string
  district?: string
  state?: string
  is_incumbent?: boolean
  photo_url?: string
  social_links?: string[]
  bio_text?: string
  age?: number
  gender?: string
  race?: string
  marital_status?: string
  past_positions?: string[]
  stance_summary: Stance[]
}
