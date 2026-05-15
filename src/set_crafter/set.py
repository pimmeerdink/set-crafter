from .recommend_tracks import get_recommendations


class Set:
    def __init__(self, tracks, bpmrange):
        self.tracks = tracks
        self.bpmrange = bpmrange

    def generate_track_recommendations(self, filter_bpm, nof_recs, sort_by):
        return get_recommendations(
            self.tracks, self.bpmrange, 15, nof_recs, filter_bpm, sort_by
        )
