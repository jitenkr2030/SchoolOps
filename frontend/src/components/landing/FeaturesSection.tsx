'use client';

import { useState } from 'react';
import { 
  School,
  User,
  CalendarCheck,
  BookOpen,
  MessageSquare,
  DollarSign,
  Bus,
  Building2,
  Briefcase,
  BarChart3,
  Brain,
  Lightbulb,
  Bot,
  Languages,
  Eye,
  Map,
  ChevronDown,
  Sparkles
} from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  school: School,
  'account-child': User,
  'calendar-check': CalendarCheck,
  'book-open-variant': BookOpen,
  'message-text': MessageSquare,
  'cash-multiple': DollarSign,
  'bus-school': Bus,
  library: Building2,
  'account-tie': Briefcase,
  'chart-bar': BarChart3,
  brain: Brain,
  'lightbulb-on': Lightbulb,
  robot: Bot,
  translate: Languages,
  eye: Eye,
  route: Map,
};

interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
  color: string;
  badge?: string;
}

function FeatureCard({ icon, title, description, color, badge }: FeatureCardProps) {
  const IconComponent = iconMap[icon] || School;
  
  return (
    <div className="group relative p-6 bg-white rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
      {badge && (
        <div className="absolute -top-3 -right-3">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-semibold rounded-full shadow-md">
            <Sparkles className="w-3 h-3" />
            {badge}
          </span>
        </div>
      )}
      <div 
        className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform duration-300 group-hover:scale-110"
        style={{ backgroundColor: `${color}15` }}
      >
        <IconComponent 
          className="w-6 h-6" 
          color={color}
        />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 mb-2">
        {title}
      </h3>
      <p className="text-slate-600 text-sm leading-relaxed">
        {description}
      </p>
    </div>
  );
}

export default function FeaturesSection() {
  const [activeTab, setActiveTab] = useState<'core' | 'ai'>('core');
  const features = LANDING_CONFIG.features;

  const handleSelectPlan = (planId: string) => {
    console.log('Selected plan:', planId);
  };

  return (
    <section id="features" className="py-20 sm:py-32 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            {features.title}
          </h2>
          <p className="text-lg text-slate-600">
            {features.subtitle}
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-12">
          <div className="inline-flex items-center gap-2 p-1 bg-slate-100 rounded-xl">
            <button
              onClick={() => setActiveTab('core')}
              className={`px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 ${
                activeTab === 'core'
                  ? 'bg-white text-indigo-600 shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Core Modules
            </button>
            <button
              onClick={() => setActiveTab('ai')}
              className={`inline-flex items-center gap-2 px-6 py-2.5 rounded-lg font-semibold text-sm transition-all duration-200 ${
                activeTab === 'ai'
                  ? 'bg-white text-indigo-600 shadow-md'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              AI Features
            </button>
          </div>
        </div>

        {/* Core Modules Grid */}
        <div 
          className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 transition-all duration-500 ${
            activeTab === 'core' ? 'opacity-100 translate-y-0' : 'opacity-50 translate-y-4 pointer-events-none absolute'
          }`}
        >
          {features.coreModules.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              color={feature.color}
            />
          ))}
        </div>

        {/* AI Features Grid */}
        <div 
          className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 transition-all duration-500 ${
            activeTab === 'ai' ? 'opacity-100 translate-y-0' : 'opacity-50 translate-y-4 pointer-events-none absolute'
          }`}
        >
          {features.aiFeatures.map((feature, index) => (
            <FeatureCard
              key={index}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              color={feature.color}
              badge={feature.badge}
            />
          ))}
        </div>

        {/* Integration Note */}
        <div className="mt-16 p-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h4 className="text-lg font-semibold text-slate-900 mb-1">
                All features work seamlessly together
              </h4>
              <p className="text-slate-600 text-sm">
                Our unified platform means your data flows automatically between modules, saving time and eliminating errors.
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm font-medium text-indigo-600">
              <span>Explore all 16 modules</span>
              <ChevronDown className="w-4 h-4 rotate-[-90deg]" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
