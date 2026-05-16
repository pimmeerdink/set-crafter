# set-crafter TODO

## From the user

- [ ] **Paste your bandcamp profile to seed a set**  
  Accept a profile URL (`https://<user>.bandcamp.com`) in the input. Backend
  scrapes the user's wishlist or collection and treats each item as a seed.
  Need a UI affordance to choose which collection (wishlist vs purchased)
  and probably to subsample (don't seed with all 500 items).

- [ ] **Loading state for BPM filter**  
  Currently the UI sits silent for ~20 s while BPM extraction runs. Show
  *something* — at minimum a spinner; better, progress like "checked 40/100
  tracks, found 12 matches" updating live. Server-sent events or a chunked
  response would give real progress instead of a fake spinner.

## My suggestions to consider

- [ ] **Auto-detect BPM of seed tracks**  
  Most users don't know the BPM of the tracks they're seeding with. Run the
  same BPM extraction on the seed item(s) and pre-fill the min/max range
  with `seed_bpm ± 8` or so. Reuses the existing pipeline; user no longer
  has to guess.

- [ ] **Tag/genre filter as an alternative to BPM**  
  bc-explorer filters by bandcamp tags (no mp3 download, just one cheap
  HTML fetch per candidate). Much faster than BPM. Could be a complement
  ("must include tag 'techno'") or an alternative ("filter by tag instead
  of BPM"). Cheapest user-facing speedup.

- [ ] **Hide tracks the user already owns**  
  Once we have the profile-paste feature, also pull the user's collection
  and filter recommendations against it. Nothing more annoying than being
  recommended what you already bought.

- [ ] **Share a set via short URL**  
  Encode the seeds + filters in a URL so a crafted set is reproducible and
  shareable. Useful for "look at this set I built" moments — pairs nicely
  with the embedded previews already on the page.

## Reference

- Algorithm: `src/set_crafter/recommend_tracks.py` (supporter sampling, BPM
  filter loop)
- BPM extraction: `src/set_crafter/analyze_bpm.py` (process pool, embed
  page → mp3 → librosa)
- Frontend: `web/src/components/Crafter.astro` + `web/src/lib/api.ts`
