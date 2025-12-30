'use client'

import React, { useState } from 'react'
import {
  Plus,
  Search,
  Filter,
  Download,
  BookOpen,
  Calendar,
  Clock,
  Eye,
  Edit,
  Trash2
} from 'lucide-react'

const mockTeachers = [
  { id: 'TCH001', name: 'Sarah Johnson', email: 'sarah.j@school.edu', subject: 'Mathematics', classes: ['10-A', '10-B'], hoursPerWeek: 18, status: 'active' },
  { id: 'TCH002', name: 'Robert Williams', email: 'robert.w@school.edu', subject: 'Physics', classes: ['11-A', '12-A'], hoursPerWeek: 22, status: 'active' },
  { id: 'TCH003', name: 'Emily Davis', email: 'emily.d@school.edu', subject: 'Chemistry', classes: ['10-A'], hoursPerWeek: 14, status: 'active' },
  { id: 'TCH004', name: 'Michael Chen', email: 'michael.c@school.edu', subject: 'English', classes: ['9-A', '9-B'], hoursPerWeek: 16, status: 'active' },
  { id: 'TCH005', name: 'Lisa Anderson', email: 'lisa.a@school.edu', subject: 'Biology', classes: ['9-A', '10-B'], hoursPerWeek: 12, status: 'on-leave' },
]

export default function TeachersPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSubject, setSelectedSubject] = useState('all')

  const filteredTeachers = mockTeachers.filter(teacher =>
    teacher.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (selectedSubject === 'all' || teacher.subject === selectedSubject)
  )

  return (
    <div className="fade-in" style={{ padding: '32px' }}>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#111827', marginBottom: '4px' }}>
              Teacher Management
            </h1>
            <p style={{ color: '#6b7280', fontSize: '0.95rem' }}>
              Manage teaching staff, schedules, and performance
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn btn-outline">
              <Download size={18} />
              Export
            </button>
            <button className="btn btn-primary">
              <Plus size={18} />
              Add Teacher
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid" style={{ marginBottom: '24px' }}>
        <div className="stat-card">
          <div className="stat-icon primary"><BookOpen size={24} /></div>
          <div className="stat-content">
            <div className="stat-value">{mockTeachers.length}</div>
            <div className="stat-label">Total Teachers</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon success"><Calendar size={24} /></div>
          <div className="stat-content">
            <div className="stat-value">{mockTeachers.filter(t => t.status === 'active').length}</div>
            <div className="stat-label">Active</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon warning"><Clock size={24} /></div>
          <div className="stat-content">
            <div className="stat-value">16.5</div>
            <div className="stat-label">Avg Hours/Week</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon danger"><BookOpen size={24} /></div>
          <div className="stat-content">
            <div className="stat-value">6</div>
            <div className="stat-label">Subjects</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ flex: 1, minWidth: '300px', background: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '8px' }}>
            <Search size={18} color="#9ca3af" />
            <input
              type="text"
              placeholder="Search teachers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ border: 'none', background: 'none', outline: 'none', width: '100%', fontSize: '0.9rem' }}
            />
          </div>
          <select
            className="form-select"
            style={{ width: '180px' }}
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
          >
            <option value="all">All Subjects</option>
            <option value="Mathematics">Mathematics</option>
            <option value="Physics">Physics</option>
            <option value="Chemistry">Chemistry</option>
            <option value="English">English</option>
            <option value="Biology">Biology</option>
          </select>
          <button className="btn btn-outline">
            <Filter size={18} />
            More Filters
          </button>
        </div>
      </div>

      {/* Teachers Table */}
      <div className="card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Teacher</th>
                <th>Subject</th>
                <th>Classes Assigned</th>
                <th>Hours/Week</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTeachers.map((teacher) => (
                <tr key={teacher.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="avatar">
                        {teacher.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, color: '#111827' }}>{teacher.name}</div>
                        <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{teacher.id}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="badge badge-primary">{teacher.subject}</span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                      {teacher.classes.map(cls => (
                        <span key={cls} className="badge badge-secondary">{cls}</span>
                      ))}
                    </div>
                  </td>
                  <td>{teacher.hoursPerWeek}h</td>
                  <td>
                    <span className={`badge ${teacher.status === 'active' ? 'badge-success' : 'badge-warning'}`}>
                      {teacher.status === 'active' ? 'Active' : 'On Leave'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-icon btn-outline btn-sm" title="View Profile">
                        <Eye size={16} />
                      </button>
                      <button className="btn btn-icon btn-outline btn-sm" title="Edit">
                        <Edit size={16} />
                      </button>
                      <button className="btn btn-icon btn-outline btn-sm" title="Delete">
                        <Trash2 size={16} color="#ef4444" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
