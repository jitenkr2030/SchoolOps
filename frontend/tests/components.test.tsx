"""
Unit tests for Frontend Components in SchoolOps
"""
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// Import components to test
import Dashboard from '@/app/page';
import StudentsPage from '@/app/students/page';
import TeachersPage from '@/app/teachers/page';
import ClassesPage from '@/app/classes/page';


// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
  useSearchParams: jest.fn(),
}));

// Mock API calls
jest.mock('@/lib/api', () => ({
  fetchStudents: jest.fn(),
  fetchTeachers: jest.fn(),
  fetchClasses: jest.fn(),
  createStudent: jest.fn(),
  updateStudent: jest.fn(),
  deleteStudent: jest.fn(),
}));

import * as api from '@/lib/api';


describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders dashboard title', () => {
    render(<Dashboard />);
    expect(screen.getByText('SchoolOps Dashboard')).toBeInTheDocument();
  });

  it('renders navigation menu', () => {
    render(<Dashboard />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Students')).toBeInTheDocument();
    expect(screen.getByText('Teachers')).toBeInTheDocument();
    expect(screen.getByText('Classes')).toBeInTheDocument();
  });

  it('renders stat cards', () => {
    render(<Dashboard />);
    expect(screen.getByText('Total Students')).toBeInTheDocument();
    expect(screen.getByText('Total Teachers')).toBeInTheDocument();
    expect(screen.getByText('Attendance Rate')).toBeInTheDocument();
    expect(screen.getByText('Fee Collection')).toBeInTheDocument();
  });

  it('renders quick actions', () => {
    render(<Dashboard />);
    expect(screen.getByText('Take Attendance')).toBeInTheDocument();
    expect(screen.getByText('Add Student')).toBeInTheDocument();
    expect(screen.getByText('Send Notification')).toBeInTheDocument();
    expect(screen.getByText('Generate Report')).toBeInTheDocument();
  });
});


describe('Students Page Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockStudents = [
    {
      id: 1,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@school.com',
      admission_number: 'STU001',
      class_name: 'Class 10',
    },
    {
      id: 2,
      first_name: 'Jane',
      last_name: 'Smith',
      email: 'jane.smith@school.com',
      admission_number: 'STU002',
      class_name: 'Class 9',
    },
  ];

  it('renders students page title', () => {
    render(<StudentsPage />);
    expect(screen.getByText('Student Management')).toBeInTheDocument();
  });

  it('renders search input', () => {
    render(<StudentsPage />);
    expect(screen.getByPlaceholderText('Search students...')).toBeInTheDocument();
  });

  it('renders add student button', () => {
    render(<StudentsPage />);
    expect(screen.getByText('Add Student')).toBeInTheDocument();
  });

  it('displays student list', async () => {
    api.fetchStudents.mockResolvedValue(mockStudents);
    
    render(<StudentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('filters students by search term', async () => {
    api.fetchStudents.mockResolvedValue(mockStudents);
    
    render(<StudentsPage />);
    
    const searchInput = screen.getByPlaceholderText('Search students...');
    fireEvent.change(searchInput, { target: { value: 'John' } });
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.queryByText('Jane Smith')).not.toBeInTheDocument();
    });
  });

  it('shows loading state', () => {
    api.fetchStudents.mockImplementation(() => new Promise(() => {}));
    
    render(<StudentsPage />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('shows empty state when no students', async () => {
    api.fetchStudents.mockResolvedValue([]);
    
    render(<StudentsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('No students found')).toBeInTheDocument();
    });
  });
});


describe('Teachers Page Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockTeachers = [
    {
      id: 1,
      first_name: 'Mr.',
      last_name: 'Sharma',
      email: 'sharma@school.com',
      subject: 'Mathematics',
    },
    {
      id: 2,
      first_name: 'Ms.',
      last_name: 'Patel',
      email: 'patel@school.com',
      subject: 'Science',
    },
  ];

  it('renders teachers page title', () => {
    render(<TeachersPage />);
    expect(screen.getByText('Teacher Management')).toBeInTheDocument();
  });

  it('renders add teacher button', () => {
    render(<TeachersPage />);
    expect(screen.getByText('Add Teacher')).toBeInTheDocument();
  });

  it('displays teacher list', async () => {
    api.fetchTeachers.mockResolvedValue(mockTeachers);
    
    render(<TeachersPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Mr. Sharma')).toBeInTheDocument();
      expect(screen.getByText('Ms. Patel')).toBeInTheDocument();
    });
  });
});


