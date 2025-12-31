import Link from 'next/link';
import { 
  Play, 
  ArrowRight, 
  CheckCircle2,
  GraduationCap,
  Users,
  Zap,
  Star
} from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

const heroStats = LANDING_CONFIG.hero.stats;

export default function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-slate-50 to-white">
      {/* Background Pattern */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-emerald-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000" />
        <div className="absolute -bottom-32 left-1/3 w-96 h-96 bg-blue-100 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 sm:pt-24 sm:pb-32 lg:pt-32 lg:pb-40">
        <div className="text-center max-w-4xl mx-auto">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-50 border border-indigo-100 mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
            </span>
            <span className="text-sm font-medium text-indigo-700">
              Trusted by 500+ schools worldwide
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight mb-6">
            {LANDING_CONFIG.hero.headline}
          </h1>

          {/* Subheadline */}
          <p className="text-lg sm:text-xl text-slate-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            {LANDING_CONFIG.hero.subheadline}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
            <Link
              href={LANDING_CONFIG.hero.primaryCTALink}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5"
            >
              {LANDING_CONFIG.hero.primaryCTA}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href={LANDING_CONFIG.hero.secondaryCTALink}
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-slate-700 font-semibold rounded-xl border border-slate-200 hover:border-indigo-200 hover:bg-indigo-50 transition-all duration-200"
            >
              <Play className="w-5 h-5 text-indigo-600" />
              {LANDING_CONFIG.hero.secondaryCTA}
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-slate-500 mb-16">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>14-day free trial</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>No credit card required</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span>Cancel anytime</span>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {heroStats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-slate-900 mb-1">
                  {stat.value}
                </div>
                <div className="text-sm text-slate-500 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dashboard Preview */}
        <div className="mt-20 relative max-w-6xl mx-auto">
          <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent z-10" />
          <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-slate-200 bg-slate-900">
            <div className="absolute top-0 left-0 right-0 h-8 bg-slate-800 flex items-center px-4 gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              <div className="w-3 h-3 rounded-full bg-emerald-500" />
            </div>
            <div className="pt-8 bg-slate-50 p-8 h-[400px] sm:h-[500px] flex items-center justify-center">
              <div className="text-center">
                <div className="w-24 h-24 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <GraduationCap className="w-12 h-12 text-indigo-600" />
                </div>
                <p className="text-slate-500 font-medium">Dashboard Preview</p>
                <p className="text-sm text-slate-400 mt-1">Interactive demo available in trial</p>
              </div>
            </div>
          </div>
        </div>

        {/* Logo Cloud */}
        <div className="mt-20 pt-16 border-t border-slate-100">
          <p className="text-center text-sm font-medium text-slate-400 mb-8">
            Trusted by leading institutions
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-16 opacity-50">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-6 h-6 text-slate-600" />
              <span className="font-semibold text-slate-600">Delhi Public School</span>
            </div>
            <div className="flex items-center gap-2">
              <Users className="w-6 h-6 text-slate-600" />
              <span className="font-semibold text-slate-600">Ryan International</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-6 h-6 text-slate-600" />
              <span className="font-semibold text-slate-600">Springfield High</span>
            </div>
            <div className="flex items-center gap-2">
              <Star className="w-6 h-6 text-slate-600" />
              <span className="font-semibold text-slate-600">Mount Carmel</span>
            </div>
            <div className="flex items-center gap-2">
              <GraduationCap className="w-6 h-6 text-slate-600" />
              <span className="font-semibold text-slate-600">St. Mary&apos;s</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
