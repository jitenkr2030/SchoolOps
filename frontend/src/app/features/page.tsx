import Link from 'next/link';
import { GraduationCap, ArrowRight, CheckCircle2, Mail, Phone, MapPin, Users, Calendar, BookOpen, MessageSquare, CreditCard, Bus } from 'lucide-react';

const features = [
  {
    icon: Users,
    title: 'Student Information System',
    description: 'Complete student profiles with enrollment workflows, attendance history, and performance tracking.',
    color: '#4F46E5',
  },
  {
    icon: Calendar,
    title: 'Attendance & Timetable',
    description: 'Daily attendance tracking with auto-scheduling and instant absence notifications to parents.',
    color: '#10B981',
  },
  {
    icon: BookOpen,
    title: 'Academics & Assessment',
    description: 'Digital gradebooks, online exams with auto-grading, and comprehensive lesson plan management.',
    color: '#F59E0B',
  },
  {
    icon: MessageSquare,
    title: 'Communication Hub',
    description: 'Announcements, parent-teacher messaging, and automated notifications for all stakeholders.',
    color: '#EC4899',
  },
  {
    icon: CreditCard,
    title: 'Fees & Finance',
    description: 'Automated fee collection, online payments, expense tracking, and financial reporting.',
    color: '#06B6D4',
  },
  {
    icon: Bus,
    title: 'Transport & Hostel',
    description: 'GPS-enabled transport tracking, hostel room allocation, and mess management.',
    color: '#84CC16',
  },
];

const allFeatures = [
  'Multi-branch school support',
  'Role-based access control',
  'Bulk student import/export',
  'Custom report builder',
  'Inventory management',
  'Library management',
  'Staff payroll processing',
  'Exam scheduling',
  'Homework assignment',
  'Parent portal access',
  'Student portal access',
  'Real-time dashboards',
];

export default function FeaturesPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Powerful Features for Modern Schools</h1>
            <p className="text-xl text-slate-300">
              Everything you need to manage your school efficiently, from admissions to academics and everything in between.
            </p>
          </div>
        </div>
      </header>

      {/* Core Features */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Core Management Modules</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Comprehensive tools designed specifically for the unique needs of educational institutions
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-slate-50 rounded-xl p-8 hover:shadow-lg transition-shadow">
                <div
                  className="w-14 h-14 rounded-xl flex items-center justify-center mb-6"
                  style={{ backgroundColor: `${feature.color}20` }}
                >
                  <feature.icon className="w-7 h-7" style={{ color: feature.color }} />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* All Features Grid */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">And Much More</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Additional features to streamline your school operations
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {allFeatures.map((feature, index) => (
              <div key={index} className="flex items-center gap-3 bg-white rounded-lg p-4 shadow-sm">
                <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                <span className="text-slate-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Role-Based Features */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Built for Every Stakeholder</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Tailored experiences for administrators, teachers, students, and parents
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-indigo-600 rounded-xl p-6 text-white">
              <h3 className="text-xl font-bold mb-4">Administrators</h3>
              <ul className="space-y-2 text-indigo-100">
                <li>• Complete system control</li>
                <li>• Multi-school management</li>
                <li>• Financial dashboards</li>
                <li>• Staff management</li>
                <li>• Custom reports</li>
              </ul>
            </div>
            <div className="bg-emerald-600 rounded-xl p-6 text-white">
              <h3 className="text-xl font-bold mb-4">Teachers</h3>
              <ul className="space-y-2 text-emerald-100">
                <li>• Digital attendance</li>
                <li>• Grade management</li>
                <li>• Homework portal</li>
                <li>• Parent messaging</li>
                <li>• Lesson plans</li>
              </ul>
            </div>
            <div className="bg-amber-600 rounded-xl p-6 text-white">
              <h3 className="text-xl font-bold mb-4">Students</h3>
              <ul className="space-y-2 text-amber-100">
                <li>• Attendance records</li>
                <li>• Grades & transcripts</li>
                <li>• Homework portal</li>
                <li>• Class timetable</li>
                <li>• Fee status</li>
              </ul>
            </div>
            <div className="bg-purple-600 rounded-xl p-6 text-white">
              <h3 className="text-xl font-bold mb-4">Parents</h3>
              <ul className="space-y-2 text-purple-100">
                <li>• Attendance alerts</li>
                <li>• Progress tracking</li>
                <li>• Fee payments</li>
                <li>• Teacher messaging</li>
                <li>• Event updates</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Integration Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Seamless Integrations</h2>
              <p className="text-lg text-slate-600 mb-4">
                SchoolOps integrates with the tools you already use, including payment gateways, SMS services, and authentication systems.
              </p>
              <p className="text-lg text-slate-600 mb-6">
                Our open API allows custom integrations to meet your specific requirements.
              </p>
              <Link
                href="/integrations"
                className="inline-flex items-center gap-2 text-indigo-600 font-semibold hover:text-indigo-700"
              >
                View Integrations
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <h3 className="text-xl font-semibold text-slate-900 mb-6">Popular Integrations</h3>
              <div className="grid grid-cols-2 gap-4">
                {['Razorpay', 'Stripe', 'Twilio', 'MSG91', 'Google Workspace', 'Microsoft 365'].map((integration, index) => (
                  <div key={index} className="flex items-center gap-2 p-3 bg-slate-50 rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                    <span className="text-slate-700 font-medium">{integration}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your School?</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Start your free trial today and experience the power of SchoolOps
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
