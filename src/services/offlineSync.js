// Lightweight offline-first sync layer.
//
// AnnaDATA needs to work in low-connectivity rural areas: farmer feedback
// and field snapshots are written to localStorage immediately, then
// "synced" (flushed) whenever the browser regains connectivity. This is a
// client-only simulation of that queue — swap `syncOne` for a real API
// call when a backend is wired up.

const QUEUE_KEY = 'annadata:sync-queue'
const CACHE_KEY = 'annadata:field-cache'

function readQueue() {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY)) || []
  } catch {
    return []
  }
}

function writeQueue(queue) {
  localStorage.setItem(QUEUE_KEY, JSON.stringify(queue))
}

export function isOnline() {
  return typeof navigator === 'undefined' ? true : navigator.onLine
}

// Queue any action (feedback, a field snapshot, etc). Returns the queued
// record, including whether it was synced immediately or parked for later.
export function queueAction(type, payload) {
  const record = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    type,
    payload,
    queuedAt: new Date().toISOString(),
    synced: false,
  }

  if (isOnline()) {
    // In a real deployment this would POST to the backend here.
    record.synced = true
    record.syncedAt = new Date().toISOString()
  } else {
    const queue = readQueue()
    queue.push(record)
    writeQueue(queue)
  }

  return record
}

// Call this on an 'online' event (see useOfflineSync hook) to flush
// anything queued while the device had no connectivity.
export function flushQueue() {
  const queue = readQueue()
  if (queue.length === 0) return []

  const synced = queue.map((r) => ({
    ...r,
    synced: true,
    syncedAt: new Date().toISOString(),
  }))
  writeQueue([])
  return synced
}

export function pendingCount() {
  return readQueue().length
}

// Cache the last successfully fetched field snapshot (weather + soil + AI
// recs) per coordinate, so the app has something to show if the network
// drops after the first sync.
export function cacheFieldSnapshot(key, snapshot) {
  try {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY)) || {}
    cache[key] = { snapshot, cachedAt: new Date().toISOString() }
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache))
  } catch {
    // storage full or unavailable — non-fatal, just skip caching
  }
}

export function getCachedFieldSnapshot(key) {
  try {
    const cache = JSON.parse(localStorage.getItem(CACHE_KEY)) || {}
    return cache[key]?.snapshot || null
  } catch {
    return null
  }
}

export function feedbackKey(lat, lng) {
  return `${lat.toFixed(3)},${lng.toFixed(3)}`
}

export function getFeedbackForField(lat, lng) {
  const key = feedbackKey(lat, lng)
  return readQueue()
    .filter((r) => r.type === 'feedback' && r.payload.fieldKey === key)
    .concat(
      JSON.parse(localStorage.getItem('annadata:synced-feedback') || '[]').filter(
        (r) => r.payload.fieldKey === key
      )
    )
}

export function persistSyncedFeedback(record) {
  const list = JSON.parse(localStorage.getItem('annadata:synced-feedback') || '[]')
  list.push(record)
  localStorage.setItem('annadata:synced-feedback', JSON.stringify(list.slice(-50)))
}
