// script.js - unified frontend for dashboard + sidebar + modules

const API = ""; // same origin
let token = null;
let me = null;
let socket = null;
let currentGroup = null;
let currentModule = null;

// --- DOM helpers
const $ = id => document.getElementById(id);
const show = el => el && el.classList.remove('hidden');
const hide = el => el && el.classList.add('hidden');

// initial view
showRegister();

function showRegister(){
  $('brand').innerText = 'Register';
  show($('register-form')); hide($('login-form')); hide($('profile-view')); hide($('dashboard-view'));
  hide($('module-card')); hide($('sidebar'));
}
function showLogin(){
  $('brand').innerText = 'Login';
  hide($('register-form')); show($('login-form')); hide($('profile-view')); hide($('dashboard-view'));
  hide($('module-card')); hide($('sidebar'));
}
function showProfile(){
  hide($('register-form')); hide($('login-form')); show($('profile-view')); hide($('dashboard-view'));
  hide($('module-card')); hide($('sidebar'));
  if(me) $('profile-info').innerHTML = `<strong>${me.username}</strong><br>Role: ${me.role}`;
}
function showDashboard(){
  hide($('register-form')); hide($('login-form')); hide($('profile-view'));
  show($('dashboard-view')); hide($('module-card')); hide($('sidebar'));
  document.body.classList.remove('sidebar-open');
  loadModules();
}

async function register(){
  const username = $('reg-username').value.trim();
  const password = $('reg-password').value;
  const role = $('reg-role').value;
  
  if(!username || !password){ 
      $('reg-msg').innerText='Enter username & password'; 
      return; 
  }
    
  $('reg-msg').innerText = 'Registering...';

  try {
    const res = await fetch('/api/user/register', {
        method:'POST', 
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({username, password, role, profile:{}})
    });

    if(res.status === 201){ 
        $('reg-msg').innerText = 'Registered — please login'; 
        showLogin(); 
    } else {
        // Handle errors (including non-JSON errors like 400 Bad Request)
        let errorMsg = `Registration failed (Status: ${res.status})`;
        try {
            const j = await res.json();
            errorMsg = j.error || errorMsg;
        } catch (e) {
            // If JSON parse fails, read plain text response
            const text = await res.text();
            if(text) errorMsg = text; // Often contains "username exists"
        }
        $('reg-msg').innerText = errorMsg;
    }
  } catch (err) {
      console.error(err);
      $('reg-msg').innerText = 'Registration failed: Network error.';
  }
}

async function login(){
  const username = $('login-username').value.trim();
  const password = $('login-password').value;
  
  if(!username || !password){ 
    $('login-msg').innerText='Enter credentials'; 
    return; 
  }
  
  $('login-msg').innerText = 'Logging in...';

  try {
    const res = await fetch('/api/user/login', {
      method:'POST', 
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username, password})
    });

    if (res.ok) {
       const j = await res.json();
       if (j.token) {
           token = j.token; 
           me = j.user; 
           $('login-msg').innerText = 'Login success';
           await fetchProfile(); 
           showDashboard(); 
           initSocket();
       } else {
           $('login-msg').innerText = 'Login failed: No token received.';
       }
    } else {
       // Handle server errors gracefully
       let errorMsg = 'Login failed';
       try {
           const j = await res.json();
           errorMsg = j.error || errorMsg;
       } catch (e) {
           const text = await res.text();
           errorMsg = text || `Login failed (Status: ${res.status})`;
       }
       $('login-msg').innerText = errorMsg;
    }
  } catch (err) {
     console.error(err);
     $('login-msg').innerText = 'Login failed: Network error.';
  }
}

async function fetchProfile(){
  const res = await fetch('/api/user/me', { headers: { 'Authorization': token } });
  if(res.ok){ me = await res.json(); }
}

function logout(){
  token = null; me = null;
  if(socket) socket.disconnect();
  socket = null; currentGroup = null; currentModule = null;
  showLogin();
}

