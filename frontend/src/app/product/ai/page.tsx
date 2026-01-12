import Link from 'next/link';
import { GraduationCap, ArrowRight, Brain, LightbulbOn, Robot, Translate, Eye, Route, Sparkles, Mail, Phone, MapPin } from 'lucide-react';

const aiFeatures = [
  {
    icon: Brain,
    title: 'Analytics & Predictions',
    description: 'AI-powered insights to identify at-risk students, forecast enrollment trends, and predict fee collection patterns.',
    color: '#4F46E5',
    features: ['At-risk student detection', 'Enrollment forecasting', 'Fee churn prediction', 'Performance analytics'],
  },
  {
    icon: LightbulbOn,
    title: 'Personalization',
    description: 'Adaptive learning paths and smart recommendations tailored to each student\'s unique learning style.',
    color: '#10B981',
    features: ['Adaptive learning paths', 'Smart recommendations', 'Remedial assignments', 'Study suggestions'],
  },
  {
    icon: Robot,
    title: 'Automation Assistants',
    description: 'Intelligent automation for quizzes, grading, and notifications to save educators valuable time.',
    color: '#F59E0B',
    features: ['AI quiz generation', 'Auto-grading', 'Smart notifications', 'Report generation'],
  },
  {
    icon: Translate,
    title: 'NLP Chatbot',
    description: 'Multilingual support with voice capabilities for seamless communication across language barriers.',
    color: '#8B5CF6',
    features: ['Multilingual support', 'Voice assistant', 'Automated responses', 'Language translation'],
  },
  {
    icon: Eye,
    title: 'Document Intelligence',
    description: 'Advanced OCR technology for document processing, receipt scanning, and ID verification.',
    color: '#EC4899',
    features: ['OCR processing', 'Receipt scanning', 'ID verification', 'Document classification'],
  },
  {
    icon: Route,
    title: 'Resource Optimization',
    description: 'Smart algorithms to optimize timetables and plan efficient transport routes.',
    color: '#06B6D4',
    features: ['Timetable optimization', 'Bus route planning', 'Room allocation', 'Resource scheduling'],
  },
];

const testimonials = [
  {
    quote: 'The AI-powered at-risk student detection has been a game-changer. We can now intervene early and support students who need help.',
    author: 'Dr. Sarah Johnson',
    role: 'Principal, Springfield High',
  },
  {
    quote: 'Auto-grading saves our teachers hours every week. The accuracy is impressive, and teachers can focus on what they do best - teaching.',
    author: 'Mr. Rahul Sharma',
    role: 'Teacher, Delhi Public School',
  },
  {
    quote: 'The multilingual chatbot has improved parent engagement significantly. Communication is no longer a barrier.',
    author: 'Mrs. Priya Patel',
    role: 'Administrator, Ryan International',
  },
];

export default function AIPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                <Brain className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold">AI-Powered Features</h1>
            </div>
            <p className="text-xl text-slate-300">
              Leverage the power of artificial intelligence to transform your school operations and improve educational outcomes.
            </p>
          </div>
        </div>
      </header>

      {/* AI Features Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Intelligent Features</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Cutting-edge AI capabilities designed specifically for educational institutions
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {aiFeatures.map((feature, index) => (
              <div key={index} className="bg-slate-50 rounded-xl p-8 hover:shadow-lg transition-shadow">
                <div
                  className="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
                  style={{ backgroundColor: `${feature.color}20` }}
                >
                  <feature.icon className="w-7 h-7" style={{ color: feature.color }} />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600 mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.features.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-center gap-2 text-sm text-slate-600">
                      <Sparkles className="w-4 h-4 text-indigo-500" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">How Our AI Works</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Advanced machine learning models trained on educational data
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '01', title: 'Data Collection', description: 'Securely collect and process school data with full privacy compliance' },
              { step: '02', title: 'Model Training', description: 'AI models learn from patterns to provide accurate predictions' },
              { step: '03', title: 'Insight Generation', description: 'Receive actionable insights and recommendations' },
              { step: '04', title: 'Continuous Improvement', description: 'Models improve over time with more data and feedback' },
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-slate-600 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Trusted by Schools Worldwide</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              See what educators are saying about our AI features
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-8 text-white">
                <div className="flex gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star key={star} className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-slate-300 mb-6 italic">&quot;{testimonial.quote}&quot;</p>
                <div>
                  <p className="font-semibold text-white">{testimonial.author}</p>
                  <p className="text-sm text-slate-400">{testimonial.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Privacy & Security */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Privacy-First AI</h2>
              <p className="text-lg text-slate-600 mb-4">
                We take data privacy seriously. Our AI features are designed with privacy at their core.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sparkles className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Data Anonymization</h3>
                    <p className="text-slate-600 text-sm">All data is anonymized before processing</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sparkles className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">FERPA Compliant</h3>
                    <p className="text-slate-600 text-sm">Full compliance with educational privacy laws</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-emerald-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Sparkles className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">No Data Sharing</h3>
                    <p className="text-slate-600 text-sm">Your data is never shared or sold</p>
                  </div>
                </li>
              </ul>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-lg">
              <h3 className="text-xl font-semibold text-slate-900 mb-6">AI Feature Availability</h3>
              <div className="space-y-4">
                {[
                  { plan: 'Starter', available: false },
                  { plan: 'Professional', available: true },
                  { plan: 'Enterprise', available: true },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                    <span className="font-medium text-slate-900">{item.plan}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${item.available ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {item.available ? 'Included' : 'Not Included'}
                    </span>
                  </div>
                ))}
              </div>
              <Link
                href="/pricing"
                className="block w-full py-4 mt-6 text-center bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Experience the Power of AI</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Start your free trial today and discover how AI can transform your school
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
