import Link from 'next/link';
import { GraduationCap, ArrowRight, MapPin, Mail, Phone, Briefcase, Clock, DollarSign } from 'lucide-react';

const openPositions = [
  {
    title: 'Senior Software Engineer',
    department: 'Engineering',
    location: 'Bangalore, India',
    type: 'Full-time',
    description: 'Build and maintain our school management platform using React, Node.js, and modern technologies.',
    requirements: [
      '3+ years of experience with React and Node.js',
      'Experience with PostgreSQL and Redis',
      'Strong problem-solving skills',
      'Good communication skills',
    ],
  },
  {
    title: 'Product Manager',
    department: 'Product',
    location: 'Bangalore, India',
    type: 'Full-time',
    description: 'Lead the product vision and roadmap for SchoolOps, working closely with engineering and design teams.',
    requirements: [
      '2+ years of product management experience',
      'Experience in SaaS products',
      'Strong analytical skills',
      'Ability to communicate with technical and non-technical stakeholders',
    ],
  },
  {
    title: 'Customer Success Manager',
    department: 'Customer Success',
    location: 'Remote / Bangalore',
    type: 'Full-time',
    description: 'Help our customers get the most out of SchoolOps through onboarding, training, and ongoing support.',
    requirements: [
      '2+ years in customer success or account management',
      'Experience in EdTech is a plus',
      'Excellent communication skills',
      'Passion for helping others succeed',
    ],
  },
  {
    title: 'DevOps Engineer',
    department: 'Engineering',
    location: 'Bangalore, India',
    type: 'Full-time',
    description: 'Manage and improve our cloud infrastructure on AWS, ensuring reliability and scalability.',
    requirements: [
      '2+ years of DevOps experience',
      'Experience with AWS, Kubernetes, and Terraform',
      'Strong scripting skills (Python/Bash)',
      'Experience with CI/CD pipelines',
    ],
  },
  {
    title: 'UX Designer',
    department: 'Design',
    location: 'Bangalore, India',
    type: 'Full-time',
    description: 'Create beautiful, intuitive interfaces for our school management platform.',
    requirements: [
      '2+ years of UX design experience',
      'Proficiency in Figma and design systems',
      'Strong portfolio demonstrating user-centered design',
      'Experience with design research',
    ],
  },
  {
    title: 'Sales Representative',
    department: 'Sales',
    location: 'Mumbai, India',
    type: 'Full-time',
    description: 'Drive new business by reaching out to schools and demonstrating the value of SchoolOps.',
    requirements: [
      '1+ years of sales experience',
      'Strong communication and presentation skills',
      'Ability to work independently',
      'Passion for sales and technology',
    ],
  },
];

export default function CareersPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">Join Our Team</h1>
            <p className="text-xl text-slate-300">
              Help us transform education with technology. We&apos;re looking for passionate individuals to join our mission.
            </p>
          </div>
        </div>
      </header>

      {/* Why Join Us */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Why Work at SchoolOps?</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              We offer a dynamic work environment where you can make a real impact
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-50 rounded-xl p-8">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-6">
                <Briefcase className="w-6 h-6 text-indigo-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Meaningful Work</h3>
              <p className="text-slate-600">
                Every line of code you write and every decision you make directly impacts schools, teachers, and students worldwide.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-8">
              <div className="w-12 h-12 bg-emerald-100 rounded-lg flex items-center justify-center mb-6">
                <Clock className="w-6 h-6 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Flexible Work</h3>
              <p className="text-slate-600">
                We offer flexible working hours, remote work options, and a healthy work-life balance to help you do your best work.
              </p>
            </div>
            <div className="bg-slate-50 rounded-xl p-8">
              <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mb-6">
                <DollarSign className="w-6 h-6 text-amber-600" />
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">Competitive Benefits</h3>
              <p className="text-slate-600">
                Competitive salaries, equity packages, health insurance, and learning & development opportunities.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Open Positions */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Open Positions</h2>
            <p className="text-lg text-slate-600 max-w-2xl mx-auto">
              Find your next role at SchoolOps
            </p>
          </div>
          <div className="space-y-6">
            {openPositions.map((position, index) => (
              <div key={index} className="bg-white rounded-xl p-8 shadow-sm">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-slate-900">{position.title}</h3>
                    <div className="flex flex-wrap gap-4 mt-2 text-sm text-slate-500">
                      <span className="flex items-center gap-1">
                        <Briefcase className="w-4 h-4" /> {position.department}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" /> {position.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" /> {position.type}
                      </span>
                    </div>
                  </div>
                  <Link
                    href={`/careers/${position.title.toLowerCase().replace(/\s+/g, '-')}`}
                    className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Apply Now
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
                <p className="text-slate-600 mb-4">{position.description}</p>
                <div>
                  <h4 className="text-sm font-semibold text-slate-900 mb-2">Requirements:</h4>
                  <ul className="grid md:grid-cols-2 gap-2">
                    {position.requirements.map((req, reqIndex) => (
                      <li key={reqIndex} className="flex items-center gap-2 text-sm text-slate-600">
                        <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
                        {req}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Culture */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 mb-6">Our Culture</h2>
              <p className="text-lg text-slate-600 mb-4">
                At SchoolOps, we believe that a great culture is the foundation of a successful company. We foster an environment of collaboration, continuous learning, and mutual respect.
              </p>
              <p className="text-lg text-slate-600 mb-4">
                We celebrate diversity and inclusion, knowing that different perspectives make us stronger. Our team comes from various backgrounds, united by a shared passion for education and technology.
              </p>
              <p className="text-lg text-slate-600">
                We encourage experimentation and learning from failures. Every team member has the opportunity to grow, take on new challenges, and make a meaningful contribution to our mission.
              </p>
            </div>
            <div className="bg-slate-100 rounded-2xl p-8">
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-indigo-600 mb-2">50+</div>
                  <div className="text-slate-600">Team Members</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-indigo-600 mb-2">12</div>
                  <div className="text-slate-600">States Represented</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-indigo-600 mb-2">4.9</div>
                  <div className="text-slate-600">Glassdoor Rating</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-indigo-600 mb-2">95%</div>
                  <div className="text-slate-600">Employee Retention</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-indigo-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Don&apos;t See the Right Fit?</h2>
          <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
            We&apos;re always looking for talented people to join our team. Send us your resume and we&apos;ll keep you in mind for future opportunities.
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-indigo-600 font-semibold rounded-xl hover:bg-slate-100 transition-colors"
          >
            Get in Touch
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
