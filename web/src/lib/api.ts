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
  tags?: string[]
  tag_match?: 'any' | 'all'
  exclude_owned_by_profile?: string | null
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

export interface ProfileItemsRequest {
  profile_url: string
  source: 'collection' | 'wishlist'
  limit?: number
}

export async function getProfileItems(
  request: ProfileItemsRequest,
): Promise<Item[]> {
  const { data } = await client.post<Item[]>('/get-profile-items', request)
  return data
}

export interface DetectBpmRequest {
  id: string
  url: string
}

export interface DetectBpmResponse {
  bpm: number | null
  error?: string | null
}

export async function detectBpm(
  request: DetectBpmRequest,
): Promise<DetectBpmResponse> {
  const { data } = await client.post<DetectBpmResponse>('/detect-bpm', request)
  return data
}
