import Link from 'next/link';
import { GraduationCap, ArrowRight, CheckCircle2, Mail, Phone, MapPin, CreditCard, MessageSquare, Key, Cloud, FileText, Users } from 'lucide-react';

const integrations = [
  {
    category: 'Payments',
    icon: CreditCard,
    items: [
      { name: 'Razorpay', description: 'India\'s leading payment gateway' },
      { name: 'Stripe', description: 'Global online payment processing' },
      { name: 'Paytm', description: 'Popular digital wallet in India' },
      { name: 'CCAvenue', description: 'Established payment solution' },
    ],
  },
  {
    category: 'Communications',
    icon: MessageSquare,
    items: [
      { name: 'Twilio', description: 'SMS and voice API' },
      { name: 'MSG91', description: 'SMS services for India' },
      { name: 'WhatsApp Business', description: 'Official WhatsApp integration' },
      { name: 'Firebase Cloud Messaging', description: 'Push notifications' },
    ],
  },
  {
    category: 'Authentication',
    icon: Key,
    items: [
      { name: 'Google Workspace', description: 'G-Suite SSO integration' },
      { name: 'Microsoft 365', description: 'Azure AD SSO' },
      { name: 'Okta', description: 'Enterprise identity management' },
      { name: 'Auth0', description: 'Authentication as a service' },
    ],
  },
  {
    category: 'Cloud Services',
    icon: Cloud,
    items: [
      { name: 'AWS', description: 'Amazon Web Services' },
      { name: 'Google Cloud', description: 'GCP infrastructure' },
      { name: 'Azure', description: 'Microsoft cloud platform' },
    ],
  },
  {
    category: 'Document Services',
    icon: FileText,
    items: [
      { name: 'DocuSign', description: 'Electronic signatures' },
      { name: 'Google Drive', description: 'Cloud storage' },
      { name: 'Dropbox', description: 'File sharing' },
    ],
  },
  {
    category: 'Student Information',
    icon: Users,
    items: [
      { name: 'Clever', description: 'Education SSO platform' },
      { name: 'ClassLink', description: 'Data integration' },
    ],
  },
];

const apiFeatures = [
  'RESTful API with comprehensive documentation',
  'Webhook support for real-time events',
  'SDKs for popular programming languages',
  'Rate limiting and throttling controls',
  'OAuth 2.0 authentication',
  'Sandbox environment for testing',
];

export default function IntegrationsPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Integrations</h1>
            <p className="text-xl text-slate-300">
              Connect SchoolOps with the tools you already use. Seamless integrations for payments, communications, and more.
            </p>
          </div>
        </div>
      </header>

      {/* Integration Categories */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Popular Integrations</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Connect with the tools and services you trust
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {integrations.map((category, index) => (
              <div key={index} className="bg-slate-50 rounded-xl p-8">
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                    <category.icon className="w-6 h-6 text-indigo-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900">{category.category}</h3>
                </div>
                <ul className="space-y-4">
                  {category.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-slate-900">{item.name}</p>
                        <p className="text-sm text-slate-500">{item.description}</p>
                      </div>
                      <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Powerful API</h2>
              <p className="text-lg text-slate-600 mb-4">
                Build custom integrations and extend SchoolOps functionality with our robust API. Whether you need to sync data with your existing systems or build custom workflows, our API has you covered.
              </p>
              <p className="text-lg text-slate-600 mb-8">
                Comprehensive documentation and SDKs make integration quick and easy.
              </p>
              <ul className="space-y-4">
                {apiFeatures.map((feature, index) => (
                  <li key={index} className="flex items-center gap-3">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                    <span className="text-slate-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-slate-900 rounded-xl p-8">
              <h3 className="text-lg font-semibold text-white mb-4">API Example</h3>
              <div className="bg-slate-800 rounded-lg p-4 overflow-x-auto">
                <pre className="text-sm text-slate-300">
{`// Get student list
const response = await fetch(
  'https://api.schoolops.io/v1/students',
  {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY',
      'Content-Type': 'application/json'
    }
  }
);

const students = await response.json();
console.log(students);`}
                </pre>
              </div>
              <div className="mt-4 flex gap-3">
                <Link
                  href="#"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  View Documentation
                </Link>
                <Link
                  href="#"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-slate-700 text-white text-sm font-semibold rounded-lg hover:bg-slate-600 transition-colors"
                >
                  Get API Key
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Custom Integration */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-indigo-600 rounded-2xl p-8 md:p-16 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Need a Custom Integration?</h2>
            <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
              Our team can help you build custom integrations tailored to your specific needs. Contact us to discuss your requirements.
            </p>
            <Link
              href="/contact"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-slate-100 transition-colors"
            >
              Contact Our Team
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Benefits of Integration</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Streamline your operations and reduce manual work
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: 'Save Time', desc: 'Automate data entry and reduce manual work by connecting your systems', icon: Clock },
              { title: 'Reduce Errors', desc: 'Eliminate data duplication and transcription errors with automated sync', icon: CheckCircle2 },
              { title: 'Improve Experience', desc: 'Provide better experiences for parents, teachers, and students', icon: Users },
            ].map((benefit, index) => (
              <div key={index} className="bg-white rounded-xl p-8 text-center">
                <div className="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center mx-auto mb-6">
                  <benefit.icon className="w-7 h-7 text-indigo-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{benefit.title}</h3>
                <p className="text-slate-600">{benefit.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-slate-900 mb-4">Ready to Connect?</h2>
          <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
            Start integrating SchoolOps with your favorite tools today
          </p>
          <Link
            href="/register"
            className="inline-flex items-center gap-2 px-8 py-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors"
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
