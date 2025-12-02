export const baseRiskPercentage = 48;

export const horizonForecast = [
  { id: 1, dayLabel: 'Mon', date: 'Apr 01', risk: 24, humidity: 58, temperature: 32, solar: 7.1, wind: 9, narrative: 'Cool breeze keeps mealybugs sluggish.' },
  { id: 2, dayLabel: 'Tue', date: 'Apr 02', risk: 28, humidity: 61, temperature: 33, solar: 7.4, wind: 11, narrative: 'Morning dew present, monitor lower canopy.' },
  { id: 3, dayLabel: 'Wed', date: 'Apr 03', risk: 36, humidity: 64, temperature: 34, solar: 7.8, wind: 8, narrative: 'Humidity rising under bright skies.' },
  { id: 4, dayLabel: 'Thu', date: 'Apr 04', risk: 52, humidity: 70, temperature: 34, solar: 8.2, wind: 6, narrative: 'Sticky afternoons favor crawlers.' },
  { id: 5, dayLabel: 'Fri', date: 'Apr 05', risk: 63, humidity: 74, temperature: 35, solar: 8.6, wind: 5, narrative: 'Still air over warm clay beds.' },
  { id: 6, dayLabel: 'Sat', date: 'Apr 06', risk: 76, humidity: 78, temperature: 35, solar: 9.0, wind: 4, narrative: 'Perfect bloom for mealybug colonies.' },
  { id: 7, dayLabel: 'Sun', date: 'Apr 07', risk: 84, humidity: 82, temperature: 36, solar: 9.2, wind: 3, narrative: 'Hot sun plus trapped humidity — treat blocks.' },
  { id: 8, dayLabel: 'Mon', date: 'Apr 08', risk: 71, humidity: 79, temperature: 35, solar: 8.7, wind: 5, narrative: 'Risk easing but scouting mandatory.' },
  { id: 9, dayLabel: 'Tue', date: 'Apr 09', risk: 58, humidity: 73, temperature: 33, solar: 7.9, wind: 7, narrative: 'Cloud breaks bring partial relief.' },
  { id: 10, dayLabel: 'Wed', date: 'Apr 10', risk: 41, humidity: 66, temperature: 32, solar: 7.1, wind: 10, narrative: 'Breeze dries canopy tips.' },
  { id: 11, dayLabel: 'Thu', date: 'Apr 11', risk: 29, humidity: 60, temperature: 31, solar: 6.8, wind: 12, narrative: 'Safe window for hygiene sprays.' },
  { id: 12, dayLabel: 'Fri', date: 'Apr 12', risk: 23, humidity: 57, temperature: 30, solar: 6.2, wind: 14, narrative: 'Cool winds flush pests out.' },
  { id: 13, dayLabel: 'Sat', date: 'Apr 13', risk: 18, humidity: 55, temperature: 29, solar: 5.8, wind: 16, narrative: 'Soil breathing easy.' },
  { id: 14, dayLabel: 'Sun', date: 'Apr 14', risk: 33, humidity: 59, temperature: 31, solar: 6.5, wind: 12, narrative: 'Watch regrowth tips for hot spots.' },
];

export const soilProfiles = [
  {
    id: 'sandy',
    textureClass: 'soil-chip--sandy',
    clay: '12%',
    modifier: -10,
    labelKey: 'controls.soil.sandy',
    descriptionKey: 'controls.soil.sandyDesc',
  },
  {
    id: 'loam',
    textureClass: 'soil-chip--loam',
    clay: '28%',
    modifier: 0,
    labelKey: 'controls.soil.loam',
    descriptionKey: 'controls.soil.loamDesc',
  },
  {
    id: 'clay',
    textureClass: 'soil-chip--clay',
    clay: '48%',
    modifier: 8,
    labelKey: 'controls.soil.clay',
    descriptionKey: 'controls.soil.clayDesc',
  },
];

export const moistureProfiles = [
  {
    id: 'dry',
    modifier: 6,
    accent: 'from-amber-200/80 via-alertOrange/70 to-burntOchre/60',
    labelKey: 'controls.moisture.dry',
    descriptionKey: 'controls.moisture.dryDesc',
  },
  {
    id: 'balance',
    modifier: 0,
    accent: 'from-leaf/80 via-chlorophyll/70 to-loam/70',
    labelKey: 'controls.moisture.balance',
    descriptionKey: 'controls.moisture.balanceDesc',
  },
  {
    id: 'wet',
    modifier: 9,
    accent: 'from-blue-200/70 via-alertOrange/60 to-burntOchre/80',
    labelKey: 'controls.moisture.wet',
    descriptionKey: 'controls.moisture.wetDesc',
  },
];
