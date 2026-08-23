const rawBaseUrl = import.meta.env?.VITE_API_BASE_URL;
const API_BASE_URL = rawBaseUrl
  ? (rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl)
  : (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '3000'))
    ? '/api'
    : 'http://127.0.0.1:8000/api';

export const getAuthToken = () => localStorage.getItem('token');
export const setAuthToken = (token) => localStorage.setItem('token', token);
export const removeAuthToken = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getStoredUser = () => {
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
};

export const setStoredUser = (user) => localStorage.setItem('user', JSON.stringify(user));

export async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const config = {
    ...options,
    headers,
  };

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  } catch (err) {
    // If proxied fetch failed or network error occurred, attempt fallback direct URL fetch
    if (API_BASE_URL.startsWith('/')) {
      try {
        response = await fetch(`http://127.0.0.1:8000/api${endpoint}`, config);
      } catch (fallbackErr) {
        throw new Error(`Unable to connect to FastAPI backend server (${API_BASE_URL}). Please ensure backend server is running.`);
      }
    } else {
      throw new Error(`Unable to connect to FastAPI backend server (${API_BASE_URL}). Please ensure backend server is running.`);
    }
  }

  if (response.status === 401) {
    removeAuthToken();
    window.dispatchEvent(new Event('unauthorized'));
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let errorMsg = 'An API error occurred';
    if (typeof data.detail === 'string') {
      errorMsg = data.detail;
    } else if (Array.isArray(data.detail)) {
      errorMsg = data.detail.map(e => e.msg || e.detail || JSON.stringify(e)).join(', ');
    } else if (typeof data.detail === 'object' && data.detail !== null) {
      errorMsg = data.detail.message || data.detail.msg || JSON.stringify(data.detail);
    } else if (data.message) {
      errorMsg = typeof data.message === 'string' ? data.message : JSON.stringify(data.message);
    }
    throw new Error(errorMsg);
  }

  return data;
}

