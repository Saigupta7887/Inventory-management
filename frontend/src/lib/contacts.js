// Import contacts from the device.
//
// Web: the Contact Picker API (navigator.contacts.select) — supported in
// Chrome/Edge on Android, not in iOS Safari or most desktops.
// Native (Capacitor): install @capacitor-community/contacts and branch here on
// Capacitor.isNativePlatform() for full access (see frontend/NATIVE.md).

export function contactsSupported() {
  return typeof navigator !== 'undefined' && 'contacts' in navigator && 'select' in navigator.contacts
}

/**
 * Opens the device contact picker and returns normalized contacts:
 *   [{ name, phone, email }]
 * Returns { supported:false } where the API is unavailable.
 */
export async function pickContacts() {
  if (!contactsSupported()) return { supported: false, contacts: [] }
  const selected = await navigator.contacts.select(['name', 'tel', 'email'], {
    multiple: true,
  })
  const contacts = selected.map((c) => ({
    name: (c.name && c.name[0]) || 'Unknown',
    phone: (c.tel && c.tel[0]) || null,
    email: (c.email && c.email[0]) || null,
  }))
  return { supported: true, contacts }
}
