import Link from 'next/link';
import { GraduationCap, ArrowRight, CheckCircle2, Users, Award, MapPin, Mail, Phone } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">About SchoolOps</h1>
            <p className="text-xl text-slate-300">
              We&apos;re on a mission to transform school management with AI-powered solutions that help educators focus on what matters most — teaching and student success.
            </p>
          </div>
        </div>
      </header>

      {/* Our Story */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Our Story</h2>
              <p className="text-lg text-slate-600 mb-4">
                SchoolOps was founded in 2020 by a team of educators and technologists who saw firsthand the administrative burden facing schools today. Teachers were spending more time on paperwork than teaching, and administrators were struggling with disconnected systems.
              </p>
              <p className="text-lg text-slate-600 mb-4">
                We set out to build a comprehensive school management platform that would automate routine tasks, improve communication between schools and parents, and provide actionable insights through artificial intelligence.
              </p>
              <p className="text-lg text-slate-600">
                Today, SchoolOps serves over 500 schools across India and around the world, helping them save time, reduce costs, and improve educational outcomes for millions of students.
              </p>
            </div>
            <div className="bg-slate-100 rounded-2xl p-8">
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">500+</div>
                  <div className="text-slate-600">Schools</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">50K+</div>
                  <div className="text-slate-600">Students</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">5K+</div>
                  <div className="text-slate-600">Teachers</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-indigo-600 mb-2">25+</div>
                  <div className="text-slate-600">Countries</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Our Values */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Our Values</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              These core principles guide everything we do at SchoolOps
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
                <Users className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Student-Centered</h3>
              <p className="text-slate-600">
                Every feature we build is designed with students in mind. We believe technology should enhance the learning experience, not distract from it.
              </p>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-6">
                <CheckCircle2 className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Excellence</h3>
              <p className="text-slate-600">
                We strive for excellence in everything we do, from the quality of our code to the responsiveness of our customer support.
              </p>
            </div>
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mb-6">
                <Award className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Innovation</h3>
              <p className="text-slate-600">
                We continuously push the boundaries of what&apos;s possible, leveraging AI and emerging technologies to solve old problems in new ways.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Leadership Team */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Leadership Team</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Meet the team behind SchoolOps
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-32 h-32 bg-slate-200 rounded-full mx-auto mb-6 flex items-center justify-center">
                <GraduationCap className="w-16 h-16 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Dr. Sarah Johnson</h3>
              <p className="text-indigo-600 mb-2">CEO & Co-Founder</p>
              <p className="text-slate-600 text-sm">Former principal with 15+ years in education administration</p>
            </div>
            <div className="text-center">
              <div className="w-32 h-32 bg-slate-200 rounded-full mx-auto mb-6 flex items-center justify-center">
                <GraduationCap className="w-16 h-16 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Rahul Sharma</h3>
              <p className="text-indigo-600 mb-2">CTO & Co-Founder</p>
              <p className="text-slate-600 text-sm">Ex-Google engineer with expertise in AI and machine learning</p>
            </div>
            <div className="text-center">
              <div className="w-32 h-32 bg-slate-200 rounded-full mx-auto mb-6 flex items-center justify-center">
                <GraduationCap className="w-16 h-16 text-slate-400" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900">Priya Patel</h3>
              <p className="text-indigo-600 mb-2">Head of Product</p>
              <p className="text-slate-600 text-sm">Education technology veteran with experience at major edtech companies</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Transform Your School?</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            Join 500+ schools already using SchoolOps to streamline operations
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