// -------- Dashboard & modules --------
async function loadModules(){
  if(!me) return;
  const role = me.role || 'student';
  const res = await fetch(`/api/dashboard/modules?role=${role}`);
  const j = await res.json();
  const grid = $('modules-grid'); grid.innerHTML = '';
  $('modules-count').innerText = `${j.count || j.modules.length} modules available`;
  j.modules.forEach(m => {
    const el = document.createElement('div');
    el.className = 'module-card-item';
    el.dataset.moduleId = m.id;
    el.innerHTML = `<div class="title">${m.title}</div><div class="desc">${m.description}</div>`;
    el.onclick = () => openModule(m.id, m.title);
    grid.appendChild(el);
  });
}

// enable sidebar mode and build vertical menu
function enableSidebarMode(modules){
  hide($('dashboard-view'));
  show($('sidebar'));
  const sb = $('sidebar-modules'); sb.innerHTML = '';
  modules.forEach(m => {
    const node = document.createElement('div');
    node.className = 'sidebar-item';
    node.innerText = m.title;
    node.onclick = () => openModule(m.id, m.title);
    sb.appendChild(node);
  });
  document.body.classList.add('sidebar-open');
}

// open module - activates sidebar mode and shows module panel
async function openModule(id, title){
  currentModule = id;
  $('module-title').innerText = title;
  // load modules list to populate sidebar
  const res = await fetch(`/api/dashboard/modules?role=${me.role}`);
  const j = await res.json();
  const modules = j.modules || [];
  enableSidebarMode(modules);

  // show module-card and relevant UI pane
  show($('module-card'));
  const panes = document.querySelectorAll('.module');
  panes.forEach(p => p.classList.add('hidden'));
  const map = {
    'attendance': 'attendance-ui',
    'lms': 'lms-ui',
    'progress_report': 'progress-ui',
    'notifications': 'notifications-ui',
    'chat': 'chat-ui',
    'exams': 'exams-ui',
    'calendar': 'calendar-ui',
    'analytics': 'analytics-ui',
    'course_management': 'course-ui',
    'document_management': 'docs-ui',
    'storage_management': 'storage-ui',
    'task_management': 'tasks-ui',
    'user_management': 'user_mgmt-ui'
  };
  const paneId = map[id];
  if(paneId) show($(paneId));
  // specialized actions
  if(id === 'chat') listGroups();
  if(id === 'lms') $('lms-username').value = me.username || '';
  if(id === 'attendance'){
    // if student show student view
    if(me.role === 'student'){
      show($('student-view'));
      $('my-roll').innerText = me.profile && me.profile.rollno ? me.profile.rollno : 'N/A';
    } else {
      show($('present-input')); hide($('student-view'));
    }
  }
}

// back to centered dashboard
function backToDashboard(){
  hide($('module-card'));
  hide($('sidebar'));
  document.body.classList.remove('sidebar-open');
  showDashboard();
}

