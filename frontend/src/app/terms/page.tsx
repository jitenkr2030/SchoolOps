import Link from 'next/link';
import { GraduationCap, Mail, Phone, MapPin, FileText, CheckCircle, AlertCircle } from 'lucide-react';

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center">
                <FileText className="w-7 h-7 text-white" />
              </div>
              <h1 className="text-4xl font-bold">Terms of Service</h1>
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
              These Terms of Service (&quot;Terms&quot;) govern your access to and use of SchoolOps&apos;s school management platform and related services. By accessing or using our Services, you agree to be bound by these Terms.
            </p>

            <div className="bg-amber-50 border border-amber-200 rounded-xl p-6 mb-8">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-semibold text-amber-800 mb-2">Important Notice</h3>
                  <p className="text-amber-700">
                    By creating an account or using SchoolOps services, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service and our Privacy Policy.
                  </p>
                </div>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-slate-600 mb-4">
              By accessing or using SchoolOps services, you accept and agree to be bound by these Terms and our Privacy Policy. If you are using our Services on behalf of an organization, you represent that you have the authority to bind that organization to these Terms.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">2. Description of Services</h2>
            <p className="text-slate-600 mb-4">
              SchoolOps provides a cloud-based school management platform that includes:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Student information management</li>
              <li>Attendance tracking and timetable management</li>
              <li>Academic and assessment tools</li>
              <li>Fee management and financial reporting</li>
              <li>Communication tools for parents and staff</li>
              <li>AI-powered analytics and insights</li>
              <li>Mobile applications for iOS and Android</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">3. Account Registration</h2>
            <p className="text-slate-600 mb-4">
              To use our Services, you must create an account. When you register, you agree to:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Provide accurate, current, and complete information</li>
              <li>Maintain the security of your password and account</li>
              <li>Accept responsibility for all activities under your account</li>
              <li>Notify us immediately of any unauthorized use</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">4. Acceptable Use</h2>
            <p className="text-slate-600 mb-4">
              You agree NOT to:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Use the Services for any illegal purpose or in violation of any laws</li>
              <li>Upload, transmit, or distribute viruses or malicious code</li>
              <li>Attempt to gain unauthorized access to our systems or networks</li>
              <li>Reverse engineer, decompile, or attempt to derive source code</li>
              <li>Copy, modify, or distribute any part of the Services without permission</li>
              <li>Use the Services to store or transmit infringing, libelous, or unlawful content</li>
              <li>Resell, lease, or sublicense the Services without our written consent</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">5. Subscription and Payment</h2>
            <div className="bg-slate-50 rounded-xl p-6 mb-6">
              <h3 className="text-lg font-semibold text-slate-900 mb-4">Subscription Terms</h3>
              <ul className="list-disc pl-6 space-y-2 text-slate-600">
                <li>Subscriptions are billed monthly or annually as selected</li>
                <li>All prices are subject to change with 30 days notice</li>
                <li>Refunds are available within 14 days of purchase for new subscriptions</li>
                <li>Accounts are charged regardless of usage levels</li>
                <li>You may cancel your subscription at any time</li>
              </ul>
            </div>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">6. Data Ownership and Rights</h2>
            <p className="text-slate-600 mb-4">
              <strong>Your Data:</strong> You retain all ownership rights to the data you upload to our platform. You grant SchoolOps a license to use, store, and process your data solely for the purpose of providing our Services.
            </p>
            <p className="text-slate-600 mb-4">
              <strong>SchoolOps Data:</strong> SchoolOps owns all rights, title, and interest in and to the Services, including all software, technology, and documentation.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">7. Data Processing Agreement</h2>
            <p className="text-slate-600 mb-4">
              For educational institutions subject to FERPA (Family Educational Rights and Privacy Act) and similar regulations, SchoolOps acts as a &quot;School Official&quot; with legitimate educational interests in the data processed. We:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Perform under the direct control of the educational institution</li>
              <li>Use the data only for educational purposes as specified by the institution</li>
              <li>Do not redisclose personally identifiable information without consent</li>
              <li>Maintain reasonable data security measures</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">8. Service Level Agreement</h2>
            <div className="bg-indigo-50 rounded-xl p-6 mb-6">
              <div className="flex items-center gap-3 mb-4">
                <CheckCircle className="w-8 h-8 text-indigo-600" />
                <h3 className="text-lg font-semibold text-indigo-900">99.9% Uptime Guarantee</h3>
              </div>
              <p className="text-indigo-700">
                We guarantee that our Services will be available 99.9% of the time in any calendar month, excluding scheduled maintenance. In the event of unplanned downtime, service credits will be provided according to our SLA policy.
              </p>
            </div>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">9. Limitation of Liability</h2>
            <p className="text-slate-600 mb-4">
              To the maximum extent permitted by law, SchoolOps shall not be liable for:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Any indirect, incidental, special, consequential, or punitive damages</li>
              <li>Loss of profits, revenue, data, or business opportunities</li>
              <li>Service interruptions or data loss</li>
              <li>Actions of third parties</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">10. Warranty Disclaimer</h2>
            <p className="text-slate-600 mb-4">
              THE SERVICES ARE PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED. SchoolOps does not warrant that the Services will be uninterrupted, timely, secure, or error-free.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">11. Termination</h2>
            <p className="text-slate-600 mb-4">
              Either party may terminate this agreement:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li><strong>By You:</strong> Cancel your subscription at any time through your account settings.</li>
              <li><strong>By SchoolOps:</strong> Terminate or suspend access for violations of these Terms.</li>
              <li><strong>Upon Expiry:</strong> When your subscription period ends without renewal.</li>
            </ul>
            <p className="text-slate-600 mb-4">
              Upon termination, you will have access to export your data for 30 days.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">12. Governing Law and Disputes</h2>
            <p className="text-slate-600 mb-4">
              These Terms are governed by the laws of India. Any disputes will be resolved through:
            </p>
            <ul className="list-disc pl-6 space-y-2 text-slate-600 mb-6">
              <li>Good-faith negotiation between parties</li>
              <li>Binding arbitration in Bangalore, Karnataka if negotiation fails</li>
              <li>Courts of Bangalore, Karnataka for injunctive relief</li>
            </ul>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">13. Changes to Terms</h2>
            <p className="text-slate-600 mb-4">
              We may modify these Terms at any time. Material changes will be notified via email or in-app notification at least 30 days before they take effect. Continued use after changes constitutes acceptance of the new Terms.
            </p>

            <h2 className="text-2xl font-bold text-slate-900 mb-4">14. Contact Information</h2>
            <div className="bg-slate-50 rounded-lg p-6">
              <p className="text-slate-700 font-medium mb-2">SchoolOps Technologies Pvt Ltd</p>
              <p className="text-slate-600 flex items-center gap-2">
                <Mail className="w-4 h-4" /> legal@schoolops.com
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
