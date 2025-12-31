# SchoolOps Mobile App

## Overview
SchoolOps mobile app built with React Native and Expo, providing comprehensive school management features for parents, students, teachers, and administrators.

## Features

### For Parents
- View child's attendance records
- Monitor academic performance and grades
- Pay school fees online
- Receive school notifications
- Communicate with teachers
- View homework assignments

### For Students
- Check attendance
- View grades and report cards
- Access homework and assignments
- View class timetable
- Check fee status

### For Teachers
- Mark student attendance
- Upload grades and assessments
- Create and assign homework
- View class schedules
- Communicate with parents

### For Administrators
- Dashboard with analytics
- User management
- Fee management
- Announcements
- Reports and analytics

## Tech Stack
- **Framework**: React Native with Expo SDK 50+
- **Navigation**: Expo Router (file-based routing)
- **UI Library**: React Native Paper v5
- **State Management**: Redux Toolkit
- **Storage**: Async Storage + Secure Store
- **Authentication**: JWT + Biometric
- **Charts**: React Native Chart Kit

## Project Structure

```
mobile/
├── app/
│   ├── (app)/              # Main app screens
│   │   ├── home.tsx        # Dashboard
│   │   ├── academics.tsx   # Attendance, Grades, Homework, Timetable
│   │   ├── fees.tsx        # Fee management
│   │   ├── chat.tsx        # Messaging
│   │   └── profile.tsx     # User profile
│   ├── (auth)/             # Auth screens
│   │   └── login.tsx       # Login screen
│   ├── _layout.tsx         # Root layout
│   └── +not-found.tsx      # 404 page
├── components/             # Reusable components
├── services/
│   ├── api.ts             # API service
│   └── mockData.ts        # Mock data for development
├── store/
│   ├── store.ts           # Redux store
│   └── slices/            # Redux slices
├── theme/
│   └── index.ts           # Theme configuration
├── utils/
│   └── helpers.ts         # Utility functions
├── package.json
├── tsconfig.json
└── app.json
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- Expo Go app (for mobile testing)
- iOS Simulator (macOS) or Android Studio (for emulator)

### Installation

```bash
# Navigate to mobile directory
cd mobile

# Install dependencies
npm install

# Start development server
npm start

# Run on specific platform
npm run ios    # iOS
npm run android # Android
npm run web    # Web
```

### Demo Login
Use the quick demo buttons on the login screen:
- **Student**: View own attendance, grades, homework
- **Parent**: View child's progress, pay fees
- **Teacher**: Mark attendance, upload grades
- **Admin**: Full system access

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Student | student@schoolops.com | demo |
| Parent | parent@schoolops.com | demo |
| Teacher | teacher@schoolops.com | demo |
| Admin | admin@schoolops.com | demo |

## Features Implemented

### Authentication
- [x] Email/password login
- [x] Biometric authentication
- [x] JWT token management
- [x] Session persistence
- [x] Role-based access

### Dashboard
- [x] Role-based dashboard
- [x] Statistics cards
- [x] Quick actions
- [x] Recent activity preview

### Academics
- [x] Attendance tracking with visual indicators
- [x] Grades display with progress bars
- [x] Homework list with status
- [x] Weekly timetable

### Fees
- [x] Fee list with status
- [x] Payment modal with quick amounts
- [x] Payment summary
- [x] Payment history

### Communication
- [x] Contact list
- [x] Chat interface
- [x] Message bubbles
- [x] Real-time input

### Profile
- [x] User information display
- [x] Stats overview
- [x] Settings menu
- [x] Logout functionality

## API Integration

The app is currently using mock data. To connect to the real backend:

1. Update `services/api.ts` with your API URL
2. Configure `API_CONFIG` in `theme/index.ts`
3. Replace mock data calls with actual API calls

```typescript
// Example API call
import { api, API_ENDPOINTS } from './services/api';

const fetchStudents = async () => {
  try {
    const response = await api.get(API_ENDPOINTS.STUDENTS);
    return response;
  } catch (error) {
    console.error('Error fetching students:', error);
  }
};
```

## Push Notifications

The app is configured for push notifications. To enable:

1. Configure Firebase Cloud Messaging
2. Update `app.json` with your credentials
3. Implement notification handlers in `_layout.tsx`

## Building for Production

```bash
# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android

# Build APK
eas build --platform android --profile preview
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@schoolops.com or open an issue on GitHub.
