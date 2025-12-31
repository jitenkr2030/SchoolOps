import { API_CONFIG } from '../theme';

// Mock Users Data
export const MOCK_USERS = {
  admin: {
    id: 'admin-001',
    email: 'admin@schoolops.com',
    firstName: 'Admin',
    lastName: 'User',
    role: 'admin' as const,
    schoolName: 'Springfield High School',
  },
  principal: {
    id: 'principal-001',
    email: 'principal@schoolops.com',
    firstName: 'Dr. Sarah',
    lastName: 'Johnson',
    role: 'principal' as const,
    schoolName: 'Springfield High School',
  },
  teacher: {
    id: 'teacher-001',
    email: 'teacher@schoolops.com',
    firstName: 'Mr. Rahul',
    lastName: 'Sharma',
    role: 'teacher' as const,
    subject: 'Mathematics',
    schoolId: 'school-001',
  },
  student: {
    id: 'student-001',
    email: 'student@schoolops.com',
    firstName: 'Amit',
    lastName: 'Kumar',
    role: 'student' as const,
    className: 'Class 10-A',
    rollNumber: '15',
    schoolId: 'school-001',
  },
  parent: {
    id: 'parent-001',
    email: 'parent@schoolops.com',
    firstName: 'Sanjay',
    lastName: 'Kumar',
    role: 'parent' as const,
    children: [
      {
        id: 'student-001',
        name: 'Amit Kumar',
        class: 'Class 10-A',
        rollNumber: '15',
      },
    ],
  },
};

// Dashboard Stats by Role
export const DASHBOARD_STATS = {
  admin: [
    { label: 'Total Students', value: '1,245', icon: 'account-group', color: '#4F46E5' },
    { label: 'Total Teachers', value: '85', icon: 'teach', color: '#10B981' },
    { label: 'Fee Collection', value: '87%', icon: 'cash-check', color: '#F59E0B' },
    { label: 'Attendance', value: '94%', icon: 'calendar-check', color: '#8B5CF6' },
  ],
  principal: [
    { label: 'Students', value: '1,245', icon: 'account-group', color: '#4F46E5' },
    { label: 'Staff', value: '120', icon: 'people', color: '#10B981' },
    { label: 'Fee Collection', value: '87%', icon: 'cash-check', color: '#F59E0B' },
    { label: 'Attendance', value: '94%', icon: 'calendar-check', color: '#8B5CF6' },
  ],
  teacher: [
    { label: 'Classes Today', value: '5', icon: 'calendar-today', color: '#4F46E5' },
    { label: 'Pending Grades', value: '28', icon: 'grade', color: '#F59E0B' },
    { label: 'Homework', value: '3 Active', icon: 'homework', color: '#10B981' },
    { label: 'Messages', value: '12', icon: 'message', color: '#8B5CF6' },
  ],
  student: [
    { label: 'Attendance', value: '94%', icon: 'calendar-check', color: '#10B981' },
    { label: 'Avg Grade', value: 'A-', icon: 'star', color: '#F59E0B' },
    { label: 'Homework', value: '4 Pending', icon: 'book-open-variant', color: '#4F46E5' },
    { label: 'Next Class', value: 'Math', icon: 'clock', color: '#8B5CF6' },
  ],
  parent: [
    { label: 'Fees Due', value: '₹5,000', icon: 'cash', color: '#EF4444' },
    { label: 'Attendance', value: '94%', icon: 'calendar-check', color: '#10B981' },
    { label: 'Last Grade', value: 'A-', icon: 'grade', color: '#F59E0B' },
    { label: 'Notices', value: '2 New', icon: 'bell', color: '#4F46E5' },
  ],
};

// Mock Attendance Data
export const ATTENDANCE_DATA = [
  { id: '1', date: '2024-01-15', day: 'Monday', status: 'Present', color: '#10B981' },
  { id: '2', date: '2024-01-16', day: 'Tuesday', status: 'Present', color: '#10B981' },
  { id: '3', date: '2024-01-17', day: 'Wednesday', status: 'Absent', color: '#EF4444' },
  { id: '4', date: '2024-01-18', day: 'Thursday', status: 'Late', color: '#F59E0B' },
  { id: '5', date: '2024-01-19', day: 'Friday', status: 'Present', color: '#10B981' },
  { id: '6', date: '2024-01-20', day: 'Saturday', status: 'Present', color: '#10B981' },
  { id: '7', date: '2024-01-22', day: 'Monday', status: 'Present', color: '#10B981' },
];

