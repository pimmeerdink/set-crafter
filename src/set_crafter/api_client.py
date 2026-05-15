import requests
import json


def get_track_recommendations(track_urls, min_bpm, max_bpm):
    # API endpoint URL
    url = "http://localhost:8000/generate-recommendations"

    # Prepare the payload
    payload = {
        "tracks": [{"url": url} for url in track_urls],
        "min_bpm": min_bpm,
        "max_bpm": max_bpm,
    }

    # Make the POST request
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        recommendations = response.json()
        return recommendations
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# Example usage
if __name__ == "__main__":
    # Example track URLs
    track_urls = [
        "https://lowincomesquad.bandcamp.com/track/siu-mata-psyro",
        "https://jerryhorny.bandcamp.com/track/business-visa",
    ]

    # Example BPM range
    min_bpm = 100
    max_bpm = 160

    # Get recommendations
    recommendations = get_track_recommendations(track_urls, min_bpm, max_bpm)
    if recommendations:
        print("Track Recommendations:")
        for i, track in enumerate(recommendations, 1):
            print(track)
