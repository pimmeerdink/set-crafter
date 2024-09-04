import React, { useState } from 'react';

const BandcampWidget = ({ id, type }) => (
  <iframe
    style={{ border: 0, width: '200px', height: '200px', marginBottom: '10px', marginRight: '10px' }}
    src={`https://bandcamp.com/EmbeddedPlayer/${type}=${id}/size=large/bgcol=ffffff/linkcol=0687f5/tracklist=false/transparent=true/`}
    seamless
  >
    <a href={`https://bandcamp.com/${type}/${id}`}>View on Bandcamp</a>
  </iframe>
);

const SetlistCreator = () => {
  const [newTrackUrl, setNewTrackUrl] = useState('');
  const [setlist, setSetlist] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [minBpm, setMinBpm] = useState(120);
  const [maxBpm, setMaxBpm] = useState(140);
  const [filterBpm, setFilterBpm] = useState(true);
  const [sortBy, setSortBy] = useState('relevance');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const getBandcampId = async (url) => {
    const response = await fetch('http://127.0.0.1:8000/get-bandcamp-id', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    if (!response.ok) throw new Error('Failed to get Bandcamp ID');
    return await response.json();
  };

  const addTrack = async (url) => {
    if (url.trim()) {
      try {
        const item = await getBandcampId(url.trim());
        setSetlist([...setlist, item]);
        setNewTrackUrl('');
      } catch (error) {
        setError('Failed to add track. Please check the URL and try again.');
      }
    }
  };

  const addTrackFromRecommendation = (rec) => {
    setSetlist([...setlist, rec]);
  };

  const removeTrack = (index) => {
    const newSetlist = setlist.filter((_, i) => i !== index);
    setSetlist(newSetlist);
  };

  const generateRecommendations = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8000/generate-recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          set_input: { items: setlist },
          bpm_range: { min: minBpm, max: maxBpm },
          filter_bpm: filterBpm,
          sort_by: sortBy
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate recommendations');
      }

      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Error generating recommendations:', error);
      setError(error.message || 'Failed to generate recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ fontSize: '24px', marginBottom: '20px', color: '#333' }}>Setlist Creator</h1>

      <div style={{ display: 'flex', marginBottom: '20px' }}>
        <div style={{ flex: 1, marginRight: '20px' }}>
          <input
            type="text"
            value={newTrackUrl}
            onChange={(e) => setNewTrackUrl(e.target.value)}
            placeholder="Enter Bandcamp track or album URL"
            style={{ width: '100%', padding: '10px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
          <button
            onClick={() => addTrack(newTrackUrl)}
            style={{ padding: '10px 20px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Add to Setlist
          </button>
        </div>

        <div style={{ flex: 1 }}>
          <input
            type="number"
            value={minBpm}
            onChange={(e) => setMinBpm(parseInt(e.target.value))}
            placeholder="Min BPM"
            style={{ width: '80px', padding: '10px', marginRight: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
          <input
            type="number"
            value={maxBpm}
            onChange={(e) => setMaxBpm(parseInt(e.target.value))}
            placeholder="Max BPM"
            style={{ width: '80px', padding: '10px', marginRight: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          />
          <div style={{ marginTop: '10px' }}>
            <label>
              <input
                type="checkbox"
                checked={filterBpm}
                onChange={(e) => setFilterBpm(e.target.checked)}
                style={{ marginRight: '5px' }}
              />
              Filter by BPM
            </label>
          </div>
          <div style={{ marginTop: '10px' }}>
            <label>
              Sort by:
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{ marginLeft: '5px', padding: '5px' }}
              >
                <option value="relevance">Relevance</option>
                  <option value="popularity">Popularity</option>
                <option value="random">Random</option>
              </select>
            </label>
          </div>
          <button
            onClick={generateRecommendations}
            style={{ padding: '10px 20px', backgroundColor: '#008CBA', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' }}
          >
            Generate Recommendations
          </button>
        </div>
      </div>

      <div style={{ display: 'flex' }}>
        <div style={{ flex: 1, marginRight: '20px' }}>
          <h2 style={{ fontSize: '20px', marginBottom: '10px', color: '#333' }}>Your Setlist:</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {setlist.map((item, index) => (
              <div key={index} style={{ marginBottom: '20px', position: 'relative' }}>
                <BandcampWidget id={item.id} type={item.type} />
                <button
                  onClick={() => removeTrack(index)}
                  style={{
                    position: 'absolute',
                    top: '5px',
                    right: '15px',
                    padding: '5px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    cursor: 'pointer',
                    width: '20px',
                    height: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px'
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: '20px', marginBottom: '10px', color: '#333' }}>Recommendations:</h2>
          {isLoading && <p>Loading recommendations...</p>}
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {recommendations.map((rec, index) => (
              <div key={index} style={{ marginBottom: '20px', position: 'relative' }}>
                <BandcampWidget id={rec.id} type={rec.type} />
                <button
                  onClick={() => addTrackFromRecommendation(rec)}
                  style={{
                    position: 'absolute',
                    bottom: '15px',
                    right: '15px',
                    padding: '5px 10px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px'
                  }}
                >
                  Add to Setlist
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SetlistCreator;
