import Link from 'next/link';
import { GraduationCap, Mail, Phone, MapPin, Shield, Lock, Eye, Database } from 'lucide-react';

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                <Shield className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-4xl font-bold">Privacy Policy</h1>
            </div>
            <p className="text-xl text-slate-300">
              Last updated: January 10, 2025
            </p>
          </div>
        </div>
      </header>

      {/* Content */}
      <section className="py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="prose prose-lg prose-slate max-w-none">
            <p className="text-lg text-slate-600 mb-8">
              At SchoolOps, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our school management platform and related services.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Information We Collect</h2>
            <p className="text-slate-600 mb-4">
              We collect information you provide directly to us and information collected automatically when you use our Services.
            </p>

            <h3 className="text-xl font-semibold text-slate-900 mb-3">Information You Provide</h3>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li><strong>Account Information:</strong> Name, email address, phone number, job title, and organization name when you create an account.</li>
              <li><strong>School Data:</strong> Information about your school including school name, address, and administrative details.</li>
              <li><strong>Student and Staff Data:</strong> Information you upload to the platform including student records, attendance data, grades, and employee information.</li>
              <li><strong>Communication Data:</strong> Messages, feedback, and communications you send through our platform.</li>
            </ul>

            <h3 className="text-xl font-semibold text-slate-900 mb-3">Information Collected Automatically</h3>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li><strong>Usage Data:</strong> Information about how you use our Services, including features accessed, time spent, and pages visited.</li>
              <li><strong>Device Information:</strong> Device type, operating system, browser type, and IP address.</li>
              <li><strong>Cookies and Tracking Technologies:</strong> We use cookies and similar technologies to collect information about your browsing activities.</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">2. How We Use Your Information</h2>
            <p className="text-slate-600 mb-4">
              We use the information we collect to provide, maintain, and improve our Services:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Provide and deliver the school management services you request</li>
              <li>Process transactions and send related information</li>
              <li>Send you technical notices, updates, security alerts, and support messages</li>
              <li>Respond to your comments, questions, and requests</li>
              <li>Provide customer service and support</li>
              <li>Monitor and analyze trends, usage, and activities in connection with our Services</li>
              <li>Detect, investigate, and prevent fraudulent transactions and other illegal activities</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">3. Data Sharing and Disclosure</h2>
            <p className="text-slate-600 mb-4">
              We do not sell your personal information. We may share your information in the following circumstances:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li><strong>With Service Providers:</strong> We share information with third-party vendors who perform services on our behalf.</li>
              <li><strong>With Your Consent:</strong> We may share information when you authorize us to do so.</li>
              <li><strong>Legal Requirements:</strong> We may disclose information if required by law or in response to valid legal requests.</li>
              <li><strong>Business Transfers:</strong> We may transfer information in connection with a merger, acquisition, or sale of assets.</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">4. Data Security</h2>
            <div className="bg-slate-50 rounded-xl p-6 mb-6">
              <div className="flex items-start gap-4">
                <Lock className="w-8 h-8 text-indigo-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">Bank-Level Security</h3>
                  <p className="text-slate-600">
                    We implement industry-standard security measures including 256-bit encryption, regular security audits, and compliance with international data protection standards. Your data is stored in secure data centers with redundant backups.
                  </p>
                </div>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">5. Data Retention</h2>
            <p className="text-slate-600 mb-4">
              We retain your information for as long as your account is active or as needed to provide you services. After termination of your account, we may retain certain information for legitimate business purposes or as required by law.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">6. Your Rights</h2>
            <p className="text-slate-600 mb-4">
              Depending on your location, you may have certain rights regarding your personal information:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Right to access and receive a copy of your personal data</li>
              <li>Right to rectify inaccurate personal data</li>
              <li>Right to request deletion of your personal data</li>
              <li>Right to restrict processing of your personal data</li>
              <li>Right to data portability</li>
              <li>Right to object to processing</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">7. Children&apos;s Privacy</h2>
            <p className="text-slate-600 mb-4">
              SchoolOps is designed for educational institutions and may contain information about minors. We comply with applicable laws regarding the collection of information from children, including FERPA in the United States and similar regulations in other jurisdictions.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">8. International Data Transfers</h2>
            <p className="text-slate-600 mb-4">
              Your information may be transferred to and processed in countries other than your country of residence. These countries may have data protection laws that are different from the laws of your country.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">9. Changes to This Policy</h2>
            <p className="text-slate-600 mb-4">
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the &quot;Last updated&quot; date.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">10. Contact Us</h2>
            <p className="text-slate-600 mb-4">
              If you have any questions about this Privacy Policy or our data practices, please contact us:
            </p>
            <div className="bg-slate-50 rounded-lg p-6">
              <p className="text-slate-700 font-medium mb-2">SchoolOps Technologies Pvt Ltd</p>
              <p className="text-slate-600 flex items-center gap-2">
                <Mail className="w-4 h-4" /> privacy@schoolops.com
              </p>
              <p className="text-slate-600 flex items-center gap-2">
                <Phone className="w-4 h-4" /> +91 1800 123 4567
              </p>
              <p className="text-slate-600 flex items-center gap-2">
                <MapPin className="w-4 h-4" /> Bangalore, Karnataka, India
              </p>
            </div>
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
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Data Security</Link></li>
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
