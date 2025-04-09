// Shared structure for sourced values
export type SourcedStr = {
  value: string
  source_url: string
}

export type Stance = {
  issue: string
  position: string
  source_url?: string
  created_at?: string
}

export type Candidate = {
  id: string
  name: string
  office: string
  party?: SourcedStr
  district?: string
  state?: string
  is_incumbent?: boolean
  photo_url?: string
  social_links?: string[]
  bio_text?: SourcedStr
  age?: number
  gender?: string
  race?: string
  marital_status?: string
  past_positions?: SourcedStr[]
  stance_summary: Stance[]
  created_at: string
  last_updated: string
}