import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Droplets, Shield, SunMedium } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useRisk } from '../context/RiskContext.jsx';

const backgroundPalette = {
  low: '#103c1e',
  medium: '#5c3b1f',
  high: '#4d2c1a',
};

const canopyVariants = {
  low: { scale: 1.08, fill: '#2fb46b' },
  medium: { scale: 1.02, fill: '#d2d970' },
  high: { scale: 0.95, fill: '#f0f0e3' },
};

const hazeVariants = {
  low: { opacity: 0.12, backgroundColor: 'rgba(47, 180, 107, 0.25)' },
  medium: { opacity: 0.4, backgroundColor: 'rgba(234, 180, 65, 0.4)' },
  high: { opacity: 0.65, backgroundColor: 'rgba(232, 106, 51, 0.55)' },
};

const bugOpacity = {
  low: 0,
  medium: 0.4,
  high: 0.9,
};

const reasonMatrix = {
  low: ['sun'],
  medium: ['sun', 'humidity'],
  high: ['sun', 'humidity', 'shelter'],
};

const reasonIconMap = {
  sun: SunMedium,
  humidity: Droplets,
  shelter: Shield,
};

const LivingTree = () => {
  const { risk, riskState, soil, moisture, forecast, soilProfiles, moistureProfiles } = useRisk();
  const { t } = useTranslation();
  const [showReasons, setShowReasons] = useState(false);

  const today = forecast[0];
  const soilProfile = soilProfiles.find((profile) => profile.id === soil);
  const moistureProfile = moistureProfiles.find((profile) => profile.id === moisture);
  const reasonsToShow = reasonMatrix[riskState];

  return (
    <div className="relative overflow-hidden rounded-[32px] border border-white/10 p-6 text-white shadow-canopy texture-panel">
      <motion.div
        className="absolute inset-0"
        aria-hidden="true"
        animate={{ backgroundColor: backgroundPalette[riskState] }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      />
      <motion.div
        className="absolute inset-x-4 top-8 h-64 rounded-[50%] blur-2xl"
        animate={hazeVariants[riskState]}
        transition={{ duration: 0.8 }}
      />

      <div className="relative z-10 flex flex-col gap-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-white/70">{t('hero.livingTree')}</p>
            <div className="mt-2 flex items-end gap-3">
              <motion.span
                key={risk}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-6xl font-numeric leading-none"
              >
                {Math.round(risk)}%
              </motion.span>
              <span className="text-xl font-semibold text-parchment">{t(`hero.pressureStates.${riskState}`)}</span>
            </div>
            <p className="mt-1 text-sm text-white/70">{t('hero.tapPrompt')}</p>
          </div>
          <div className="rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-sm backdrop-blur">
            <p className="text-xs uppercase tracking-[0.25em] text-leaf/80">{t('hero.next48h')}</p>
            <p className="text-lg font-semibold">
              {today ? `${today.temperature}°C / ${today.humidity}%` : '—'}
            </p>
            <p className="text-xs text-white/70">{t('hero.conditionsLabel')}</p>
          </div>
        </div>

        <motion.svg
          viewBox="0 0 320 300"
          className="mx-auto h-[260px] w-full cursor-pointer"
          onClick={() => setShowReasons((prev) => !prev)}
        >
          <motion.rect
            x="140"
            y="150"
            width="40"
            height="110"
            rx="20"
            fill="#6c3f25"
            animate={{ y: riskState === 'high' ? 160 : 150 }}
            transition={{ type: 'spring', stiffness: 60, damping: 12 }}
          />
          <motion.circle
            cx="160"
            cy="140"
            r="90"
            variants={canopyVariants}
            animate={riskState}
          />
          {[...Array(9)].map((_, index) => (
            <motion.circle
              key={`fruit-${index}`}
              cx={90 + index * 20 - (index % 3) * 12}
              cy={200 - (index % 4) * 18}
              r={index % 2 === 0 ? 10 : 7}
              fill="#f5e2a0"
              animate={{ opacity: riskState === 'high' ? 0.15 : 0.85 }}
              transition={{ duration: 0.6 }}
            />
          ))}
          {[...Array(14)].map((_, index) => (
            <motion.circle
              key={`bug-${index}`}
              cx={100 + (index * 17) % 140}
              cy={80 + ((index * 13) % 90)}
              r={index % 3 === 0 ? 4 : 3}
              fill="#f9f9f7"
              animate={{ opacity: bugOpacity[riskState] }}
              transition={{ duration: 0.5 }}
            />
          ))}
        </motion.svg>

        <div className="grid gap-3 sm:grid-cols-2">
          <article className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-white/70">{t('hero.currentSoil')}</p>
            <p className="text-lg font-semibold">{soilProfile ? t(soilProfile.labelKey) : '—'}</p>
            <p className="text-sm text-white/70">{soilProfile?.clay} clay</p>
          </article>
          <article className="rounded-2xl border border-white/10 bg-white/10 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-white/70">{t('hero.currentMoisture')}</p>
            <p className="text-lg font-semibold">{moistureProfile ? t(moistureProfile.labelKey) : '—'}</p>
            <p className="text-sm text-white/70">{moistureProfile ? t(moistureProfile.descriptionKey) : ''}</p>
          </article>
        </div>
      </div>

      <AnimatePresence>
        {showReasons && (
          <motion.div
            className="absolute inset-0 z-20 bg-dusk/80 p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <div className="flex flex-col gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.3em] text-alertOrange">{t('hero.whyTitle')}</p>
                <p className="text-sm text-white/70">{t('hero.whySubtitle')}</p>
              </div>
              <div className="grid gap-3 sm:grid-cols-3">
                {reasonsToShow.map((reason) => {
                  const Icon = reasonIconMap[reason];
                  return (
                    <div key={reason} className="rounded-2xl bg-white/10 p-3">
                      <Icon className="h-6 w-6 text-alertOrange" />
                      <p className="mt-2 font-semibold">{t(`tree.factors.${reason}`)}</p>
                      <p className="text-sm text-white/70">{t(`tree.factors.${reason}Desc`)}</p>
                    </div>
                  );
                })}
              </div>
              <p className="text-xs text-white/70">{t('hero.tapToClose')}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default LivingTree;
