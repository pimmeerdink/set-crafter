import axios from 'axios'
import type { BandcampUrl, Item } from '@/types'

const API_BASE =
  (import.meta as any).env?.PUBLIC_API_BASE ?? 'http://localhost:8000'

const client = axios.create({ baseURL: API_BASE })

export async function getBandcampId(input: BandcampUrl): Promise<Item> {
  const { data } = await client.post<Item>('/get-bandcamp-id', input)
  return data
}

export interface GenerateRecommendationsRequest {
  set_input: { items: Item[] }
  bpm_range: { min: number; max: number }
  filter_bpm: boolean
  sort_by: 'relevance' | 'popularity' | 'random'
}

export async function generateRecommendations(
  request: GenerateRecommendationsRequest,
): Promise<Item[]> {
  const { data } = await client.post<Item[]>(
    '/generate-recommendations',
    request,
  )
  return data
}
