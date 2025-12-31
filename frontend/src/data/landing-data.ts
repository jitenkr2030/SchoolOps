// Landing page content data - easy to edit and maintain

export const LANDING_CONFIG = {
  meta: {
    title: 'SchoolOps - Smart School Management System',
    description: 'Automate school operations with AI-powered features for attendance, academics, fees, and communication.',
    keywords: 'school management, education software, attendance tracking, fee management',
  },
  
  hero: {
    headline: 'Transform Your School Operations with AI-Powered Management',
    subheadline: 'The complete school management system that automates administrative tasks, enhances parent-teacher communication, and delivers AI-driven insights for better educational outcomes.',
    primaryCTA: 'Start Free Trial',
    primaryCTALink: '/register',
    secondaryCTA: 'Watch Demo',
    secondaryCTALink: '/demo',
    stats: [
      { value: '500+', label: 'Schools' },
      { value: '50K+', label: 'Students' },
      { value: '99.9%', label: 'Uptime' },
      { value: '4.9/5', label: 'Rating' },
    ],
  },

  features: {
    title: 'Everything You Need to Manage Your School',
    subtitle: 'From admission to alumni, SchoolOps covers every aspect of school administration',
    
    coreModules: [
      {
        icon: 'school',
        title: 'Admin & Setup',
        description: 'School profiles, RBAC, bulk import, multi-branch support',
        color: '#4F46E5',
      },
      {
        icon: 'account-child',
        title: 'Student Information',
        description: 'Complete student profiles, enrollment workflows, custom attributes',
        color: '#10B981',
      },
      {
        icon: 'calendar-check',
        title: 'Attendance & Timetable',
        description: 'Daily tracking, auto-scheduling, absence notifications',
        color: '#F59E0B',
      },
      {
        icon: 'book-open-variant',
        title: 'Academics & Assessment',
        description: 'Lesson plans, online exams, auto-grading, gradebooks',
        color: '#8B5CF6',
      },
      {
        icon: 'message-text',
        title: 'Communication',
        description: 'Announcements, chat, parent-teacher meetings',
        color: '#EC4899',
      },
      {
        icon: 'cash-multiple',
        title: 'Fees & Finance',
        description: 'Fee plans, online payments, financial reports',
        color: '#06B6D4',
      },
      {
        icon: 'bus-school',
        title: 'Transport & Hostel',
        description: 'GPS tracking, room allocation, mess billing',
        color: '#84CC16',
      },
      {
        icon: 'library',
        title: 'Library & Inventory',
        description: 'Catalog management, checkouts, asset tracking',
        color: '#F97316',
      },
      {
        icon: 'account-tie',
        title: 'Staff & Payroll',
        description: 'Employee management, salary processing, performance reviews',
        color: '#6366F1',
      },
      {
        icon: 'chart-bar',
        title: 'Reports & Dashboards',
        description: 'Real-time analytics, custom reports, exports',
        color: '#14B8A6',
      },
    ],

    aiFeatures: [
      {
        icon: 'brain',
        title: 'Analytics & Predictions',
        description: 'At-risk student detection, enrollment forecasting, fee churn prediction',
        color: '#4F46E5',
        badge: 'AI-Powered',
      },
      {
        icon: 'lightbulb-on',
        title: 'Personalization',
        description: 'Adaptive learning paths, smart recommendations, remedial assignments',
        color: '#10B981',
        badge: 'AI-Powered',
      },
      {
        icon: 'robot',
        title: 'Automation Assistants',
        description: 'AI quiz generation, auto-grading, smart notifications',
        color: '#F59E0B',
        badge: 'AI-Powered',
      },
      {
        icon: 'translate',
        title: 'NLP Chatbot',
        description: 'Multilingual support, voice assistant, automated responses',
        color: '#8B5CF6',
        badge: 'AI-Powered',
      },
      {
        icon: 'eye',
        title: 'Document Intelligence',
        description: 'OCR processing, receipt scanning, ID verification',
        color: '#EC4899',
        badge: 'AI-Powered',
      },
      {
        icon: 'route',
        title: 'Resource Optimization',
        description: 'Timetable optimization, bus route planning',
        color: '#06B6D4',
        badge: 'AI-Powered',
      },
    ],
  },

  userRoles: [
    {
      id: 'admin',
      title: 'Administrators',
      icon: 'shield-account',
      description: 'Complete control over school operations',
      features: [
        'Multi-school management',
        'Role-based access control',
        'Financial dashboards',
        'Staff management',
        'System configuration',
        'Comprehensive reports',
      ],
      color: '#4F46E5',
    },
    {
      id: 'teacher',
      title: 'Teachers',
      icon: 'teach',
      description: 'Simplified classroom management',
      features: [
        'Digital attendance taking',
        'Grade management',
        'Homework assignment',
        'Parent communication',
        'Class performance analytics',
        'Lesson plan templates',
      ],
      color: '#10B981',
    },
    {
      id: 'student',
      title: 'Students',
      icon: 'school',
      description: 'Access to all academic resources',
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
    {
      id: 'parent',
      title: 'Parents',
      icon: 'account-group',
        description: 'Stay connected with your child\'s education',
      features: [
        'Real-time attendance alerts',
        'Academic progress tracking',
        'Fee payment portal',
        'Teacher messaging',
        'Event notifications',
        'Homework monitoring',
      ],
      color: '#8B5CF6',
    },
  ],

  testimonials: [
    {
      id: 1,
      name: 'Dr. Sarah Johnson',
      role: 'Principal',
      school: 'Springfield High School',
      avatar: 'SJ',
      content: 'SchoolOps has transformed how we manage our school. The AI-powered insights help us identify at-risk students early, and the automation saves our staff hours every week.',
      rating: 5,
      color: '#4F46E5',
    },
    {
      id: 2,
      name: 'Mr. Rahul Sharma',
      role: 'Mathematics Teacher',
      school: 'Delhi Public School',
      avatar: 'RS',
      content: 'Taking attendance and managing grades has never been easier. The parent communication feature has significantly improved engagement with families.',
      rating: 5,
      color: '#10B981',
    },
    {
      id: 3,
      name: 'Mrs. Priya Patel',
      role: 'Parent',
      school: 'Parent Representative',
      avatar: 'PP',
      content: 'I love being able to track my child\'s attendance and grades in real-time. The app notifications keep me informed about school events and homework.',
      rating: 5,
      color: '#F59E0B',
    },
  ],

  pricing: [
    {
      id: 'starter',
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
      ],
      cta: 'Get Started',
      popular: false,
      color: '#6B7280',
    },
    {
      id: 'professional',
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
      ],
      cta: 'Start Free Trial',
      popular: true,
      color: '#4F46E5',
    },
    {
      id: 'enterprise',
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
      ],
      cta: 'Contact Sales',
      popular: false,
      color: '#1F2937',
    },
  ],

  faqs: [
    {
      id: 1,
      question: 'How long does it take to implement SchoolOps?',
      answer: 'Implementation typically takes 2-4 weeks depending on the size of your institution. Our team handles data migration, setup, and staff training.',
    },
    {
      id: 2,
      question: 'Can I try SchoolOps before purchasing?',
      answer: 'Yes! We offer a 14-day free trial with full access to all features. No credit card required.',
    },
    {
      id: 3,
      question: 'Is my data secure with SchoolOps?',
      answer: 'Absolutely. We use bank-level encryption, regular security audits, and comply with data protection regulations. Your data is backed up daily.',
    },
    {
      id: 4,
      question: 'Do you offer mobile apps?',
      answer: 'Yes, we have native iOS and Android apps for teachers, students, and parents. All apps sync in real-time with the web dashboard.',
    },
    {
      id: 5,
      question: 'What support options are available?',
      answer: 'All plans include email support. Professional and Enterprise plans get priority phone support and dedicated account managers.',
    },
    {
      id: 6,
      question: 'Can SchoolOps integrate with our existing systems?',
      answer: 'Yes, we offer APIs and pre-built integrations with popular payment gateways, SMS services, and authentication systems.',
    },
  ],

  cta: {
    title: 'Ready to Transform Your School?',
    subheadline: 'Join 500+ schools already using SchoolOps to streamline operations and improve outcomes.',
    buttonText: 'Start Your Free Trial',
    buttonLink: '/register',
  },

  footer: {
    company: {
      name: 'SchoolOps',
      description: 'Smart school management powered by AI',
      social: {
        twitter: 'https://twitter.com/schoolops',
        linkedin: 'https://linkedin.com/company/schoolops',
        facebook: 'https://facebook.com/schoolops',
      },
    },
    product: [
      { label: 'Features', href: '#features' },
      { label: 'Pricing', href: '#pricing' },
      { label: 'AI Features', href: '#ai-features' },
      { label: 'Mobile App', href: '#mobile' },
      { label: 'Integrations', href: '#integrations' },
    ],
    companyLinks: [
      { label: 'About Us', href: '/about' },
      { label: 'Careers', href: '/careers' },
      { label: 'Blog', href: '/blog' },
      { label: 'Contact', href: '/contact' },
    ],
    legal: [
      { label: 'Privacy Policy', href: '/privacy' },
      { label: 'Terms of Service', href: '/terms' },
      { label: 'Data Security', href: '/security' },
    ],
  },
};

export const formatPrice = (price: number, currency: string = '₹'): string => {
  return `${currency}${price.toLocaleString('en-IN')}`;
};

export const calculateYearlyDiscount = (monthly: number, yearly: number): number => {
  return Math.round(((monthly * 12 - yearly) / (monthly * 12)) * 100);
};
