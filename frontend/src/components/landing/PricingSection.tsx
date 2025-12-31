'use client';

import { useState } from 'react';
import { Check } from 'lucide-react';
import { LANDING_CONFIG, formatPrice, calculateYearlyDiscount } from '@/data/landing-data';

interface PricingCardProps {
  plan: typeof LANDING_CONFIG.pricing[0];
  isYearly: boolean;
  onSelect: (planId: string) => void;
}

const PricingCard: React.FC<PricingCardProps> = ({ plan, isYearly, onSelect }) => {
  const price = isYearly ? plan.yearlyPrice : plan.monthlyPrice;
  const savings = calculateYearlyDiscount(plan.monthlyPrice, plan.yearlyPrice);
  const displayPrice = formatPrice(price);

  return (
    <div className={`relative bg-white rounded-2xl p-8 border-2 transition-all duration-300 hover:shadow-xl ${
      plan.popular 
        ? 'border-indigo-600 shadow-lg scale-105' 
        : 'border-slate-200 hover:border-indigo-200'
    }`}>
      {plan.popular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="inline-flex items-center px-4 py-1 bg-indigo-600 text-white text-sm font-semibold rounded-full">
            Most Popular
          </span>
        </div>
      )}
      
      <div className="mb-6">
        <h3 className="text-2xl font-bold mb-2" style={{ color: plan.color }}>
          {plan.name}
        </h3>
        <p className="text-slate-600">{plan.description}</p>
      </div>
      
      <div className="mb-4">
        <div className="flex items-baseline gap-1">
          <span className="text-4xl font-bold text-slate-900">
            {displayPrice}
          </span>
          <span className="text-slate-500">/{isYearly ? 'year' : 'month'}</span>
        </div>
      </div>
      
      {isYearly && savings > 0 && (
        <div className="mb-6">
          <span className="inline-flex items-center px-3 py-1 bg-emerald-100 text-emerald-700 text-sm font-semibold rounded-lg">
            Save {savings}%
          </span>
        </div>
      )}
      
      <ul className="space-y-4 mb-8">
        {plan.features.map((feature, index) => (
          <li key={index} className="flex items-start gap-3">
            <Check className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
            <span className="text-slate-600">{feature}</span>
          </li>
        ))}
      </ul>
      
      <button
        className="w-full py-3 rounded-xl font-semibold transition-all duration-200 hover:opacity-90"
        style={{ backgroundColor: plan.color, color: 'white' }}
        onClick={() => onSelect(plan.id)}
      >
        {plan.cta}
      </button>
    </div>
  );
};

interface PricingSectionProps {
  onSelectPlan: (planId: string) => void;
}

export default function PricingSection({ onSelectPlan }: PricingSectionProps) {
  const [isYearly, setIsYearly] = useState(true);

  return (
    <section id="pricing" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg text-slate-600">
            Choose the plan that fits your school. All plans include core features.
          </p>
        </div>
        
        <div className="flex justify-center mb-12">
          <div className="inline-flex items-center gap-4 p-1 bg-slate-100 rounded-xl">
            <button
              className={`px-6 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                !isYearly
                  ? 'bg-white text-slate-900 shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              onClick={() => setIsYearly(false)}
            >
              Monthly
            </button>
            <button
              className={`relative px-6 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                isYearly
                  ? 'bg-white text-slate-900 shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              onClick={() => setIsYearly(true)}
            >
              Yearly
              <span className="absolute -top-2 -right-2 inline-flex items-center px-2 py-0.5 bg-emerald-500 text-white text-xs font-bold rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {LANDING_CONFIG.pricing.map((plan) => (
            <PricingCard
              key={plan.id}
              plan={plan}
              isYearly={isYearly}
              onSelect={onSelectPlan}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
