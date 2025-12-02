import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { baseRiskPercentage, horizonForecast, moistureProfiles, soilProfiles } from '../data/mockData';

const RiskContext = createContext(null);

const soilMap = soilProfiles.reduce((acc, profile) => {
  acc[profile.id] = profile;
  return acc;
}, {});

const moistureMap = moistureProfiles.reduce((acc, profile) => {
  acc[profile.id] = profile;
  return acc;
}, {});

const clamp = (value) => Math.min(100, Math.max(0, value));

const getRiskState = (value) => {
  if (value < 30) return 'low';
  if (value < 70) return 'medium';
  return 'high';
};

const computeRisk = (base, soilId, moistureId) => {
  const soilModifier = soilMap[soilId]?.modifier ?? 0;
  const moistureModifier = moistureMap[moistureId]?.modifier ?? 0;
  return clamp(base + soilModifier + moistureModifier);
};

export const RiskProvider = ({ children }) => {
  const [soil, setSoil] = useState('loam');
  const [moisture, setMoisture] = useState('balance');
  const [forecast, setForecast] = useState(horizonForecast);
  const [risk, setRisk] = useState(() => computeRisk(forecast[0]?.risk ?? baseRiskPercentage, 'loam', 'balance'));

  useEffect(() => {
    setRisk((current) => {
      const base = forecast[0]?.risk ?? current ?? baseRiskPercentage;
      return computeRisk(base, soil, moisture);
    });
  }, [soil, moisture, forecast]);

  const riskState = getRiskState(risk);

  const value = useMemo(
    () => ({
      risk,
      riskState,
      soil,
      setSoil,
      moisture,
      setMoisture,
      forecast,
      setForecast,
      soilProfiles,
      moistureProfiles,
    }),
    [risk, riskState, soil, moisture, forecast]
  );

  return <RiskContext.Provider value={value}>{children}</RiskContext.Provider>;
};

export const useRisk = () => {
  const context = useContext(RiskContext);
  if (!context) {
    throw new Error('useRisk must be used inside RiskProvider');
  }
  return context;
};