// -------- Attendance actions --------
async function loadGroupMembers(){
  const gid = $('att-group-id').value.trim();
  if(!gid){ alert('Enter group id'); return; }
  const res = await fetch(`/api/attendance/group_members?group_id=${encodeURIComponent(gid)}`);
  const j = await res.json();
  if(j.error){ $('group-members-list').innerText = j.error; return; }
  const list = $('group-members-list'); list.innerHTML = '';
  j.forEach(s => {
    const div = document.createElement('div');
    div.innerText = `${s.rollno} — ${s.name}`;
    list.appendChild(div);
  });
  show($('present-input'));
}
async function submitAttendance(){
  const gid = $('att-group-id').value.trim();
  const present = $('present-rolls').value.split(',').map(x=>x.trim()).filter(x=>x).map(Number);
  const payload = { role: me.role, group_id: gid, present };
  const res = await fetch('/api/attendance/mark', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
  const j = await res.json();
  $('attendance-result').innerText = JSON.stringify(j,null,2);
}
async function viewMyAttendance(){
  const roll = $('progress-roll').value || (me.profile && me.profile.rollno);
  if(!roll){ alert('roll missing'); return; }
  const res = await fetch(`/api/attendance/my?rollno=${encodeURIComponent(roll)}`);
  const j = await res.json();
  $('my-attendance-result').innerText = JSON.stringify(j,null,2);
}

// -------- LMS actions (file upload & list) --------
async function uploadLmsFile(){
  const gid = $('lms-group-id').value.trim();
  const username = $('lms-username').value.trim() || me.username;
  const fileInput = $('lms-file');
  if(!gid || !fileInput.files.length){ alert('Group ID and file required'); return; }
  const fd = new FormData();
  fd.append('group_id', gid);
  fd.append('username', username);
  fd.append('file', fileInput.files[0]);
  const res = await fetch('/api/lms/upload', { method:'POST', body: fd });
  const j = await res.json();
  alert(j.uploaded ? 'Uploaded' : (j.error || 'Upload failed'));
}

async function listLmsFiles(){
  const gid = $('lms-group-id').value.trim();
  if(!gid){ alert('Group ID required'); return; }
  const res = await fetch(`/api/lms/files?group_id=${encodeURIComponent(gid)}`);
  const j = await res.json();
  const el = $('lms-files'); el.innerHTML = '';
  if(j.files && j.files.length){
    j.files.forEach(f => {
      const a = document.createElement('div');
      a.innerHTML = `<strong>${f.filename}</strong> — ${f.uploaded_by} <br><a href="${f.url}" target="_blank">Open / Download</a>`;
      el.appendChild(a);
    });
  } else el.innerText = 'No files';
}

// -------- Progress (report) --------
async function loadProgress(){
  const roll = $('progress-roll').value || (me.profile && me.profile.rollno);
  if(!roll){ alert('Provide roll'); return; }
  const res = await fetch(`/api/progress/report/${encodeURIComponent(roll)}`);
  const j = await res.json();
  $('progress-result').innerText = JSON.stringify(j,null,2);
}

// -------- Notifications --------
async function sendNotification(){
  const target = $('notif-target').value.trim();
  const msg = $('notif-msg').value.trim();
  const type = $('notif-type').value;
  if(!target || !msg){ alert('target and message required'); return; }
  const payload = { role: me.role, msg };
  if(type === 'group'){ payload.group_id = target; await fetch('/api/notifications/send_group', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)}); }
  else { payload.username = target; await fetch('/api/notifications/send_user', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)}); }
  alert('Sent (if permitted)');
}
async function loadMyNotifs(){
  const username = me.username;
  const res = await fetch(`/api/notifications/list?username=${encodeURIComponent(username)}`);
  const j = await res.json();
  const el = $('notifs-list'); el.innerHTML = '';
  (j.notifications || []).forEach(n => {
    const node = document.createElement('div'); node.innerHTML = `<strong>${n.message}</strong><div style="font-size:12px;color:#ddd">${n.date}</div><hr>`;
    el.appendChild(node);
  });
}

