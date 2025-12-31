import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

export default function CTASection() {
  return (
    <section className="py-20 bg-indigo-600">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
          {LANDING_CONFIG.cta.title}
        </h2>
        <p className="text-lg sm:text-xl text-indigo-100 mb-10 max-w-2xl mx-auto">
          {LANDING_CONFIG.cta.subheadline}
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Link
            href={LANDING_CONFIG.cta.buttonLink}
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-indigo-50 transition-colors"
          >
            {LANDING_CONFIG.cta.buttonText}
            <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            href="/demo"
            className="inline-flex items-center justify-center px-8 py-4 bg-transparent text-white font-semibold rounded-xl border-2 border-indigo-400 hover:bg-indigo-500 transition-colors"
          >
            Request Demo
          </Link>
        </div>

        <div className="flex flex-wrap justify-center gap-8 text-sm text-indigo-100">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔒</span>
            <span>No credit card required</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">✓</span>
            <span>14-day free trial</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">💬</span>
            <span>24/7 support</span>
          </div>
        </div>
      </div>
    </section>
  );
}
