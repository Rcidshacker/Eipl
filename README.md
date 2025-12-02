# Sitaphal Sentinel Mobile UI

A tactile, farmer-first React experience that visualizes custard apple (sitaphal) mealybug pressure using a living tree metaphor. The interface embraces earthy textures, large touch targets, and bilingual (English/Marathi) support to serve growers across devices.

## Tech Stack

- [React 18](https://react.dev/) + [Vite](https://vitejs.dev/)
- Tailwind CSS with a custom "Tactile Ecology" palette and font stack (Bitter + Nunito Sans)
- [Framer Motion](https://www.framer.com/motion/) for smooth morphing animations
- [lucide-react](https://lucide.dev/) iconography
- `react-i18next` for bilingual text with persistence in `localStorage`

## Getting Started

> Node.js 18+ and npm are recommended.

```bash
cd /home/engine/project
npm install
npm run dev        # start the Vite dev server
npm run build      # production build
npm run preview    # preview the production build
```

The React source lives in `/src`, alongside `index.html`, `tailwind.config.cjs`, and supporting config files.

## Project Structure

```
project/
├── index.html
├── package.json
├── postcss.config.js
├── tailwind.config.cjs
├── vite.config.js
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   ├── data/mockData.js
│   ├── context/RiskContext.jsx
│   ├── i18n/
│   │   ├── index.js
│   │   └── locales/{en,mr}.json
│   └── components/
│       ├── Tree.jsx
│       ├── Horizon.jsx
│       ├── Controls.jsx
│       ├── ActionCards.jsx
│       └── LanguageToggle.jsx
└── README.md
```

## Core Experience

| Component | Purpose |
| --- | --- |
| `Tree.jsx` | 3D-inspired custard apple tree SVG that morphs across low/medium/high risk states. Tap to reveal "why" signals (heat, humidity, canopy shelter). |
| `Horizon.jsx` | 14-day, touch-scrollable terrain timeline. Smooth plains represent safe days; jagged ridges highlight risky windows with tooltips. |
| `Controls.jsx` | Soil texture selector, moisture dial, and live "sky telemetry" metrics. Adjusting controls recalculates the risk state instantly. |
| `ActionCards.jsx` | Context-aware advisory deck with chunky, icon-led guidance tailored to the current risk band. |
| `LanguageToggle.jsx` | English ↔ Marathi toggle with persisted preference. |

The shared `RiskContext` wires mock forecast data, soil/moisture modifiers, and derived risk percentages so every component stays in sync.

## Design System Highlights

- **Palette:** Deep chlorophyll greens (#0F3B1D, #1C7C4D), loam browns (#8B7355), slate greys, burnt ochre + alert orange highlights.
- **Typography:** Bitter (serif) for headings, Nunito Sans + Barlow Condensed for data glyphs.
- **Texture:** Custom parchment/slate noise backgrounds and chunky drop shadows for tactile depth.
- **Accessibility:** 44px+ touch targets, high-contrast cards, and bilingual content.

## Extending Toward Live Data

- Replace the static `horizonForecast` in `src/data/mockData.js` with XGBoost outputs or API payloads.
- Update `RiskContext` to call backend endpoints and feed the response into the provider state.
- Hook farmer-specific soil profiles or weather stations into the control panel for personalized tuning.

Enjoy exploring the Sitaphal Sentinel interface!