// Mock Grades Data
export const GRADES_DATA = [
  { id: '1', subject: 'Mathematics', score: 92, maxScore: 100, grade: 'A', examType: 'Unit Test 1', date: '2024-01-10' },
  { id: '2', subject: 'Science', score: 85, maxScore: 100, grade: 'A-', examType: 'Unit Test 1', date: '2024-01-08' },
  { id: '3', subject: 'English', score: 78, maxScore: 100, grade: 'B+', examType: 'Unit Test 1', date: '2024-01-05' },
  { id: '4', subject: 'Social Science', score: 88, maxScore: 100, grade: 'A-', examType: 'Unit Test 1', date: '2024-01-03' },
  { id: '5', subject: 'Hindi', score: 95, maxScore: 100, grade: 'A', examType: 'Unit Test 1', date: '2024-01-12' },
];

// Mock Homework Data
export const HOMEWORK_DATA = [
  { id: '1', title: 'Chapter 5 Exercise', subject: 'Mathematics', description: 'Solve all problems from exercise 5.1 to 5.5', dueDate: '2024-01-20', status: 'pending' as const },
  { id: '2', title: 'Lab Report', subject: 'Science', description: 'Write a lab report for the chemistry experiment', dueDate: '2024-01-22', status: 'pending' as const },
  { id: '3', title: 'Essay Writing', subject: 'English', description: 'Write an essay on "My Future Dreams"', dueDate: '2024-01-18', status: 'submitted' as const },
  { id: '4', title: 'Map Work', subject: 'Social Science', description: 'Label the states of India on the outline map', dueDate: '2024-01-25', status: 'pending' as const },
];

// Mock Fee Data
export const FEE_DATA = [
  { id: '1', feeType: 'Tuition Fee', amount: 15000, dueDate: '2024-04-30', status: 'Paid' as const, academicYear: '2023-2024' },
  { id: '2', feeType: 'Development Fee', amount: 5000, dueDate: '2024-04-30', status: 'Paid' as const, academicYear: '2023-2024' },
  { id: '3', feeType: 'Transport Fee', amount: 8000, dueDate: '2024-05-31', status: 'Overdue' as const, academicYear: '2023-2024' },
  { id: '4', feeType: 'Library Fee', amount: 2000, dueDate: '2024-06-30', status: 'Pending' as const, academicYear: '2023-2024' },
  { id: '5', feeType: 'Tuition Fee', amount: 15000, dueDate: '2024-07-31', status: 'Pending' as const, academicYear: '2024-2025' },
];

// Mock Timetable
export const TIMETABLE_DATA = [
  { id: '1', day: 'Monday', time: '08:00 - 08:45', subject: 'Mathematics', className: 'Class 10-A', room: 'Room 101' },
  { id: '2', day: 'Monday', time: '08:45 - 09:30', subject: 'Science', className: 'Class 10-A', room: 'Room 102' },
  { id: '3', day: 'Monday', time: '09:30 - 10:15', subject: 'English', className: 'Class 10-A', room: 'Room 103' },
  { id: '4', day: 'Monday', time: '10:15 - 10:45', subject: 'Break', className: '', room: '' },
  { id: '5', day: 'Monday', time: '10:45 - 11:30', subject: 'Social Science', className: 'Class 10-A', room: 'Room 101' },
  { id: '6', day: 'Tuesday', time: '08:00 - 08:45', subject: 'Hindi', className: 'Class 10-A', room: 'Room 104' },
  { id: '7', day: 'Tuesday', time: '08:45 - 09:30', subject: 'Mathematics', className: 'Class 10-A', room: 'Room 101' },
];

