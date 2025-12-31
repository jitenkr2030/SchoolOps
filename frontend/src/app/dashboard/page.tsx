'use client'

import React from 'react'
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  Calendar,
  BookOpen,
  DollarSign,
  Bus,
  Library,
  BarChart3,
  MessageSquare,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  Search,
  Sparkles,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import Link from 'next/link'

// Mock data for demonstration
const stats = [
  { label: 'Total Students', value: '2,847', change: '+12%', positive: true, icon: Users, color: 'primary' },
  { label: 'Teachers', value: '156', change: '+5%', positive: true, icon: GraduationCap, color: 'success' },
  { label: 'Attendance Rate', value: '94.2%', change: '+2.1%', positive: true, icon: Calendar, color: 'secondary' },
  { label: 'Fee Collection', value: '$1.2M', change: '-3%', positive: false, icon: DollarSign, color: 'warning' },
]

const recentActivities = [
  { id: 1, icon: '👨‍🎓', text: 'New student enrolled: Emily Brown', time: '5 min ago', type: 'success' },
  { id: 2, icon: '💰', text: 'Fee payment received: $550 from John Smith', time: '15 min ago', type: 'success' },
  { id: 3, icon: '📊', text: 'AI Report: 5 students flagged as at-risk', time: '1 hour ago', type: 'warning' },
  { id: 4, icon: '📚', text: 'New assignment posted by Sarah Johnson', time: '2 hours ago', type: 'info' },
  { id: 5, icon: '🚌', text: 'Bus #3 delayed by 10 minutes', time: '3 hours ago', type: 'warning' },
]

const upcomingEvents = [
  { title: 'Parent-Teacher Meeting', date: 'Dec 30, 2024', type: 'meeting' },
  { title: 'Final Exams Begin', date: 'Jan 5, 2025', type: 'exam' },
  { title: 'Winter Break', date: 'Jan 15, 2025', type: 'holiday' },
]

