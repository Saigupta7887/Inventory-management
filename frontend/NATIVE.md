# Bondly on native iOS & Android (Capacitor)

Bondly ships as one Vue codebase that runs three ways:

1. **Responsive web** — desktop + mobile browser
2. **Installable PWA** — "Add to Home Screen" on any device (via `vite-plugin-pwa`)
3. **Native iOS / Android apps** — the same web build wrapped by **Capacitor**

This guide covers #3.

## Prerequisites

- Node 20+
- **iOS:** macOS + Xcode + CocoaPods, and an Apple Developer account to publish
- **Android:** Android Studio + JDK 17

## Point the app at your API

Native apps can't use Vite's dev proxy, so set the API base URL at build time:

```bash
# frontend/.env.production
VITE_API_BASE=https://api.yourdomain.com
VITE_GOOGLE_CLIENT_ID=...    # optional social login
VITE_APPLE_CLIENT_ID=...
```

## Add the platforms (one time)

```bash
cd frontend
npm install
npm run build            # produces dist/
npm run cap:add:ios      # creates ios/  (macOS only)
npm run cap:add:android  # creates android/
```

> The generated `ios/` and `android/` folders are native projects. Commit them
> if you want reproducible native builds, or keep them local and regenerate.

## Build & run

```bash
npm run cap:sync         # build web + copy into native projects
npm run cap:open:ios     # opens Xcode  -> Run
npm run cap:open:android # opens Android Studio -> Run
```

`cap:sync` re-runs on every web change; re-open the IDE to rebuild.

## Native social sign-in (recommended for the app stores)

The web Google/Apple flow (`src/lib/social.js`) works in the browser and PWA.
Inside a native webview, use the native plugins for a first-class experience and
to satisfy store review:

- **Apple:** `@capacitor-community/apple-sign-in`
- **Google:** `@codetrix-studio/capacitor-google-auth`

Both return an identity token you POST to the same backend endpoints
(`/api/auth/apple`, `/api/auth/google`) already implemented here — only the
token-acquisition step changes. Add a small platform check in `social.js`
(`Capacitor.isNativePlatform()`) to branch to the native plugin.

## App identity

- Bundle / application ID: `app.bondly.mobile` (see `capacitor.config.json`)
- App icon: generate from `public/icons/icon-512.png` with
  [`@capacitor/assets`](https://github.com/ionic-team/capacitor-assets):
  `npx @capacitor/assets generate`
