'use client'

import React, { useState } from 'react'
import {
  Plus,
  Search,
  Filter,
  Download,
  Upload,
  Eye,
  Edit,
  Trash2,
  AlertCircle,
  Sparkles
} from 'lucide-react'

// Mock student data
const mockStudents = [
  { id: 'STU001', name: 'Emily Johnson', email: 'emily.j@email.com', grade: 10, section: 'A', rollNumber: 23, attendance: 96, status: 'active', riskLevel: 'low' },
  { id: 'STU002', name: 'Michael Chen', email: 'michael.c@email.com', grade: 10, section: 'A', rollNumber: 24, attendance: 72, status: 'active', riskLevel: 'high' },
  { id: 'STU003', name: 'Sarah Williams', email: 'sarah.w@email.com', grade: 9, section: 'B', rollNumber: 15, attendance: 98, status: 'active', riskLevel: 'low' },
  { id: 'STU004', name: 'David Brown', email: 'david.b@email.com', grade: 11, section: 'A', rollNumber: 31, attendance: 85, status: 'active', riskLevel: 'medium' },
  { id: 'STU005', name: 'Jennifer Davis', email: 'jennifer.d@email.com', grade: 10, section: 'B', rollNumber: 18, attendance: 94, status: 'active', riskLevel: 'low' },
]

export default function StudentsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedGrade, setSelectedGrade] = useState('all')

  const filteredStudents = mockStudents.filter(student =>
    student.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (selectedGrade === 'all' || student.grade.toString() === selectedGrade)
  )

  const getRiskBadge = (risk: string) => {
    const styles: Record<string, { bg: string; color: string }> = {
      high: { bg: 'rgba(239, 68, 68, 0.1)', color: '#ef4444' },
      medium: { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' },
      low: { bg: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }
    }
    return (
      <span className="badge" style={{ background: styles[risk]?.bg, color: styles[risk]?.color }}>
        <AlertCircle size={12} style={{ marginRight: '4px' }} />
        {risk.charAt(0).toUpperCase() + risk.slice(1)} Risk
      </span>
    )
  }

  return (
    <div className="fade-in" style={{ padding: '32px' }}>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#111827', marginBottom: '4px' }}>
              Student Management
            </h1>
            <p style={{ color: '#6b7280', fontSize: '0.95rem' }}>
              Manage all student records, enrollments, and information
            </p>
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn btn-outline">
              <Upload size={18} />
              Import CSV
            </button>
            <button className="btn btn-primary">
              <Plus size={18} />
              Add Student
            </button>
          </div>
        </div>
      </div>

      {/* AI Risk Assessment Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)',
        border: '1px solid rgba(239, 68, 68, 0.2)',
        borderRadius: '12px',
        padding: '20px',
        marginBottom: '24px',
        display: 'flex',
        alignItems: 'center',
        gap: '20px'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          background: 'linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Sparkles size={24} color="white" />
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{ fontWeight: 600, color: '#111827', marginBottom: '4px' }}>AI-Powered Risk Assessment</h3>
          <p style={{ fontSize: '0.9rem', color: '#6b7280' }}>
            1 student flagged as high-risk for dropout. 3 students showing early warning signs.
          </p>
        </div>
        <button className="btn btn-outline">Review Students</button>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div style={{ padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ flex: 1, minWidth: '300px', background: '#f3f4f6', display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '8px' }}>
            <Search size={18} color="#9ca3af" />
            <input
              type="text"
              placeholder="Search students by name, ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ border: 'none', background: 'none', outline: 'none', width: '100%', fontSize: '0.9rem' }}
            />
          </div>
          <select
            className="form-select"
            style={{ width: '160px' }}
            value={selectedGrade}
            onChange={(e) => setSelectedGrade(e.target.value)}
          >
            <option value="all">All Grades</option>
            <option value="9">Grade 9</option>
            <option value="10">Grade 10</option>
            <option value="11">Grade 11</option>
            <option value="12">Grade 12</option>
          </select>
          <button className="btn btn-outline">
            <Filter size={18} />
            More Filters
          </button>
          <button className="btn btn-outline">
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      {/* Students Table */}
      <div className="card">
        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Student</th>
                <th>Grade/Section</th>
                <th>Roll Number</th>
                <th>Attendance</th>
                <th>AI Risk Level</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.map((student) => (
                <tr key={student.id}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div className="avatar">
                        {student.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, color: '#111827' }}>{student.name}</div>
                        <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{student.id}</div>
                      </div>
                    </div>
                  </td>
                  <td>Grade {student.grade}-{student.section}</td>
                  <td>#{student.rollNumber}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div className="progress" style={{ width: '80px' }}>
                        <div
                          className={`progress-bar ${student.attendance >= 90 ? 'success' : student.attendance >= 80 ? 'warning' : 'danger'}`}
                          style={{ width: `${student.attendance}%` }}
                        ></div>
                      </div>
                      <span style={{ fontSize: '0.85rem', color: '#6b7280' }}>{student.attendance}%</span>
                    </div>
                  </td>
                  <td>{getRiskBadge(student.riskLevel)}</td>
                  <td>
                    <span className={`badge ${student.status === 'active' ? 'badge-success' : 'badge-danger'}`}>
                      {student.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn btn-icon btn-outline btn-sm" title="View Details">
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