export const api = {
  login: (username, password) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  getMe: () => apiRequest('/auth/me'),

  // User Management
  getUsers: (params = {}) => {
    const searchParams = new URLSearchParams();
    if (params.skip !== undefined) searchParams.append('skip', params.skip);
    if (params.limit !== undefined) searchParams.append('limit', params.limit);
    if (params.role) searchParams.append('role', params.role);
    if (params.is_active !== undefined && params.is_active !== null) searchParams.append('is_active', params.is_active);
    if (params.search) searchParams.append('search', params.search);
    return apiRequest(`/users?${searchParams.toString()}`);
  },
  createUser: (userData) =>
    apiRequest('/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  getUser: (id) => apiRequest(`/users/${id}`),
  updateUser: (id, userData) =>
    apiRequest(`/users/${id}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    }),
  updateUserStatus: (id, is_active) =>
    apiRequest(`/users/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    }),

  // Academic Structure
  getDepartments: () => apiRequest('/departments'),
  getAcademicYears: () => apiRequest('/academic-years'),
  getSemesters: (academicYearId) =>
    apiRequest(`/semesters${academicYearId ? `?academic_year_id=${academicYearId}` : ''}`),
  getAcademicClasses: (departmentId) =>
    apiRequest(`/academic-classes${departmentId ? `?department_id=${departmentId}` : ''}`),
  getDivisions: (classId) =>
    apiRequest(`/divisions${classId ? `?academic_class_id=${classId}` : ''}`),
  getBatches: (divisionId) =>
    apiRequest(`/batches${divisionId ? `?division_id=${divisionId}` : ''}`),
  getSubjects: (departmentId, semesterId) => {
    const params = new URLSearchParams();
    if (departmentId) params.append('department_id', departmentId);
    if (semesterId) params.append('semester_id', semesterId);
    return apiRequest(`/subjects?${params.toString()}`);
  },
  getTeachers: async (departmentId) => {
    try {
      const res = await api.getUsers({ role: 'TEACHER', limit: 100 });
      let items = res.items || [];
      if (departmentId) {
        items = items.filter(u => u.teacher_profile && u.teacher_profile.department_id === parseInt(departmentId));
      }
      return items.map(u => ({
        id: u.teacher_profile?.id || u.id,
        employee_id: u.teacher_profile?.employee_id || `EMP-00${u.id}`,
        full_name: u.teacher_profile?.full_name || u.full_name || u.username,
        email: u.email,
        department_id: u.teacher_profile?.department_id || 1,
      }));
    } catch (err) {
      return [];
    }
  },
  getStudents: async (params = {}) => {
    try {
      const res = await api.getUsers({ role: 'STUDENT', limit: 100 });
      let items = res.items || [];
      if (params.division_id) {
        items = items.filter(u => u.student_profile && u.student_profile.division_id === parseInt(params.division_id));
      }
      return items.map(u => ({
        id: u.student_profile?.id || u.id,
        roll_number: u.student_profile?.roll_number || `RN-00${u.id}`,
        full_name: u.student_profile?.full_name || u.full_name || u.username,
        email: u.email,
        division_id: u.student_profile?.division_id || 1,
      }));
    } catch (err) {
      return [];
    }
  },
  getEnrollments: (divisionId) =>
    apiRequest(`/enrollments${divisionId ? `?division_id=${divisionId}` : ''}`),
  getSubjectAssignments: (teacherId) =>
    apiRequest(`/subject-assignments${teacherId ? `?teacher_id=${teacherId}` : ''}`),

  // Timetable Management
  getTimetables: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        params.append(key, val);
      }
    });
    return apiRequest(`/timetable?${params.toString()}`);
  },
  createTimetable: (data) =>
    apiRequest('/timetable', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateTimetableStatus: (id, is_active) =>
    apiRequest(`/timetable/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    }),

  // Attendance Sessions
  createSession: (payload) =>
    apiRequest('/attendance-sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getSessions: (filters = {}) => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        params.append(key, val);
      }
    });
    return apiRequest(`/attendance-sessions?${params.toString()}`);
  },

  getSessionByToken: (token) => apiRequest(`/attendance-sessions/token/${token}`),
  closeSession: (id) => apiRequest(`/attendance-sessions/${id}/close`, { method: 'PATCH' }),
  cancelSession: (id) => apiRequest(`/attendance-sessions/${id}/cancel`, { method: 'PATCH' }),

  // Attendance Marking & Records
  studentMarkAttendance: (session_token) =>
    apiRequest('/attendance/mark', {
      method: 'POST',
      body: JSON.stringify({ session_token }),
    }),

  manualMarkAttendance: (sessionId, records) =>
    apiRequest(`/attendance/sessions/${sessionId}/manual-mark`, {
      method: 'POST',
      body: JSON.stringify({ records }),
    }),

  getSessionRecords: (sessionId) => apiRequest(`/attendance/sessions/${sessionId}/records`),

  correctAttendance: (recordId, new_status, reason) =>
    apiRequest(`/attendance/records/${recordId}/correct`, {
      method: 'PATCH',
      body: JSON.stringify({ new_status, reason }),
    }),

  getAuditLogs: () => apiRequest('/attendance/audit-logs'),
  getMyHistory: () => apiRequest('/attendance/my-history'),

  // Reports
  getMySummary: () => apiRequest('/attendance/my-summary'),
  getStudentSummary: (studentId) => apiRequest(`/attendance/students/${studentId}/summary`),
  getDefaulters: (divisionId, threshold = 75, academicYearId = null) => {
    const params = new URLSearchParams();
    params.append('threshold_percentage', threshold);
    if (divisionId) params.append('division_id', divisionId);
    if (academicYearId) params.append('academic_year_id', academicYearId);
    return apiRequest(`/reports/defaulters?${params.toString()}`);
  },
};

