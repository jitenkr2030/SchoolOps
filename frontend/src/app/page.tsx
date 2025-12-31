'use client';

import Navbar from '@/components/landing/Navbar';
import HeroSection from '@/components/landing/HeroSection';
import FeaturesSection from '@/components/landing/FeaturesSection';
import RoleTabsSection from '@/components/landing/RoleTabsSection';
import TestimonialsSection from '@/components/landing/TestimonialsSection';
import PricingSection from '@/components/landing/PricingSection';
import FAQSection from '@/components/landing/FAQSection';
import CTASection from '@/components/landing/CTASection';
import Footer from '@/components/landing/Footer';

export default function LandingPage() {
  const handleSelectPlan = (planId: string) => {
    console.log('Selected plan:', planId);
    // Navigate to registration or contact page based on plan
    if (planId === 'contact') {
      window.location.href = '/contact';
    } else {
      window.location.href = '/register';
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <main>
        <HeroSection />
        <FeaturesSection />
        <RoleTabsSection />
        <TestimonialsSection onSelectPlan={handleSelectPlan} />
        <PricingSection onSelectPlan={handleSelectPlan} />
        <FAQSection onSelectPlan={handleSelectPlan} />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
