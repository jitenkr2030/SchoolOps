import Link from 'next/link';
import { GraduationCap, ArrowRight, Calendar, User, MapPin, Mail, Phone } from 'lucide-react';

const blogPosts = [
  {
    id: 1,
    title: 'How AI is Transforming School Management',
    excerpt: 'Discover how artificial intelligence is revolutionizing the way schools handle attendance, grading, and parent communication.',
    author: 'Dr. Sarah Johnson',
    role: 'CEO & Co-Founder',
    date: 'January 8, 2025',
    category: 'AI in Education',
    image: 'bg-indigo-100',
  },
  {
    id: 2,
    title: '5 Ways to Improve Parent-Teacher Communication',
    excerpt: 'Effective communication between parents and teachers is crucial for student success. Learn how technology can help bridge the gap.',
    author: 'Priya Patel',
    role: 'Head of Product',
    date: 'January 5, 2025',
    category: 'Best Practices',
    image: 'bg-emerald-100',
  },
  {
    id: 3,
    title: 'The Future of Digital Assessment in Schools',
    excerpt: 'Traditional exams are evolving. Explore how online assessments and auto-grading are changing the way we evaluate student performance.',
    author: 'Rahul Sharma',
    role: 'CTO & Co-Founder',
    date: 'January 2, 2025',
    category: 'Technology',
    image: 'bg-amber-100',
  },
  {
    id: 4,
    title: 'Streamlining Fee Collection with Online Payments',
    excerpt: 'Cash handling is outdated. Learn how schools are reducing administrative burden and improving cash flow with digital payment solutions.',
    author: 'Amit Kumar',
    role: 'Customer Success Manager',
    date: 'December 28, 2024',
    category: 'Finance',
    image: 'bg-blue-100',
  },
  {
    id: 5,
    title: 'Building a Culture of Data-Driven Decision Making',
    excerpt: 'Schools collect vast amounts of data. Learn how to leverage analytics to make informed decisions that improve outcomes.',
    author: 'Dr. Sarah Johnson',
    role: 'CEO & Co-Founder',
    date: 'December 25, 2024',
    category: 'Analytics',
    image: 'bg-purple-100',
  },
  {
    id: 6,
    title: 'The Role of Mobile Apps in Modern Education',
    excerpt: 'Mobile apps are becoming essential tools for schools. Discover how they enhance communication and keep everyone connected.',
    author: 'Neha Sharma',
    role: 'Product Designer',
    date: 'December 22, 2024',
    category: 'Mobile',
    image: 'bg-pink-100',
  },
];

const categories = [
  'All Posts',
  'AI in Education',
  'Best Practices',
  'Technology',
  'Finance',
  'Analytics',
  'Mobile',
  'Security',
];

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">SchoolOps Blog</h1>
            <p className="text-xl text-slate-300">
              Insights, tips, and stories from the world of education technology
            </p>
          </div>
        </div>
      </header>

      {/* Categories */}
      <section className="py-8 border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap gap-4 justify-center">
            {categories.map((category, index) => (
              <button
                key={index}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  index === 0
                    ? 'bg-indigo-600 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Post */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-slate-900 rounded-2xl overflow-hidden">
            <div className="grid md:grid-cols-2">
              <div className="bg-indigo-100 min-h-[300px] flex items-center justify-center">
                <GraduationCap className="w-24 h-24 text-indigo-600" />
              </div>
              <div className="p-8 md:p-12 flex flex-col justify-center">
                <span className="inline-block px-3 py-1 bg-indigo-600 text-white text-xs font-medium rounded-full mb-4 w-fit">
                  {blogPosts[0].category}
                </span>
                <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
                  {blogPosts[0].title}
                </h2>
                <p className="text-slate-300 mb-6 text-lg">
                  {blogPosts[0].excerpt}
                </p>
                <div className="flex items-center gap-4 text-sm text-slate-400 mb-6">
                  <span className="flex items-center gap-1">
                    <User className="w-4 h-4" /> {blogPosts[0].author}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" /> {blogPosts[0].date}
                  </span>
                </div>
                <Link
                  href="/blog/how-ai-is-transforming-school-management"
                  className="inline-flex items-center gap-2 text-white font-semibold hover:text-indigo-300 transition-colors"
                >
                  Read More
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Blog Grid */}
      <section className="py-16 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {blogPosts.slice(1).map((post, index) => (
              <div key={index} className="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <div className={`${post.image} h-48 flex items-center justify-center`}>
                  <GraduationCap className="w-16 h-16 text-slate-600" />
                </div>
                <div className="p-6">
                  <span className="inline-block px-3 py-1 bg-slate-100 text-indigo-600 text-xs font-medium rounded-full mb-3">
                    {post.category}
                  </span>
                  <h3 className="text-xl font-semibold text-slate-900 mb-3 hover:text-indigo-600 transition-colors">
                    <Link href={`/blog/${post.title.toLowerCase().replace(/\s+/g, '-')}`}>
                      {post.title}
                    </Link>
                  </h3>
                  <p className="text-slate-600 mb-4 line-clamp-2">
                    {post.excerpt}
                  </p>
                  <div className="flex items-center justify-between text-sm text-slate-500">
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" /> {post.author.split(' ')[0]}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" /> {post.date}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-indigo-600 rounded-2xl p-8 md:p-16 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Stay Updated</h2>
            <p className="text-xl text-indigo-100 mb-8 max-w-2xl mx-auto">
              Subscribe to our newsletter to get the latest insights and updates delivered to your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
              <input
                type="email"
                placeholder="Enter your email"
                className="flex-1 px-6 py-3 rounded-lg text-slate-900 outline-none focus:ring-2 focus:ring-white"
              />
              <button className="px-8 py-3 bg-slate-900 text-white font-semibold rounded-lg hover:bg-slate-800 transition-colors">
                Subscribe
              </button>
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