// Mock Notifications
export const NOTIFICATIONS = [
  { id: '1', title: 'Fee Due Reminder', message: 'Tuition fee for the month is due. Please pay before the due date.', type: 'fee', date: '2024-01-15' },
  { id: '2', title: 'Parent Meeting', message: 'Parent-teacher meeting scheduled for January 25, 2024.', type: 'event', date: '2024-01-14' },
  { id: '3', title: 'Holiday Notice', message: 'School will remain closed on January 26 for Republic Day.', type: 'announcement', date: '2024-01-12' },
  { id: '4', title: 'Exam Schedule', message: 'Mid-term exam schedule has been released. Please check the notice board.', type: 'academic', date: '2024-01-10' },
];

// Mock Chat Messages
export const CHAT_MESSAGES = [
  { id: '1', senderId: 'teacher-001', receiverId: 'parent-001', message: 'Hello, I wanted to discuss Amit\'s progress in Mathematics.', timestamp: '2024-01-15 10:30:00', type: 'received' as const },
  { id: '2', senderId: 'parent-001', receiverId: 'teacher-001', message: 'Hello Sir, yes please. How is he performing?', timestamp: '2024-01-15 10:35:00', type: 'sent' as const },
  { id: '3', senderId: 'teacher-001', receiverId: 'parent-001', message: 'He is doing well but needs to focus more on practice problems. His understanding of concepts is good.', timestamp: '2024-01-15 10:40:00', type: 'received' as const },
  { id: '4', senderId: 'parent-001', receiverId: 'teacher-001', message: 'Thank you for the update. We will ensure he practices more at home.', timestamp: '2024-01-15 10:45:00', type: 'sent' as const },
];

// Role-based Quick Actions
export const QUICK_ACTIONS = {
  admin: [
    { label: 'Add Student', icon: 'account-plus', screen: 'addStudent' },
    { label: 'Send Notice', icon: 'bell-ring', screen: 'sendNotice' },
    { label: 'View Reports', icon: 'chart-bar', screen: 'reports' },
    { label: 'Settings', icon: 'cog', screen: 'settings' },
  ],
  principal: [
    { label: 'Staff Management', icon: 'account-group', screen: 'staff' },
    { label: 'Announcements', icon: 'bullhorn', screen: 'announcements' },
    { label: 'Reports', icon: 'chart-line', screen: 'reports' },
    { label: 'Settings', icon: 'cog', screen: 'settings' },
  ],
  teacher: [
    { label: 'Mark Attendance', icon: 'check-circle', screen: 'attendance' },
    { label: 'Add Grades', icon: 'grade', screen: 'grades' },
    { label: 'Create Homework', icon: 'homework', screen: 'homework' },
    { label: 'Send Message', icon: 'message', screen: 'messages' },
  ],
  student: [
    { label: 'View Timetable', icon: 'calendar-clock', screen: 'timetable' },
    { label: 'Homework', icon: 'book', screen: 'homework' },
    { label: 'Results', icon: 'chart-bar', screen: 'results' },
    { label: 'Profile', icon: 'account', screen: 'profile' },
  ],
  parent: [
    { label: 'Pay Fees', icon: 'credit-card', screen: 'payFees' },
    { label: 'View Progress', icon: 'chart-line', screen: 'progress' },
    { label: 'Contact Teacher', icon: 'phone', screen: 'contact' },
    { label: 'View Notices', icon: 'bell', screen: 'notices' },
  ],
};

// Helper function to get mock data based on user role
export const getMockDataForRole = (role: string) => {
  switch (role) {
    case 'admin':
    case 'principal':
      return {
        stats: DASHBOARD_STATS.admin,
        actions: QUICK_ACTIONS.admin,
      };
    case 'teacher':
      return {
        stats: DASHBOARD_STATS.teacher,
        actions: QUICK_ACTIONS.teacher,
      };
    case 'student':
      return {
        stats: DASHBOARD_STATS.student,
        actions: QUICK_ACTIONS.student,
        attendance: ATTENDANCE_DATA,
        grades: GRADES_DATA,
        homework: HOMEWORK_DATA,
        timetable: TIMETABLE_DATA,
      };
    case 'parent':
      return {
        stats: DASHBOARD_STATS.parent,
        actions: QUICK_ACTIONS.parent,
        fees: FEE_DATA,
        notifications: NOTIFICATIONS,
      };
    default:
      return {
        stats: [],
        actions: [],
      };
  }
};