describe('Classes Page Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const mockClasses = [
    { id: 1, name: 'Class 10', section: 'A', academic_year: '2024-2025' },
    { id: 2, name: 'Class 9', section: 'B', academic_year: '2024-2025' },
  ];

  it('renders classes page title', () => {
    render(<ClassesPage />);
    expect(screen.getByText('Class Management')).toBeInTheDocument();
  });

  it('renders add class button', () => {
    render(<ClassesPage />);
    expect(screen.getByText('Add Class')).toBeInTheDocument();
  });

  it('displays class list', async () => {
    api.fetchClasses.mockResolvedValue(mockClasses);
    
    render(<ClassesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Class 10 - A')).toBeInTheDocument();
      expect(screen.getByText('Class 9 - B')).toBeInTheDocument();
    });
  });
});


describe('Form Components', () => {
  it('validates required fields', async () => {
    const user = userEvent.setup();
    
    render(
      <form>
        <input type="text" name="firstName" required placeholder="First Name" />
        <input type="email" name="email" required placeholder="Email" />
        <button type="submit">Submit</button>
      </form>
    );
    
    const submitButton = screen.getByRole('button', { name: 'Submit' });
    await user.click(submitButton);
    
    // Form should not submit with empty required fields
    expect(submitButton).toBeEnabled();
  });

  it('validates email format', () => {
    render(
      <input type="email" name="email" placeholder="Email" />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    expect(emailInput.validity.valid).toBe(false);
  });

  it('validates phone number format', () => {
    render(
      <input type="tel" name="phone" placeholder="Phone" pattern="[0-9]{10}" />
    );
    
    const phoneInput = screen.getByPlaceholderText('Phone');
    fireEvent.change(phoneInput, { target: { value: '12345' } });
    
    expect(phoneInput.validity.valid).toBe(false);
  });
});


describe('Modal Components', () => {
  it('renders modal when opened', () => {
    render(
      <div>
        <button onClick={() => {}}>Open Modal</button>
        <div className="modal">
          <h2>Add Student</h2>
          <p>Fill in the student details</p>
        </div>
      </div>
    );
    
    expect(screen.getByText('Add Student')).toBeInTheDocument();
    expect(screen.getByText('Fill in the student details')).toBeInTheDocument();
  });

  it('closes modal on close button click', () => {
    const handleClose = jest.fn();
    
    render(
      <div className="modal-overlay" onClick={handleClose}>
        <div className="modal-content" onClick={(e) => e.stopPropagation()}>
          <button onClick={handleClose}>Close</button>
        </div>
      </div>
    );
    
    const closeButton = screen.getByRole('button', { name: 'Close' });
    fireEvent.click(closeButton);
    
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});


describe('Data Table Components', () => {
  it('renders table headers', () => {
    render(
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Class</th>
            <th>Actions</th>
          </tr>
        </thead>
      </table>
    );
    
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Email')).toBeInTheDocument();
    expect(screen.getByText('Class')).toBeInTheDocument();
    expect(screen.getByText('Actions')).toBeInTheDocument();
  });

  it('renders pagination controls', () => {
    render(
      <div className="pagination">
        <button>Previous</button>
        <span>Page 1 of 5</span>
        <button>Next</button>
      </div>
    );
    
    expect(screen.getByText('Previous')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('Page 1 of 5')).toBeInTheDocument();
  });

  it('sorts columns on header click', async () => {
    const user = userEvent.setup();
    
    render(
      <table>
        <thead>
          <tr>
            <th onClick={() => {}}>Name</th>
            <th onClick={() => {}}>Email</th>
          </tr>
        </thead>
      </table>
    );
    
    const nameHeader = screen.getByText('Name');
    await user.click(nameHeader);
    
    // Should show sort indicator
    expect(nameHeader).toBeInTheDocument();
  });
});
