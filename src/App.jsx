import { Droplets, SunMedium, ThermometerSun } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import ActionCards from './components/ActionCards.jsx';
import Controls from './components/Controls.jsx';
import Horizon from './components/Horizon.jsx';
import LanguageToggle from './components/LanguageToggle.jsx';
import LivingTree from './components/Tree.jsx';
import { useRisk } from './context/RiskContext.jsx';

const App = () => {
  const { t } = useTranslation();
  const { risk, riskState, forecast } = useRisk();
  const today = forecast[0];

  const summaryChips = [
    { label: t('hero.humidity'), value: today ? `${today.humidity}%` : '—', icon: Droplets },
    { label: t('hero.temperature'), value: today ? `${today.temperature}°C` : '—', icon: ThermometerSun },
    { label: t('hero.solar'), value: today ? `${today.solar} MJ/m²` : '—', icon: SunMedium },
  ];

  return (
    <div className="min-h-screen pb-16">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-10">
        <header className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.45em] text-white/70">{t('app.kicker')}</p>
            <h1 className="mt-2 font-serif text-4xl text-parchment sm:text-5xl">{t('app.title')}</h1>
            <p className="mt-2 max-w-xl text-lg text-white/80">{t('app.subtitle')}</p>
            <p className="mt-2 text-sm text-white/60">{t('app.lastUpdated')}</p>
            <span className="mt-3 inline-flex items-center rounded-full bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-leaf/80">
              {t('app.locationTag')}
            </span>
          </div>
          <LanguageToggle />
        </header>

        <section className="mt-6 grid gap-6 lg:grid-cols-[1.2fr,0.8fr]">
          <LivingTree />
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-6 text-white">
            <p className="text-xs uppercase tracking-[0.4em] text-white/70">{t('app.fieldPulse')}</p>
            <div className="mt-2 flex items-end gap-3">
              <span className="text-5xl font-numeric">{Math.round(risk)}%</span>
              <span className="text-leaf text-xl font-semibold">{t(`hero.pressureStates.${riskState}`)}</span>
            </div>
            <p className="text-sm text-white/60">{t('app.stateLabel')}</p>
            <div className="mt-5 grid gap-3">
              {summaryChips.map(({ label, value, icon: Icon }) => (
                <div key={label} className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/30 px-4 py-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-white/60">{label}</p>
                    <p className="text-lg font-semibold">{value}</p>
                  </div>
                  <Icon className="h-8 w-8 text-parchment" />
                </div>
              ))}
            </div>
          </div>
        </section>

        <div className="mt-8 space-y-8">
          <Horizon />
          <Controls />
          <ActionCards />
        </div>
      </div>
    </div>
  );
};

export default App;
