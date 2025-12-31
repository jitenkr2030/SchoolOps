import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AttendanceRecord {
  id: string;
  date: string;
  status: 'Present' | 'Absent' | 'Late' | 'Excused';
  className?: string;
}

interface AcademicState {
  attendance: AttendanceRecord[];
  grades: GradeRecord[];
  homework: HomeworkRecord[];
  timetable: TimetableSlot[];
  isLoading: boolean;
  error: string | null;
}

interface GradeRecord {
  id: string;
  subject: string;
  score: number;
  maxScore: number;
  grade: string;
  examType: string;
  date: string;
  teacherName?: string;
}

interface HomeworkRecord {
  id: string;
  title: string;
  subject: string;
  description: string;
  dueDate: string;
  status: 'pending' | 'submitted' | 'graded';
  attachments?: string[];
}

interface TimetableSlot {
  id: string;
  day: string;
  time: string;
  subject: string;
  className: string;
  room: string;
}

const initialState: AcademicState = {
  attendance: [],
  grades: [],
  homework: [],
  timetable: [],
  isLoading: false,
  error: null,
};

const academicsSlice = createSlice({
  name: 'academics',
  initialState,
  reducers: {
    setAttendance: (state, action: PayloadAction<AttendanceRecord[]>) => {
      state.attendance = action.payload;
    },
    addAttendanceRecord: (state, action: PayloadAction<AttendanceRecord>) => {
      state.attendance.unshift(action.payload);
    },
    setGrades: (state, action: PayloadAction<GradeRecord[]>) => {
      state.grades = action.payload;
    },
    addGradeRecord: (state, action: PayloadAction<GradeRecord>) => {
      state.grades.unshift(action.payload);
    },
    setHomework: (state, action: PayloadAction<HomeworkRecord[]>) => {
      state.homework = action.payload;
    },
    updateHomeworkStatus: (state, action: PayloadAction<{ id: string; status: HomeworkRecord['status'] }>) => {
      const homework = state.homework.find(h => h.id === action.payload.id);
      if (homework) {
        homework.status = action.payload.status;
      }
    },
    setTimetable: (state, action: PayloadAction<TimetableSlot[]>) => {
      state.timetable = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setAttendance,
  addAttendanceRecord,
  setGrades,
  addGradeRecord,
  setHomework,
  updateHomeworkStatus,
  setTimetable,
  setLoading,
  setError,
} = academicsSlice.actions;

export default academicsSlice.reducer;
