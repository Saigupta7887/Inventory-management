import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { IconGuide, IconCheck, IconX, IconPin, IconPlay } from '../icons'

const EXAMPLES = ['Change my car tire', 'Hang a picture frame', 'Fix a leaky faucet', 'Assemble flat-pack furniture']

export default function Guide() {
  const [task, setTask] = useState('')
  const [plan, setPlan] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function run(e, preset) {
    if (e) e.preventDefault()
    const t = preset || task
    if (!t.trim()) return
    if (preset) setTask(preset)
    setBusy(true); setError('')
    try {
      const r = await api.post('/tasks/plan', { task: t })
      setPlan(r)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <h2 className="page-h"><span className="page-ic"><IconGuide width={22} height={22} /></span> How do I…?</h2>
      <p className="muted">Describe a job. We'll list the tools it needs, check what you already own, and show you how.</p>

      <form onSubmit={run} className="search-bar">
        <input placeholder="e.g. change my car tire" value={task} onChange={(e) => setTask(e.target.value)} autoFocus />
        <button className="btn primary" disabled={busy}>{busy ? 'Thinking…' : 'Show me how'}</button>
      </form>

      {!plan && (
        <div className="examples">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="chip" onClick={() => run(null, ex)}>{ex}</button>
          ))}
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {plan && (
        <div className="guide">
          <div className={`verdict ${plan.ready ? 'buy' : 'owned'}`}>
            <span className="verdict-ic">{plan.ready ? <IconCheck width={26} height={26} /> : <IconX width={26} height={26} />}</span>
            <div>
              <div className="verdict-title">{plan.ready ? "You've got what you need" : `You're missing ${plan.missing_essential} essential tool${plan.missing_essential === 1 ? '' : 's'}`}</div>
              <div className="verdict-msg">
                {plan.ready
                  ? `You own the essential tools for “${plan.title}”. Follow the steps below.`
                  : `Grab the missing essentials (or use the Find page to double-check) before you start.`}
              </div>
            </div>
          </div>

          <div className="guide-grid">
            <section className="card">
              <h3>Tools you'll need</h3>
              <ul className="tool-need">
                {plan.tools.map((t, i) => (
                  <li key={i} className={t.owned ? 'have' : 'missing'}>
                    <span className={`need-ic ${t.owned ? 'ok' : 'no'}`}>
                      {t.owned ? <IconCheck width={15} height={15} /> : <IconX width={15} height={15} />}
                    </span>
                    <div className="need-main">
                      <div className="need-name">
                        {t.name}
                        {t.essential && <span className="req">required</span>}
                      </div>
                      <div className="need-sub">
                        {t.owned
                          ? <span className="have-loc"><IconPin width={12} height={12} /> {t.location_name || 'In your inventory'}</span>
                          : <span className="muted">Not in your inventory</span>}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
              {!plan.ready && <Link to="/search" className="btn ghost sm">Check the Find page</Link>}
            </section>

            <section className="card">
              <h3>Step by step</h3>
              <ol className="steps">
                {plan.steps.map((s, i) => <li key={i}>{s}</li>)}
              </ol>
              {plan.safety?.length > 0 && (
                <div className="safety">
                  <div className="safety-h">Safety</div>
                  <ul>{plan.safety.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
              )}
              <a className="btn primary video-btn" href={plan.video_url} target="_blank" rel="noreferrer">
                <IconPlay width={18} height={18} /> Watch a how-to video
              </a>
            </section>
          </div>
        </div>
      )}
    </div>
  )
}
