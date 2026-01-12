import Link from 'next/link';
import { GraduationCap, ArrowRight, CheckCircle2, Mail, Phone, MapPin, Users, Building, Star } from 'lucide-react';

const plans = [
  {
    name: 'Starter',
    description: 'Perfect for small schools getting started',
    monthlyPrice: 4999,
    yearlyPrice: 49990,
    features: [
      'Up to 200 students',
      'Core modules (5)',
      'Basic reports',
      'Email support',
      'Mobile app access',
      'Parent portal',
      'Student portal',
    ],
    cta: 'Get Started',
    popular: false,
    color: '#6B7280',
  },
  {
    name: 'Professional',
    description: 'Ideal for growing schools',
    monthlyPrice: 9999,
    yearlyPrice: 99990,
    features: [
      'Up to 1000 students',
      'All 10 core modules',
      'AI features included',
      'Advanced analytics',
      'Priority support',
      'Custom integrations',
      'API access',
      'Dedicated account manager',
    ],
    cta: 'Start Free Trial',
    popular: true,
    color: '#4F46E5',
  },
  {
    name: 'Enterprise',
    description: 'For large institutions',
    monthlyPrice: 24999,
    yearlyPrice: 249990,
    features: [
      'Unlimited students',
      'All modules + AI Suite',
      'Multi-branch support',
      'Dedicated account manager',
      'Custom development',
      'On-premise option',
      'SLA guarantee',
      '24/7 phone support',
      'Custom training',
      'White-label options',
    ],
    cta: 'Contact Sales',
    popular: false,
    color: '#1F2937',
  },
];

const faqs = [
  {
    question: 'Can I switch plans later?',
    answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes take effect at the start of your next billing cycle.',
  },
  {
    question: 'Is there a free trial?',
    answer: 'Yes, all plans come with a 14-day free trial. No credit card required to start.',
  },
  {
    question: 'What payment methods do you accept?',
    answer: 'We accept all major credit cards, debit cards, net banking, UPI, and bank transfers for annual plans.',
  },
  {
    question: 'What happens after my trial ends?',
    answer: 'After your trial, you can choose to subscribe to a paid plan or continue with limited free features.',
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Simple, Transparent Pricing</h1>
            <p className="text-xl text-slate-300">
              Choose the plan that fits your school. All plans include a 14-day free trial.
            </p>
          </div>
        </div>
      </header>

      {/* Pricing Cards */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Billing Toggle */}
          <div className="flex justify-center mb-12">
            <div className="bg-slate-100 rounded-xl p-1 inline-flex">
              <button className="px-6 py-2 bg-white rounded-lg shadow-sm text-sm font-medium text-slate-900">
                Monthly
              </button>
              <button className="px-6 py-2 text-sm font-medium text-slate-600 hover:text-slate-900">
                Yearly (Save 17%)
              </button>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <div
                key={index}
                className={`relative rounded-2xl p-8 ${
                  plan.popular ? 'bg-white shadow-xl ring-2 ring-indigo-600' : 'bg-slate-50'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <span className="bg-indigo-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                <div className="mb-8">
                  <h3 className="text-xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                  <p className="text-slate-600 mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-slate-900">
                      ₹{plan.monthlyPrice.toLocaleString()}
                    </span>
                    <span className="text-slate-500">/month</span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">
                    or ₹{plan.yearlyPrice.toLocaleString()}/year
                  </p>
                </div>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/register"
                  className={`block w-full py-4 text-center font-semibold rounded-xl transition-colors ${
                    plan.popular
                      ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                      : 'bg-white text-slate-900 border border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Compare Plans</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Detailed comparison of features across all plans
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full bg-white rounded-xl shadow-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-4 px-6 font-semibold text-slate-900">Feature</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-900">Starter</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-900 bg-indigo-50">Professional</th>
                  <th className="text-center py-4 px-6 font-semibold text-slate-900">Enterprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {[
                  { feature: 'Students', starter: 'Up to 200', pro: 'Up to 1,000', enterprise: 'Unlimited' },
                  { feature: 'Core Modules', starter: '5', pro: '10', enterprise: 'All' },
                  { feature: 'AI Features', starter: false, pro: true, enterprise: true },
                  { feature: 'API Access', starter: false, pro: true, enterprise: true },
                  { feature: 'Multi-branch', starter: false, pro: false, enterprise: true },
                  { feature: 'On-premise', starter: false, pro: false, enterprise: true },
                  { feature: 'Support', starter: 'Email', pro: 'Priority', enterprise: '24/7 Phone' },
                  { feature: 'SLA', starter: false, pro: false, enterprise: true },
                ].map((row, index) => (
                  <tr key={index}>
                    <td className="py-4 px-6 text-slate-700">{row.feature}</td>
                    <td className="text-center py-4 px-6 text-slate-600">
                      {typeof row.starter === 'boolean' ? (
                        row.starter ? <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" /> : '—'
                      ) : (
                        row.starter
                      )}
                    </td>
                    <td className="text-center py-4 px-6 bg-indigo-50 text-slate-600">
                      {typeof row.pro === 'boolean' ? (
                        row.pro ? <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" /> : '—'
                      ) : (
                        row.pro
                      )}
                    </td>
                    <td className="text-center py-4 px-6 text-slate-600">
                      {typeof row.enterprise === 'boolean' ? (
                        row.enterprise ? <CheckCircle2 className="w-5 h-5 text-emerald-500 mx-auto" /> : '—'
                      ) : (
                        row.enterprise
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQs */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Frequently Asked Questions</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Have questions about pricing? We have answers.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-slate-50 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{faq.question}</h3>
                <p className="text-slate-600">{faq.answer}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Get Started?</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Start your 14-day free trial today. No credit card required.
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-slate-100 transition-colors"
          >
            Start Free Trial
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-slate-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <Link href="/" className="flex items-center gap-2 mb-4">
                <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center">
                  <GraduationCap className="w-6 h-6 text-white" />
                </div>
                <span className="text-xl font-bold text-white">SchoolOps</span>
              </Link>
              <p className="text-sm text-slate-400">Smart school management powered by AI</p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/product/ai" className="hover:text-white transition-colors">AI Features</Link></li>
                <li><Link href="/mobile-app" className="hover:text-white transition-colors">Mobile App</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white transition-colors">About Us</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Contact</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2"><Mail className="w-4 h-4" /> contact@schoolops.com</li>
                <li className="flex items-center gap-2"><Phone className="w-4 h-4" /> +91 1800 123 4567</li>
                <li className="flex items-center gap-2"><MapPin className="w-4 h-4" /> Bangalore, India</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 text-center text-sm text-slate-400">
            © {new Date().getFullYear()} SchoolOps. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
