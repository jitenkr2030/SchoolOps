'use client'

import React, { useState } from 'react'
import {
  Plus,
  Users,
  BookOpen,
  Calendar,
  Eye,
  Edit
} from 'lucide-react'

const mockClasses = [
  { id: 'CLS001', name: 'Grade 9-A', grade: 9, section: 'A', students: 32, teacher: 'Ms. Anderson', subjects: 8, timetable: 'Active' },
  { id: 'CLS002', name: 'Grade 9-B', grade: 9, section: 'B', students: 28, teacher: 'Mr. Parker', subjects: 8, timetable: 'Active' },
  { id: 'CLS003', name: 'Grade 10-A', grade: 10, section: 'A', students: 35, teacher: 'Mrs. Johnson', subjects: 7, timetable: 'Active' },
  { id: 'CLS004', name: 'Grade 10-B', grade: 10, section: 'B', students: 30, teacher: 'Mr. Chen', subjects: 7, timetable: 'Pending' },
  { id: 'CLS005', name: 'Grade 11-A', grade: 11, section: 'A', students: 25, teacher: 'Dr. Williams', subjects: 6, timetable: 'Active' },
  { id: 'CLS006', name: 'Grade 12-A', grade: 12, section: 'A', students: 22, teacher: 'Ms. Davis', subjects: 5, timetable: 'Active' },
]

export default function ClassesPage() {
  const [activeTab, setActiveTab] = useState('classes')

  return (
    <div className="fade-in" style={{ padding: '32px' }}>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#111827', marginBottom: '4px' }}>
              Classes & Subjects
            </h1>
            <p style={{ color: '#6b7280', fontSize: '0.95rem' }}>
              Manage classes, sections, and curriculum
            </p>
          </div>
          <button className="btn btn-primary">
            <Plus size={18} />
            Add Class
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs" style={{ marginBottom: '24px' }}>
        <button
          className={`tab ${activeTab === 'classes' ? 'active' : ''}`}
          onClick={() => setActiveTab('classes')}
        >
          Classes
        </button>
        <button
          className={`tab ${activeTab === 'subjects' ? 'active' : ''}`}
          onClick={() => setActiveTab('subjects')}
        >
          Subjects
        </button>
        <button
          className={`tab ${activeTab === 'sections' ? 'active' : ''}`}
          onClick={() => setActiveTab('sections')}
        >
          Sections
        </button>
      </div>

      {activeTab === 'classes' && (
        <>
          {/* Stats */}
          <div className="stats-grid" style={{ marginBottom: '24px' }}>
            <div className="stat-card">
              <div className="stat-icon primary"><Users size={24} /></div>
              <div className="stat-content">
                <div className="stat-value">{mockClasses.length}</div>
                <div className="stat-label">Total Classes</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon success"><Users size={24} /></div>
              <div className="stat-content">
                <div className="stat-value">172</div>
                <div className="stat-label">Total Students</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon secondary"><BookOpen size={24} /></div>
              <div className="stat-content">
                <div className="stat-value">6</div>
                <div className="stat-label">Subjects</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon warning"><Calendar size={24} /></div>
              <div className="stat-content">
                <div className="stat-value">6</div>
                <div className="stat-label">Sections</div>
              </div>
            </div>
          </div>

          {/* Classes Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
            {mockClasses.map((cls) => (
              <div key={cls.id} className="card" style={{ cursor: 'pointer', transition: 'all 0.2s' }}>
                <div className="card-body">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                    <div>
                      <h3 style={{ fontWeight: 600, color: '#111827', fontSize: '1.1rem' }}>{cls.name}</h3>
                      <p style={{ fontSize: '0.85rem', color: '#6b7280' }}>{cls.id}</p>
                    </div>
                    <span className={`badge ${cls.timetable === 'Active' ? 'badge-success' : 'badge-warning'}`}>
                      {cls.timetable}
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                    <div style={{ background: '#f9fafb', padding: '12px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#111827' }}>{cls.students}</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>Students</div>
                    </div>
                    <div style={{ background: '#f9fafb', padding: '12px', borderRadius: '8px' }}>
                      <div style={{ fontSize: '1.25rem', fontWeight: 600, color: '#111827' }}>{cls.subjects}</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>Subjects</div>
                    </div>
                  </div>

                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '4px' }}>Class Teacher</div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="avatar avatar-sm">
                        {cls.teacher.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span style={{ fontWeight: 500, color: '#374151' }}>{cls.teacher}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-outline btn-sm" style={{ flex: 1 }}>
                      <Eye size={14} />
                      View
                    </button>
                    <button className="btn btn-outline btn-sm" style={{ flex: 1 }}>
                      <Edit size={14} />
                      Edit
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {activeTab === 'subjects' && (
        <div className="card">
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Subject Code</th>
                  <th>Subject Name</th>
                  <th>Teachers</th>
                  <th>Classes Assigned</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { code: 'MATH', name: 'Mathematics', teachers: 3, classes: ['9-A', '10-A', '11-A', '12-A'] },
                  { code: 'PHYS', name: 'Physics', teachers: 2, classes: ['10-A', '11-A', '12-A'] },
                  { code: 'CHEM', name: 'Chemistry', teachers: 2, classes: ['10-A', '11-A', '12-A'] },
                  { code: 'ENG', name: 'English', teachers: 3, classes: ['9-A', '9-B', '10-A', '10-B'] },
                  { code: 'BIO', name: 'Biology', teachers: 2, classes: ['9-A', '10-B', '11-A'] },
                  { code: 'HIST', name: 'History', teachers: 2, classes: ['9-A', '9-B', '10-A'] },
                ].map((subject) => (
                  <tr key={subject.code}>
                    <td>
                      <span className="badge badge-primary">{subject.code}</span>
                    </td>
                    <td style={{ fontWeight: 500 }}>{subject.name}</td>
                    <td>{subject.teachers}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                        {subject.classes.map(cls => (
                          <span key={cls} className="badge badge-secondary">{cls}</span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button className="btn btn-icon btn-outline btn-sm">
                          <Edit size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
