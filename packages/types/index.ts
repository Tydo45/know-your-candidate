export type Sourced<T> = {
  value: T
  source_url: string
}

export type Stance = {
  issue: string
  position: string
}

export type Candidate = {
  id: string
  name: string
  office: string
  party: Sourced<string>
  district?: string
  state?: string
  is_incumbent?: boolean
  photo_url?: string
  social_links?: string[]
  bio_text?: Sourced<string>
  age?: number
  gender?: string
  race?: string
  marital_status?: string
  past_positions?: Sourced<string>[]
  stance_summary: Sourced<Stance>[]
}