// -------- Chat (socket.io) --------
function initSocket(){
  if(socket) return;
  socket = io();
  socket.on('connect', ()=> console.log('socket connected'));
  socket.on('receive_message', data => appendMessage(data.username, data.message, false));
  socket.on('system_message', data => appendSystem(data.msg));
  socket.on('typing', data => { $('typing-indicator').innerText = `${data.username} is typing...`; setTimeout(()=> $('typing-indicator').innerText='', 900); });
}
async function createGroup(){
  const groupName = $('chat-group-name').value || 'Group';
  const res = await fetch('/api/chat/create_group', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name: groupName})});
  const j = await res.json();
  $('groups-list').innerText = `Created group: ${j.group_id} (${j.group_name})`;
}
async function listGroups(){
  const res = await fetch('/api/chat/groups');
  const j = await res.json();
  $('groups-list').innerText = JSON.stringify(j,null,2);
}
async function joinGroup(){
  const groupId = $('chat-group').value.trim();
  const username = $('chat-username').value.trim() || me.username;
  if(!groupId || !username){ alert('enter group id and name'); return; }
  const res = await fetch('/api/chat/join_group', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({group_id: groupId, username})});
  const j = await res.json(); if(j.error){ alert(j.error); return; }
  initSocket();
  socket.emit('join_room', { group_id: groupId, username });
  currentGroup = groupId;
  $('chat-room-title').innerText = `Group: ${j.group.name} (${j.group.id})`;
  show($('chat-room')); hide($('groups-list'));
}
function sendChatMessage(){
  const text = $('chat-message-input').value.trim();
  const username = $('chat-username').value.trim() || me.username;
  if(!text || !currentGroup) return;
  socket.emit('send_message', { group_id: currentGroup, username, message: text });
  appendMessage(username, text, true);
  $('chat-message-input').value = '';
}
function appendMessage(username, text, meFlag){
  const box = $('chat-messages'); const div = document.createElement('div');
  div.className = 'chat-message' + (meFlag ? ' me' : '');
  div.innerHTML = `<strong>${username}</strong><div>${text}</div>`;
  box.appendChild(div); box.scrollTop = box.scrollHeight;
}
function appendSystem(msg){ const box = $('chat-messages'); const div = document.createElement('div'); div.style.textAlign='center'; div.style.opacity=0.9; div.style.fontStyle='italic'; div.innerText = msg; box.appendChild(div); box.scrollTop = box.scrollHeight; }
function emitTyping(){ const username = $('chat-username').value.trim() || me.username; if(!currentGroup || !username) return; socket.emit('typing', {group_id: currentGroup, username}); }

// -------- Exams & Calendar & Others (basic)
async function createExam(){
  const title = $('exam-title').value.trim(); const date = $('exam-date').value.trim();
  if(!title || !date){ alert('title & date required'); return; }
  await fetch('/api/exams/create', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title, date, role: me.role})});
  alert('Exam created');
}
async function loadExams(){ const res = await fetch('/api/exams/list'); const j = await res.json(); $('exams-list').innerText = JSON.stringify(j,null,2); }
async function loadEvents(){ const res = await fetch('/api/calendar/list'); const j = await res.json(); $('events-list').innerText = JSON.stringify(j,null,2); }
async function loadAnalytics(){ const res = await fetch('/api/analytics/overview'); const j = await res.json(); $('analytics-data').innerText = JSON.stringify(j,null,2); }
async function createCourse(){ const title = $('course-title').value.trim() || 'Untitled'; await fetch('/api/course/add', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title})}); loadCourses(); }
async function loadCourses(){ const res = await fetch('/api/course/list'); const j = await res.json(); $('course-list').innerText = JSON.stringify(j,null,2); }
async function uploadDoc(){ const name = $('doc-name').value||'doc'; const url = $('doc-url').value||''; await fetch('/api/docs/upload', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name,url})}); $('docs-list').innerText = JSON.stringify(await (await fetch('/api/docs/list')).json(),null,2); }
async function getUsage(){ $('storage-data').innerText = JSON.stringify(await (await fetch('/api/storage/usage')).json(),null,2); }
async function createTask(){ const title = $('task-title').value||'Task'; const assigned = $('task-assigned').value||me.username; await fetch('/api/tasks/create', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({title, desc:'', assigned_to: assigned})}); loadTasks(); }
async function loadTasks(){ const res = await fetch(`/api/tasks/list?user=${encodeURIComponent(me.username)}`); $('task-list').innerText = JSON.stringify(await res.json(),null,2); }
async function listUsers(){ $('users-list').innerText = JSON.stringify(await (await fetch('/api/user/list')).json(),null,2); }

// init socket after login
function initSocket(){ if(socket) return; socket = io(); socket.on('connect', ()=> console.log('socket connected')); socket.on('receive_message', data => appendMessage(data.username, data.message, false)); socket.on('system_message', data => appendSystem(data.msg)); socket.on('typing', data => { $('typing-indicator').innerText = `${data.username} is typing...`; setTimeout(()=> $('typing-indicator').innerText='', 900); }); }

// small helper to ensure dashboard modules load when returning
window.showDashboard = showDashboard;
window.openModule = openModule;

