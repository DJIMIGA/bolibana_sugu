import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { logoutAsync } from './authSlice';

interface NotificationState {
  unreadCount: number;
  permissionGranted: boolean;
  notificationsEnabled: boolean;
}

const initialState: NotificationState = {
  unreadCount: 0,
  permissionGranted: false,
  notificationsEnabled: true,
};

const notificationSlice = createSlice({
  name: 'notification',
  initialState,
  reducers: {
    incrementUnreadCount: (state) => {
      state.unreadCount += 1;
    },
    clearUnreadCount: (state) => {
      state.unreadCount = 0;
    },
    setPermissionGranted: (state, action: PayloadAction<boolean>) => {
      state.permissionGranted = action.payload;
    },
    setNotificationsEnabled: (state, action: PayloadAction<boolean>) => {
      state.notificationsEnabled = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(logoutAsync.fulfilled, (state) => {
      state.unreadCount = 0;
      state.permissionGranted = false;
      state.notificationsEnabled = true;
    });
  },
});

export const {
  incrementUnreadCount,
  clearUnreadCount,
  setPermissionGranted,
  setNotificationsEnabled,
} = notificationSlice.actions;
export default notificationSlice.reducer;
