import { Star } from 'lucide-react';
import { LANDING_CONFIG } from '@/data/landing-data';

interface TestimonialCardProps {
  testimonial: typeof LANDING_CONFIG.testimonials[0];
}

const TestimonialCard: React.FC<TestimonialCardProps> = ({ testimonial }) => {
  return (
    <div 
      className="bg-white rounded-xl p-7 border border-slate-200 shadow-lg hover:shadow-xl transition-shadow"
      style={{ borderTopWidth: 4, borderTopColor: testimonial.color }}
    >
      <div className="flex gap-1 mb-4">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star key={star} className="w-5 h-5 text-amber-400 fill-current" />
        ))}
      </div>
      
      <p className="text-slate-600 italic leading-relaxed mb-6">
        "{testimonial.content}"
      </p>
      
      <div className="flex items-center gap-4">
        <div 
          className="w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold"
          style={{ backgroundColor: `${testimonial.color}20`, color: testimonial.color }}
        >
          {testimonial.avatar}
        </div>
        <div>
          <div className="font-semibold text-slate-900">{testimonial.name}</div>
          <div className="text-sm text-slate-500">{testimonial.role}</div>
          <div className="text-xs text-slate-400">{testimonial.school}</div>
        </div>
      </div>
    </div>
  );
};

interface TestimonialsSectionProps {
  onSelectPlan: (planId: string) => void;
}

export default function TestimonialsSection({ onSelectPlan }: TestimonialsSectionProps) {
  return (
    <section id="testimonials" className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">
            Trusted by Schools Worldwide
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            See what educators, administrators, and parents are saying about SchoolOps
          </p>
        </div>
        
        <div className="flex overflow-x-auto gap-6 pb-8 px-4 snap-x snap-mandatory scrollbar-hide">
          {LANDING_CONFIG.testimonials.map((testimonial) => (
            <div key={testimonial.id} className="flex-shrink-0 w-[360px] snap-center">
              <TestimonialCard testimonial={testimonial} />
            </div>
          ))}
        </div>
        
        <div className="mt-16 text-center">
          <p className="text-sm text-slate-500 uppercase tracking-wider mb-8">
            Trusted by leading institutions
          </p>
          <div className="flex flex-wrap justify-center gap-6">
            {['Delhi Public School', 'Ryan International', 'DAV Public', 'Jain Heritage', 'Narayana Group'].map((school, index) => (
              <div 
                key={index}
                className="w-24 h-12 bg-slate-100 rounded-lg flex items-center justify-center"
              >
                <span className="text-xl font-bold text-slate-400">{school.charAt(0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
