import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, photoUrl } from '../api'

export default function Scan() {
  const [locations, setLocations] = useState([])
  const [locationId, setLocationId] = useState('')
  const [photo, setPhoto] = useState(null)
  const [detections, setDetections] = useState([])
  const [selected, setSelected] = useState({})
  const [step, setStep] = useState('upload') // upload | detecting | review | done
  const [error, setError] = useState('')
  const [hovered, setHovered] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/locations').then(setLocations).catch(() => {})
  }, [])

  async function onFile(e) {
    const file = e.target.files[0]
    if (!file) return
    setError('')
    try {
      const form = new FormData()
      form.append('file', file)
      if (locationId) form.append('location_id', locationId)
      const p = await api.upload('/photos', form)
      setPhoto(p)
      setStep('detecting')
      const dets = await api.post(`/photos/${p.id}/detect`)
      setDetections(dets)
      const sel = {}
      dets.forEach((d) => (sel[d.id] = true))
      setSelected(sel)
      setStep('review')
    } catch (err) {
      setError(err.message)
      setStep('upload')
    }
  }

  async function accept() {
    const ids = Object.keys(selected).filter((id) => selected[id])
    if (!ids.length) return
    try {
      await api.post(`/photos/${photo.id}/accept`, { detection_ids: ids, location_id: locationId || null })
      setStep('done')
    } catch (err) {
      setError(err.message)
    }
  }

  function reset() {
    setPhoto(null); setDetections([]); setSelected({}); setStep('upload'); setError('')
  }

  return (
    <div>
      <h2>📷 Scan a location</h2>
      <p className="muted">Upload a photo of a desk, drawer, shelf or pegboard. AI detects the tools; you confirm which to add.</p>

      <div className="row">
        <label className="field">
          <span>Location (optional)</span>
          <select value={locationId} onChange={(e) => setLocationId(e.target.value)}>
            <option value="">— Unassigned —</option>
            {locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </label>
      </div>

      {error && <div className="error">{error}</div>}

      {step === 'upload' && (
        <label className="dropzone">
          <input type="file" accept="image/*" onChange={onFile} hidden />
          <div className="dz-inner">
            <div className="dz-icon">🖼️</div>
            <div>Click to choose a photo</div>
            <div className="muted small">JPG, PNG or WebP</div>
          </div>
        </label>
      )}

      {step === 'detecting' && <div className="card center">🔎 Detecting tools…</div>}

      {(step === 'review' || step === 'done') && photo && (
        <div className="scan-grid">
          <div className="photo-frame">
            <img src={photoUrl(photo.id)} alt="uploaded" />
            {detections.map((d) => d.bbox && (
              <div
                key={d.id}
                className={`bbox ${hovered === d.id ? 'hi' : ''} ${selected[d.id] ? '' : 'dim'}`}
                style={{
                  left: `${d.bbox.x * 100}%`, top: `${d.bbox.y * 100}%`,
                  width: `${d.bbox.w * 100}%`, height: `${d.bbox.h * 100}%`,
                }}
              ><span>{d.label}</span></div>
            ))}
          </div>

          <div>
            {step === 'review' ? (
              <>
                <h3>Detected tools ({detections.length})</h3>
                <div className="det-list">
                  {detections.map((d) => (
                    <label key={d.id} className="det-item" onMouseEnter={() => setHovered(d.id)} onMouseLeave={() => setHovered(null)}>
                      <input type="checkbox" checked={!!selected[d.id]} onChange={(e) => setSelected({ ...selected, [d.id]: e.target.checked })} />
                      <div className="det-main">
                        <div className="det-label">{d.label}</div>
                        <div className="muted small">{d.suggested_category} · {(d.confidence * 100).toFixed(0)}% confident</div>
                      </div>
                    </label>
                  ))}
                </div>
                <button className="btn primary" onClick={accept}>Add selected to inventory</button>
                <button className="btn ghost" onClick={reset}>Cancel</button>
              </>
            ) : (
              <div className="card center">
                <div className="dz-icon">✅</div>
                <h3>Added to your inventory!</h3>
                <button className="btn primary" onClick={() => navigate('/items')}>View items</button>
                <button className="btn ghost" onClick={reset}>Scan another</button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
