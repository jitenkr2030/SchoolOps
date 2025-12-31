import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import academicsReducer from './slices/academicsSlice';
import feesReducer from './slices/feesSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    academics: academicsReducer,
    fees: feesReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
