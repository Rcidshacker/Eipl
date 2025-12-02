import { LifeBuoy, NotebookPen, Scissors, Search, ShieldHalf, SprayCan, Wand2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useRisk } from '../context/RiskContext.jsx';

const ACTION_MATRIX = {
  low: [
    { key: 'observe', icon: Search, tone: 'from-parchment to-loam/40' },
    { key: 'hygiene', icon: Wand2, tone: 'from-parchment to-leaf/30' },
    { key: 'log', icon: NotebookPen, tone: 'from-parchment to-slate/30' },
  ],
  medium: [
    { key: 'observe', icon: Search, tone: 'from-leaf/90 to-chlorophyll' },
    { key: 'prune', icon: Scissors, tone: 'from-loam/80 to-burntOchre/60' },
    { key: 'biocontrol', icon: ShieldHalf, tone: 'from-leaf/80 to-alertOrange/40' },
  ],
  high: [
    { key: 'treat', icon: SprayCan, tone: 'from-burntOchre/90 to-alertOrange/70' },
    { key: 'cover', icon: ShieldHalf, tone: 'from-slate to-loam' },
    { key: 'support', icon: LifeBuoy, tone: 'from-leaf/70 to-parchment/80' },
  ],
};

const ActionCards = () => {
  const { riskState } = useRisk();
  const { t } = useTranslation();
  const cards = ACTION_MATRIX[riskState];

  return (
    <section className="rounded-[32px] border border-white/10 bg-white/5 p-6 text-white">
      <p className="text-xs uppercase tracking-[0.35em] text-white/70">{t('actions.heading')}</p>
      <div className="mt-4 grid gap-4 md:grid-cols-3">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <article
              key={card.key}
              className={`flex min-h-[160px] flex-col justify-between rounded-[26px] border border-white/20 bg-gradient-to-br p-5 shadow-slab text-chlorophyll ${card.tone}`}
            >
              <Icon className="h-7 w-7" />
              <div>
                <h4 className="text-lg font-semibold">{t(`actions.${riskState}.${card.key}.title`)}</h4>
                <p className="text-sm text-chlorophyll/80">{t(`actions.${riskState}.${card.key}.body`)}</p>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
};

export default ActionCards;
