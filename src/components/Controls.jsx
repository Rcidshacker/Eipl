import { Droplets, GaugeCircle, SunMedium, ThermometerSun, Wind } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useRisk } from '../context/RiskContext.jsx';

const Controls = () => {
  const { soil, setSoil, moisture, setMoisture, soilProfiles, moistureProfiles, forecast } = useRisk();
  const { t } = useTranslation();
  const today = forecast[0];

  const environmentMetrics = [
    {
      icon: Droplets,
      label: t('controls.environment.humidity'),
      value: today ? `${today.humidity}%` : '—',
    },
    {
      icon: ThermometerSun,
      label: t('controls.environment.temperature'),
      value: today ? `${today.temperature}°C` : '—',
    },
    {
      icon: SunMedium,
      label: t('controls.environment.solar'),
      value: today ? `${today.solar} MJ/m²` : '—',
    },
    {
      icon: Wind,
      label: t('controls.environment.wind'),
      value: today ? `${today.wind} km/h` : '—',
    },
  ];

  return (
    <section className="rounded-[32px] border border-white/10 bg-white/[0.04] p-6 text-white">
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-white/70">{t('controls.title')}</p>
        <p className="text-sm text-white/70">{t('controls.subtitle')}</p>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/60">{t('controls.soil.title')}</p>
          <div className="mt-3 grid gap-4 md:grid-cols-3">
            {soilProfiles.map((profile) => (
              <button
                key={profile.id}
                type="button"
                className={`soil-chip px-4 py-4 text-left text-white transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-parchment ${
                  profile.textureClass
                } ${soil === profile.id ? 'ring-4 ring-parchment/60' : 'ring-2 ring-white/10'}`}
                onClick={() => setSoil(profile.id)}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-base font-semibold">{t(profile.labelKey)}</p>
                  <span className="rounded-full bg-black/30 px-3 py-1 text-xs font-semibold">{profile.clay}</span>
                </div>
                <p className="mt-3 text-sm text-white/80">{t(profile.descriptionKey)}</p>
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/60">{t('controls.moisture.title')}</p>
          <div className="moisture-dial mt-3 flex flex-wrap gap-4">
            {moistureProfiles.map((profile) => (
              <button
                key={profile.id}
                type="button"
                onClick={() => setMoisture(profile.id)}
                className={`flex flex-1 min-w-[120px] items-center justify-center gap-2 rounded-full bg-gradient-to-b px-4 py-4 text-left text-sm font-semibold text-chlorophyll shadow-slab transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-parchment ${
                  profile.accent
                } ${moisture === profile.id ? 'ring-4 ring-parchment/70' : 'ring-2 ring-white/20'}`}
              >
                <GaugeCircle className="h-6 w-6" />
                <div>
                  <p className="text-base">{t(profile.labelKey)}</p>
                  <p className="text-xs text-chlorophyll/80">{t(profile.descriptionKey)}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {environmentMetrics.map(({ icon: Icon, label, value }) => (
          <div key={label} className="rounded-2xl border border-white/10 bg-black/30 p-4">
            <Icon className="h-6 w-6 text-parchment" />
            <p className="mt-2 text-xs uppercase tracking-[0.3em] text-white/60">{label}</p>
            <p className="text-xl font-semibold">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Controls;