const aiInsights = [
  {
    title: 'At-Risk Students',
    description: 'AI has identified 5 students showing signs of academic decline based on attendance and performance patterns.',
    action: 'Review Students',
    icon: AlertCircle,
    color: '#ef4444'
  },
  {
    title: 'Enrollment Forecast',
    description: 'Projected 15% increase in enrollment for next academic year based on current trends.',
    action: 'View Forecast',
    icon: TrendingUp,
    color: '#10b981'
  },
  {
    title: 'Optimal Timetable',
    description: 'AI has generated an optimized timetable considering teacher availability and room capacity.',
    action: 'View Schedule',
    icon: Calendar,
    color: '#0ea5e9'
  },
]

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', exact: true },
  { path: '/students', icon: Users, label: 'Students' },
  { path: '/teachers', icon: GraduationCap, label: 'Teachers' },
  { path: '/classes', icon: BookOpen, label: 'Classes' },
  { path: '/attendance', icon: Calendar, label: 'Attendance' },
  { path: '/academics', icon: BookOpen, label: 'Academics' },
  { path: '/fees', icon: DollarSign, label: 'Fees' },
  { path: '/transport', icon: Bus, label: 'Transport' },
  { path: '/library', icon: Library, label: 'Library' },
  { path: '/reports', icon: BarChart3, label: 'Reports' },
  { path: '/ai-insights', icon: Sparkles, label: 'AI Insights' },
]

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = React.useState(false)

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div style={{ padding: '20px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', textDecoration: 'none' }}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2">
              <path d="M22 10v6M2 10l10-5 10 5-10 5z" />
              <path d="M6 12v5c3 3 9 3 12 0v-5" />
            </svg>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'white' }}>SchoolOps</span>
          </Link>
        </div>

        <nav style={{ padding: '20px 0' }}>
          <div style={{ marginBottom: '24px' }}>
            <div style={{ padding: '8px 20px', fontSize: '0.75rem', textTransform: 'uppercase', color: '#9ca3af', fontWeight: 600 }}>
              Main Menu
            </div>
            {navItems.map((item) => (
              <a
                key={item.path}
                href={item.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 20px',
                  color: '#d1d5db',
                  textDecoration: 'none',
                  transition: 'all 0.2s',
                  borderLeft: '3px solid transparent',
                }}
              >
                <item.icon size={20} />
                <span>{item.label}</span>
              </a>
            ))}
          </div>

          <div style={{ padding: '8px 20px', fontSize: '0.75rem', textTransform: 'uppercase', color: '#9ca3af', fontWeight: 600 }}>
            System
          </div>
          <a href="/settings" style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 20px', color: '#d1d5db', textDecoration: 'none' }}>
            <Settings size={20} />
            <span>Settings</span>
          </a>
          <a href="/" style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 20px', color: '#d1d5db', textDecoration: 'none' }}>
            <LogOut size={20} />
            <span>Back to Home</span>
          </a>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        {/* Header */}
        <header style={{ background: 'white', padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)', position: 'sticky', top: 0, zIndex: 50 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#6b7280' }}>
              <Menu size={24} />
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#f3f4f6', padding: '10px 16px', borderRadius: '8px', minWidth: '320px' }}>
              <Search size={18} color="#9ca3af" />
              <input type="text" placeholder="Search students, teachers, classes..." style={{ border: 'none', background: 'none', outline: 'none', width: '100%', fontSize: '0.9rem' }} />
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button style={{ position: 'relative', background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#6b7280' }}>
              <Bell size={22} />
              <span style={{ position: 'absolute', top: '4px', right: '4px', width: '8px', height: '8px', background: '#ef4444', borderRadius: '50%' }}></span>
            </button>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '6px 12px', borderRadius: '8px', cursor: 'pointer' }}>
              <div className="avatar">AU</div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>Admin User</div>
                <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>Administrator</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div style={{ padding: '32px' }}>
          {/* Page Header */}
          <div style={{ marginBottom: '32px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#111827', marginBottom: '4px' }}>Welcome back, Admin!</h1>
                <p style={{ color: '#6b7280', fontSize: '0.95rem' }}>Here's what's happening at Green Valley High School today</p>
              </div>
              <div style={{ display: 'flex', gap: '12px' }}>
                <button className="btn btn-outline">
                  <BarChart3 size={18} />
                  Generate Report
                </button>
                <button className="btn btn-primary">
                  <Sparkles size={18} />
                  AI Insights
                </button>
              </div>
            </div>
          </div>

          {/* AI Features Section */}
          <div style={{ background: 'linear-gradient(135deg, rgba(79, 70, 229, 0.05) 0%, rgba(14, 165, 233, 0.05) 100%)', border: '1px solid rgba(79, 70, 229, 0.1)', borderRadius: '12px', padding: '24px', marginBottom: '24px' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'linear-gradient(135deg, #4f46e5 0%, #0ea5e9 100%)', color: 'white', padding: '6px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 600, marginBottom: '16px' }}>
              <Sparkles size={14} />
              AI-Powered Features
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              {aiInsights.map((insight, index) => (
                <div key={index} style={{ background: 'white', padding: '16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', transition: 'all 0.2s' }}>
                  <div style={{ width: '40px', height: '40px', background: insight.color, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                    <insight.icon size={20} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '2px' }}>{insight.title}</h4>
                    <p style={{ fontSize: '0.8rem', color: '#6b7280' }}>{insight.description.slice(0, 60)}...</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid" style={{ marginBottom: '32px' }}>
            {stats.map((stat, index) => (
              <div key={index} className="card" style={{ padding: '24px', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, background: stat.color === 'primary' ? 'rgba(79, 70, 229, 0.1)' : stat.color === 'success' ? 'rgba(16, 185, 129, 0.1)' : stat.color === 'secondary' ? 'rgba(14, 165, 233, 0.1)' : 'rgba(245, 158, 11, 0.1)', color: stat.color === 'primary' ? '#4f46e5' : stat.color === 'success' ? '#10b981' : stat.color === 'secondary' ? '#0ea5e9' : '#f59e0b' }}>
                  <stat.icon size={24} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '1.75rem', fontWeight: 700, color: '#111827' }}>{stat.value}</div>
                  <div style={{ color: '#6b7280', fontSize: '0.9rem', marginTop: '4px' }}>{stat.label}</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', marginTop: '8px', color: stat.positive ? '#10b981' : '#ef4444' }}>
                    {stat.positive ? <TrendingUp size={14} /> : <TrendingUp size={14} style={{ transform: 'rotate(180deg)' }} />}
                    {stat.change} from last month
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
            {/* Recent Activity */}
            <div className="card">
              <div style={{ padding: '20px 24px', borderBottom: '1px solid #f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h3 style={{ fontWeight: 600, color: '#111827' }}>Recent Activity</h3>
                <button className="btn btn-outline btn-sm">View All</button>
              </div>
              <div style={{ padding: '12px 24px' }}>
                {recentActivities.map((activity) => (
                  <div key={activity.id} style={{ display: 'flex', gap: '12px', padding: '12px 0', borderBottom: '1px solid #f3f4f6' }}>
                    <span style={{ fontSize: '1.25rem' }}>{activity.icon}</span>
                    <div style={{ flex: 1 }}>
                      <p style={{ color: '#374151', fontSize: '0.9rem' }}>{activity.text}</p>
                      <span style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '4px', display: 'block' }}>{activity.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="card">
              <div style={{ padding: '20px 24px', borderBottom: '1px solid #f3f4f6', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h3 style={{ fontWeight: 600, color: '#111827' }}>Upcoming Events</h3>
                <button className="btn btn-outline btn-sm">Calendar</button>
              </div>
              <div style={{ padding: '16px 24px' }}>
                {upcomingEvents.map((event, index) => (
                  <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', background: '#f9fafb', borderRadius: '8px', marginBottom: '12px' }}>
                    <div style={{ width: '48px', height: '48px', background: event.type === 'meeting' ? 'rgba(79, 70, 229, 0.1)' : event.type === 'exam' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
                      {event.type === 'meeting' ? '👥' : event.type === 'exam' ? '📝' : '🎉'}
                    </div>
                    <div style={{ flex: 1 }}>
                      <h4 style={{ fontWeight: 600, color: '#111827', marginBottom: '4px' }}>{event.title}</h4>
                      <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>{event.date}</p>
                    </div>
                    <button className="btn btn-outline btn-sm">View</button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
