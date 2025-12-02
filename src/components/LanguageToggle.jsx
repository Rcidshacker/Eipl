import { useTranslation } from 'react-i18next';

const langs = [
  { id: 'en', labelKey: 'language.english', short: 'EN' },
  { id: 'mr', labelKey: 'language.marathi', short: 'MR' },
];

const LanguageToggle = () => {
  const { i18n, t } = useTranslation();

  const handleChange = (lang) => {
    i18n.changeLanguage(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem('sitaphal-lang', lang);
    }
  };

  return (
    <div
      className="flex items-center gap-1 rounded-full bg-white/10 p-1 text-sm"
      role="group"
      aria-label="Language selector"
    >
      {langs.map((lang) => {
        const active = i18n.language === lang.id;
        return (
          <button
            key={lang.id}
            type="button"
            aria-pressed={active}
            onClick={() => handleChange(lang.id)}
            className={`min-w-[64px] rounded-full px-4 py-2 font-semibold transition-all focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-alertOrange ${
              active ? 'bg-parchment text-chlorophyll shadow-slab' : 'text-parchment/80'
            }`}
          >
            <span className="block text-xs uppercase tracking-[0.2em]">{lang.short}</span>
            <span className="text-[0.85rem] leading-none">{t(lang.labelKey)}</span>
          </button>
        );
      })}
    </div>
  );
};

export default LanguageToggle;
