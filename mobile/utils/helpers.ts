export const formatDate = (dateString: string, format: 'short' | 'long' | 'relative' = 'short'): string => {
  const date = new Date(dateString);
  
  if (format === 'relative') {
    const now = new Date();
    const diffTime = date.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    if (diffDays === -1) return 'Yesterday';
    if (diffDays > 1 && diffDays <= 7) return `In ${diffDays} days`;
    if (diffDays < -1 && diffDays >= -7) return `${Math.abs(diffDays)} days ago`;
  }
  
  if (format === 'long') {
    return date.toLocaleDateString('en-IN', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
  
  return date.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
};

export const formatCurrency = (amount: number, currency: string = 'INR'): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

export const calculatePercentage = (value: number, total: number): number => {
  if (total === 0) return 0;
  return Math.round((value / total) * 100);
};

export const getGradeColor = (grade: string): string => {
  const upperGrade = grade.toUpperCase();
  if (upperGrade.startsWith('A')) return '#10B981'; // Green
  if (upperGrade.startsWith('B')) return '#4F46E5'; // Blue
  if (upperGrade.startsWith('C')) return '#F59E0B'; // Yellow
  return '#EF4444'; // Red
};

export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'present':
    case 'paid':
    case 'active':
      return '#10B981';
    case 'absent':
    case 'overdue':
    case 'inactive':
      return '#EF4444';
    case 'late':
    case 'pending':
    case 'partial':
      return '#F59E0B';
    case 'excused':
      return '#8B5CF6';
    default:
      return '#6B7280';
  }
};

export const getInitials = (firstName: string, lastName?: string): string => {
  const first = firstName.charAt(0).toUpperCase();
  const last = lastName ? lastName.charAt(0).toUpperCase() : '';
  return `${first}${last}`;
};

export const validateEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePhone = (phone: string): boolean => {
  const re = /^[6-9]\d{9}$/;
  return re.test(phone);
};

export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
};

export const getDaysInMonth = (year: number, month: number): number => {
  return new Date(year, month + 1, 0).getDate();
};

export const getMonthName = (month: number): string => {
  return new Date(2000, month, 1).toLocaleString('default', { month: 'long' });
};

export const isToday = (dateString: string): boolean => {
  const today = new Date().toISOString().split('T')[0];
  return dateString === today;
};

export const isPastDate = (dateString: string): boolean => {
  const date = new Date(dateString);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return date < today;
};

export const getRelativeTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(dateString, 'short');
};
