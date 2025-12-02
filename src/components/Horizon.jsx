import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Droplets, SunMedium, ThermometerSun, Wind } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useRisk } from '../context/RiskContext.jsx';

const Horizon = () => {
  const { forecast } = useRisk();
  const { t } = useTranslation();
  const [activeDay, setActiveDay] = useState(forecast[0]);

  return (
    <section className="rounded-[32px] border border-white/10 bg-white/5 p-6 text-white">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-white/70">{t('horizon.title')}</p>
          <p className="text-sm text-white/70">{t('horizon.subtitle')}</p>
        </div>
        {activeDay && (
          <div className="text-sm text-leaf">
            {t('horizon.riskCallout', { day: activeDay.date, risk: activeDay.risk })}
          </div>
        )}
      </div>

      <div className="terrain-track no-scrollbar mt-4 flex gap-4 overflow-x-auto py-3">
        {forecast.map((day) => {
          const risky = day.risk >= 55;
          return (
            <button
              key={day.id}
              type="button"
              onClick={() => setActiveDay(day)}
              onMouseEnter={() => setActiveDay(day)}
              className={`terrain-card px-4 pb-4 pt-5 text-left transition-transform focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-parchment ${
                activeDay?.id === day.id ? 'scale-105' : 'scale-100'
              } ${risky ? 'terrain-card--ridge' : 'terrain-card--calm'}`}
              aria-label={t('horizon.riskCallout', { day: day.date, risk: day.risk })}
            >
              <div className={`terrain-wave ${risky ? 'terrain-wave--ridge' : 'terrain-wave--calm'}`} />
              <div className="relative z-10 flex flex-col gap-1">
                <span className="text-xs uppercase tracking-[0.25em] text-white/70">{day.dayLabel}</span>
                <span className="text-3xl font-numeric">{day.risk}%</span>
                <p className="text-xs text-white/80">{day.narrative}</p>
              </div>
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {activeDay && (
          <motion.div
            key={activeDay.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-6 grid gap-4 rounded-3xl border border-white/10 bg-black/30 p-4 sm:grid-cols-4"
          >
            <MetricCard icon={Droplets} label={t('horizon.metrics.humidity')} value={`${activeDay.humidity}%`} />
            <MetricCard icon={ThermometerSun} label={t('horizon.metrics.temperature')} value={`${activeDay.temperature}°C`} />
            <MetricCard icon={SunMedium} label={t('horizon.metrics.solar')} value={`${activeDay.solar} MJ/m²`} subtle />
            <MetricCard icon={Wind} label={t('horizon.metrics.wind')} value={`${activeDay.wind} km/h`} />
          </motion.div>
        )}
      </AnimatePresence>

      {activeDay && (
        <p className="mt-3 text-sm text-white/70">{t('horizon.activeNarrative', { note: activeDay.narrative })}</p>
      )}
    </section>
  );
};

const MetricCard = ({ icon: Icon, label, value, subtle = false }) => (
  <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
    <Icon className={`h-5 w-5 ${subtle ? 'text-alertOrange/70' : 'text-parchment'}`} />
    <p className="mt-2 text-xs uppercase tracking-[0.25em] text-white/60">{label}</p>
    <p className="text-xl font-semibold">{value}</p>
  </div>
);

export default Horizon;
