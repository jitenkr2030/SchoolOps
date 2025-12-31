'use client';

import { useState } from 'react';
import { 
  ShieldAccount, 
  Teach, 
  School, 
  AccountGroup,
  Check
} from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'shield-account': ShieldAccount,
  'teach': Teach,
  'school': School,
  'account-group': AccountGroup,
};

interface RoleCardProps {
  role: typeof LANDING_CONFIG.userRoles[0];
  isActive: boolean;
  onPress: () => void;
}

const RoleCard: React.FC<RoleCardProps> = ({ role, isActive, onPress }) => {
  const IconComponent = iconMap[role.icon] || School;
  
  return (
    <button
      className={`flex flex-col items-center p-6 rounded-xl border-2 transition-all min-w-[140px] ${
        isActive
          ? 'border-indigo-600 bg-white shadow-lg'
          : 'border-slate-200 bg-white hover:border-indigo-200'
      }`}
      onClick={onPress}
    >
      <div 
        className={`w-14 h-14 rounded-full flex items-center justify-center mb-3 transition-colors ${
          isActive ? '' : 'bg-slate-100'
        }`}
        style={{ 
          backgroundColor: isActive ? `${role.color}20` : undefined 
        }}
      >
        <IconComponent 
          className="w-7 h-7" 
          style={{ color: role.color }} 
        />
      </div>
      <span 
        className={`font-semibold ${isActive ? '' : 'text-slate-600'}`}
        style={{ color: isActive ? role.color : undefined }}
      >
        {role.title}
      </span>
    </button>
  );
};

interface RoleFeatureListProps {
  role: typeof LANDING_CONFIG.userRoles[0];
}

const RoleFeatureList: React.FC<RoleFeatureListProps> = ({ role }) => {
  return (
    <div>
      <h4 className="text-lg font-semibold text-slate-900 mb-4">
        Key Benefits for {role.title}
      </h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {role.features.map((feature, index) => (
          <div key={index} className="flex items-center gap-3">
            <span className="text-lg" style={{ color: role.color }}>✓</span>
            <span className="text-slate-600">{feature}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

interface RoleTabsSectionProps {
  onSelectPlan: (planId: string) => void;
}

export default function RoleTabsSection({ onSelectPlan }: RoleTabsSectionProps) {
  const [activeRole, setActiveRole] = useState(LANDING_CONFIG.userRoles[0]);
  const activeRoleData = LANDING_CONFIG.userRoles.find(r => r.id === activeRole.id) || LANDING_CONFIG.userRoles[0];

  return (
    <section id="roles" className="py-20 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Built for Everyone in the School Ecosystem
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Whether you're an administrator, teacher, student, or parent, SchoolOps has tools tailored for your needs
          </p>
        </div>
        
        <div className="flex flex-wrap justify-center gap-4 mb-12">
          {LANDING_CONFIG.userRoles.map((role) => (
            <RoleCard
              key={role.id}
              role={role}
              isActive={activeRole.id === role.id}
              onPress={() => setActiveRole(role)}
            />
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto items-center">
          <div>
            <h3 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3">
              {activeRoleData.title}
            </h3>
            <p className="text-lg text-slate-600 mb-8">
              {activeRoleData.description}
            </p>
            <RoleFeatureList role={activeRoleData} />
          </div>
          
          <div 
            className="bg-white rounded-2xl overflow-hidden shadow-xl border-t-4"
            style={{ borderColor: activeRoleData.color }}
          >
            <div className="bg-slate-100 px-4 py-3 flex items-center gap-2 border-b border-slate-200">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
              </div>
            </div>
            <div className="p-6">
              <h4 className="text-xl font-bold mb-6" style={{ color: activeRoleData.color }}>
                {activeRoleData.title} Dashboard
              </h4>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-slate-50 p-4 rounded-lg border-l-4" style={{ borderColor: activeRoleData.color }}>
                  <div className="text-2xl font-bold text-slate-900">94%</div>
                  <div className="text-sm text-slate-500">Attendance</div>
                </div>
                <div className="bg-slate-50 p-4 rounded-lg border-l-4" style={{ borderColor: activeRoleData.color }}>
                  <div className="text-2xl font-bold text-slate-900">A-</div>
                  <div className="text-sm text-slate-500">Performance</div>
                </div>
              </div>
              
              <div className="space-y-3">
                {[1, 2, 3].map((item) => (
                  <div key={item} className="flex items-center gap-3">
                    <div 
                      className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold"
                      style={{ backgroundColor: `${activeRoleData.color}20`, color: activeRoleData.color }}
                    >
                      ✓
                    </div>
                    <div className="flex-1 h-3 bg-slate-100 rounded" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
