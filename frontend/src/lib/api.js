const API_BASE = import.meta.env.VITE_API_URL || '';

function getAuthHeaders() {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

export async function loginUser(email, password) {
  const formData = new URLSearchParams();
  formData.append('username', email); // OAuth2 requires username field
  formData.append('password', password);
  
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString()
  });
  
  if (!res.ok) {
    let errMsg = 'Login failed';
    try { const errData = await res.json(); errMsg = errData.detail || errMsg; } catch(e) { errMsg = `Server error ${res.status}: ${res.statusText}`; }
    throw new Error(errMsg);
  }
  
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function signupUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (!res.ok) {
    let errMsg = 'Signup failed';
    try { const errData = await res.json(); errMsg = errData.detail || errMsg; } catch(e) { errMsg = `Server error ${res.status}: ${res.statusText}`; }
    throw new Error(errMsg);
  }
  
  return res.json();
}

export function logoutUser() {
  localStorage.removeItem('token');
}

export async function reviewResume(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/review-resume`, { 
    method: 'POST', 
    headers: getAuthHeaders(),
    body: formData 
  });
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}

export async function matchResume(file, jobDescription) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('job_description', jobDescription);
  const res = await fetch(`${API_BASE}/match-resume`, { 
    method: 'POST', 
    headers: getAuthHeaders(),
    body: formData 
  });
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}

export async function fetchHistory() {
  const res = await fetch(`${API_BASE}/history`, { headers: getAuthHeaders() });
  if (!res.ok) {
    if (res.status === 401) logoutUser();
    throw new Error('Failed to fetch history');
  }
  return res.json();
}

export async function fetchMatchHistory() {
  const res = await fetch(`${API_BASE}/match-history`, { headers: getAuthHeaders() });
  if (!res.ok) {
    if (res.status === 401) logoutUser();
    throw new Error('Failed to fetch match history');
  }
  return res.json();
}

export async function searchResumes(query) {
  const res = await fetch(`${API_BASE}/search-resumes?query=${encodeURIComponent(query)}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error((await res.json()).detail || res.statusText);
  return res.json();
}
