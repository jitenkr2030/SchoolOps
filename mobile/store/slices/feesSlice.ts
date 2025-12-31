import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface FeeRecord {
  id: string;
  feeType: string;
  amount: number;
  dueDate: string;
  status: 'Pending' | 'Paid' | 'Overdue' | 'Partial';
  paidAmount?: number;
  academicYear: string;
}

interface FeeState {
  fees: FeeRecord[];
  totalDue: number;
  totalPaid: number;
  isLoading: boolean;
  error: string | null;
}

const initialState: FeeState = {
  fees: [],
  totalDue: 0,
  totalPaid: 0,
  isLoading: false,
  error: null,
};

const feesSlice = createSlice({
  name: 'fees',
  initialState,
  reducers: {
    setFees: (state, action: PayloadAction<FeeRecord[]>) => {
      state.fees = action.payload;
      state.totalDue = action.payload
        .filter(f => f.status !== 'Paid')
        .reduce((sum, f) => sum + (f.amount - (f.paidAmount || 0)), 0);
      state.totalPaid = action.payload
        .filter(f => f.status === 'Paid')
        .reduce((sum, f) => sum + f.amount, 0);
    },
    addPayment: (state, action: PayloadAction<{ feeId: string; amount: number }>) => {
      const fee = state.fees.find(f => f.id === action.payload.feeId);
      if (fee) {
        fee.paidAmount = (fee.paidAmount || 0) + action.payload.amount;
        if (fee.paidAmount >= fee.amount) {
          fee.status = 'Paid';
        } else {
          fee.status = 'Partial';
        }
        // Recalculate totals
        state.totalDue = state.fees
          .filter(f => f.status !== 'Paid')
          .reduce((sum, f) => sum + (f.amount - (f.paidAmount || 0)), 0);
        state.totalPaid = state.fees
          .filter(f => f.status === 'Paid')
          .reduce((sum, f) => sum + f.amount, 0);
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setFees, addPayment, setLoading, setError } = feesSlice.actions;
export default feesSlice.reducer;
