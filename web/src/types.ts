export interface Item {
  id: string
  type: 'album' | 'track'
  url: string
  sales?: number
}

export interface Set {
  items: Item[]
}

export interface BandcampUrl {
  url: string
}

export interface BPMRange {
  min: number
  max: number
}

export interface RecommendationRequest {
  setInput: Set
  bpmRange: BPMRange
  filterBpm: boolean
  sortBy: 'relevance' | 'popularity' | 'random'
}
