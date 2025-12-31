'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

interface FAQItemProps {
  item: typeof LANDING_CONFIG.faqs[0];
  isExpanded: boolean;
  onToggle: () => void;
}

const FAQItem: React.FC<FAQItemProps> = ({ item, isExpanded, onToggle }) => {
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden mb-4">
      <button
        className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50 transition-colors"
        onClick={onToggle}
      >
        <span className="font-semibold text-slate-900 pr-4">{item.question}</span>
        <ChevronDown 
          className={`w-5 h-5 text-indigo-600 flex-shrink-0 transition-transform ${isExpanded ? 'rotate-180' : ''}`} 
        />
      </button>
      
      {isExpanded && (
        <div className="px-5 pb-5 pt-0 border-t border-slate-100">
          <p className="text-slate-600 leading-relaxed pt-4">{item.answer}</p>
        </div>
      )}
    </div>
  );
};

interface FAQSectionProps {
  onSelectPlan: (planId: string) => void;
}

export default function FAQSection({ onSelectPlan }: FAQSectionProps) {
  const [expandedId, setExpandedId] = useState<number | null>(1);

  const toggleFAQ = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <section id="faq" className="py-20 bg-slate-50">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-lg text-slate-600">
            Got questions? We've got answers. If you don't see your question here, feel free to contact us.
          </p>
        </div>
        
        <div className="mb-12">
          {LANDING_CONFIG.faqs.map((faq) => (
            <FAQItem
              key={faq.id}
              item={faq}
              isExpanded={expandedId === faq.id}
              onToggle={() => toggleFAQ(faq.id)}
            />
          ))}
        </div>
        
        <div className="bg-indigo-600 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-white mb-3">
            Still have questions?
          </h3>
          <p className="text-indigo-100 mb-6 max-w-md mx-auto">
            Our team is here to help. Contact us and we'll get back to you within 24 hours.
          </p>
          <button 
            className="inline-flex items-center px-6 py-3 bg-white text-indigo-600 font-semibold rounded-lg hover:bg-indigo-50 transition-colors"
            onClick={() => onSelectPlan('contact')}
          >
            Contact Sales
          </button>
        </div>
      </div>
    </section>
  );
}
