// Build deep links that hand off to the phone's messaging / dialer apps,
// pre-filled with a message. No app can send silently — these open the
// relevant app with the draft ready for the user to send.

function digits(phone, keepPlus = true) {
  if (!phone) return ''
  const cleaned = phone.replace(/[^\d+]/g, '')
  return keepPlus ? cleaned : cleaned.replace(/\D/g, '')
}

export function whatsappLink(phone, text) {
  // wa.me needs the number in international format without + or symbols.
  const n = digits(phone, false)
  return `https://wa.me/${n}?text=${encodeURIComponent(text || '')}`
}

export function smsLink(phone, text) {
  // `?&body=` is the most cross-platform (iOS + Android) form.
  return `sms:${digits(phone)}?&body=${encodeURIComponent(text || '')}`
}

export function emailLink(email, subject, body) {
  const params = []
  if (subject) params.push(`subject=${encodeURIComponent(subject)}`)
  if (body) params.push(`body=${encodeURIComponent(body)}`)
  return `mailto:${email || ''}${params.length ? '?' + params.join('&') : ''}`
}

export function telLink(phone) {
  return `tel:${digits(phone)}`
}

// Available channels for a person given the data we hold.
export function channelsFor(person) {
  const out = []
  if (person.phone) {
    out.push({ key: 'whatsapp', label: 'WhatsApp', icon: '🟢' })
    out.push({ key: 'sms', label: 'Text', icon: '💬' })
    out.push({ key: 'call', label: 'Call', icon: '📞' })
  }
  if (person.email) out.push({ key: 'email', label: 'Email', icon: '✉️' })
  return out
}

export function linkFor(channel, person, text) {
  switch (channel) {
    case 'whatsapp': return whatsappLink(person.phone, text)
    case 'sms': return smsLink(person.phone, text)
    case 'email': return emailLink(person.email, `Hey ${person.name.split(' ')[0]}`, text)
    case 'call': return telLink(person.phone)
    default: return '#'
  }
}
