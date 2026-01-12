import Link from 'next/link';
import { GraduationCap, ArrowRight, Smartphone, Tablet, Monitor, Download, Mail, Phone, MapPin, Star, CheckCircle2 } from 'lucide-react';

const appFeatures = [
  {
    icon: Smartphone,
    title: 'For Parents',
    description: 'Stay connected with your child\'s education',
    features: [
      'Real-time attendance alerts',
      'Academic progress tracking',
      'Fee payment portal',
      'Teacher messaging',
      'Homework monitoring',
      'Event notifications',
    ],
    color: '#4F46E5',
  },
  {
    icon: Tablet,
    title: 'For Teachers',
    description: 'Manage your classroom on the go',
    features: [
      'Digital attendance taking',
      'Grade management',
      'Homework assignment',
      'Parent communication',
      'Class schedule',
      'Lesson plan access',
    ],
    color: '#10B981',
  },
  {
    icon: Monitor,
    title: 'For Students',
    description: 'Access all academic resources',
    features: [
      'Attendance records',
      'Grades & transcripts',
      'Homework portal',
      'Class timetable',
      'Study materials',
      'Fee status',
    ],
    color: '#F59E0B',
  },
];

const appStats = [
  { value: '50K+', label: 'Downloads' },
  { value: '4.8', label: 'App Store Rating' },
  { value: '4.7', label: 'Play Store Rating' },
  { value: '99%', label: 'User Satisfaction' },
];

export default function MobileAppPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                <Smartphone className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold">Mobile App</h1>
            </div>
            <p className="text-xl text-slate-300">
              SchoolOps on your fingertips. Access everything you need, anywhere, anytime.
            </p>
          </div>
        </div>
      </header>

      {/* App Preview Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Stay Connected, Always</h2>
              <p className="text-lg text-slate-600 mb-8">
                The SchoolOps mobile app brings the power of our comprehensive school management platform to your smartphone. Whether you are a parent, teacher, or student, stay informed and connected wherever you go.
              </p>
              <div className="flex flex-wrap gap-4">
                <a
                  href="#"
                  className="inline-flex items-center gap-3 px-6 py-3 bg-black text-white rounded-xl hover:bg-slate-800 transition-colors"
                >
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
                  </svg>
                  <div className="text-left">
                    <p className="text-xs text-slate-400">Download on the</p>
                    <p className="font-semibold">App Store</p>
                  </div>
                </a>
                <a
                  href="#"
                  className="inline-flex items-center gap-3 px-6 py-3 bg-black text-white rounded-xl hover:bg-slate-800 transition-colors"
                >
                  <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>
                  </svg>
                  <div className="text-left">
                    <p className="text-xs text-slate-400">Get it on</p>
                    <p className="font-semibold">Google Play</p>
                  </div>
                </a>
              </div>
            </div>
            <div className="relative">
              <div className="bg-slate-100 rounded-3xl p-8 aspect-[3/4] max-w-xs mx-auto flex items-center justify-center">
                <Smartphone className="w-32 h-32 text-slate-300" />
              </div>
              <div className="absolute -bottom-4 -right-4 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium">
                App Preview
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* App Stats */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {appStats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-indigo-600 mb-2">{stat.value}</div>
                <div className="text-slate-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features by Role */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Features for Everyone</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Tailored experiences for parents, teachers, and students
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {appFeatures.map((role, index) => (
              <div key={index} className="bg-slate-50 rounded-xl p-8">
                <div
                  className="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
                  style={{ backgroundColor: `${role.color}20` }}
                >
                  <role.icon className="w-7 h-7" style={{ color: role.color }} />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">{role.title}</h3>
                <p className="text-slate-600 mb-6">{role.description}</p>
                <ul className="space-y-3">
                  {role.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center gap-3 text-sm text-slate-600">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Powerful Features</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Everything you need to stay connected and informed
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { title: 'Push Notifications', desc: 'Instant alerts for attendance, grades, and announcements' },
              { title: 'Offline Mode', desc: 'Access important data even without internet connection' },
              { title: 'Biometric Login', desc: 'Quick and secure login with fingerprint or face ID' },
              { title: 'Multi-language', desc: 'Support for multiple regional languages' },
              { title: 'Dark Mode', desc: 'Easy on the eyes with system-wide dark theme' },
              { title: 'Real-time Sync', desc: 'Data syncs instantly across all devices' },
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-slate-600 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Reviews */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Loved by Users</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              See what our users have to say
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'Priya S.', role: 'Parent', rating: 5, text: 'The app makes it so easy to track my child\'s attendance and grades. Love the push notifications!' },
              { name: 'Rahul K.', role: 'Teacher', rating: 5, text: 'Taking attendance and messaging parents has never been easier. A must-have app for teachers.' },
              { name: 'Amit M.', role: 'Principal', rating: 5, text: 'Our school went fully digital with the SchoolOps app. Parents and teachers love the convenience.' },
            ].map((review, index) => (
              <div key={index} className="bg-slate-900 rounded-xl p-6 text-white">
                <div className="flex gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star key={star} className="w-5 h-5 text-amber-400 fill-amber-400" />
                  ))}
                </div>
                <p className="text-slate-300 mb-4">&quot;{review.text}&quot;</p>
                <div>
                  <p className="font-semibold text-white">{review.name}</p>
                  <p className="text-sm text-slate-400">{review.role}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Download the App Today</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Join thousands of schools and families using the SchoolOps mobile app
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <a
              href="#"
              className="inline-flex items-center gap-3 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-slate-100 transition-colors"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01z"/>
              </svg>
              App Store
            </a>
            <a
              href="#"
              className="inline-flex items-center gap-3 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-slate-100 transition-colors"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
                <path d="M3,20.5V3.5C3,2.91 3.34,2.39 3.84,2.15L13.69,12L3.84,21.85C3.34,21.6 3,21.09 3,20.5M16.81,15.12L6.05,21.34L14.54,12.85L16.81,15.12M20.16,10.81C20.5,11.08 20.75,11.5 20.75,12C20.75,12.5 20.53,12.9 20.18,13.18L17.89,14.5L15.39,12L17.89,9.5L20.16,10.81M6.05,2.66L16.81,8.88L14.54,11.15L6.05,2.66Z"/>
              </svg>
              Google Play
            </a>
          </div>
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
