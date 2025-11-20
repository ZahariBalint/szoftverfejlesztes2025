const API_BASE_URL = 'http://127.0.0.1:5000/api';

const TIME_START_HOUR = 6;
const TIME_END_HOUR = 20;
const TOTAL_MINUTES = (TIME_END_HOUR - TIME_START_HOUR) * 60;

// DOM elements
const timerBtn = document.getElementById('timerBtn');
const timerText = document.getElementById('timerText');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logoutBtn');
const prevWeekBtn = document.getElementById('prevWeekBtn');
const nextWeekBtn = document.getElementById('nextWeekBtn');
const todayBtn = document.getElementById('todayBtn');
const weekRangeSpan = document.getElementById('weekRange');
const modificationModal = document.getElementById('modificationModal');
const modificationForm = document.getElementById('modificationForm');
const closeModalBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');
const successCheckmark = document.getElementById('successCheckmark');

// State
let weeklyData = null;
let activeSession = null;
let updateInterval = null;
let timerUpdateInterval = null;
let currentWeekStart = null;

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserInfo();
    loadWeeklyData();
    setupEventListeners();
});

function checkAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }
}

function loadUserInfo() {
    const userStr = localStorage.getItem('user');
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            usernameSpan.textContent = user.username || 'Felhasználó';
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
}

function setupEventListeners() {
    logoutBtn.addEventListener('click', handleLogout);
    timerBtn.addEventListener('click', handleTimerClick);
    prevWeekBtn.addEventListener('click', () => navigateWeek(-1));
    nextWeekBtn.addEventListener('click', () => navigateWeek(1));
    todayBtn.addEventListener('click', goToCurrentWeek);
}

function handleLogout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
}

async function loadWeeklyData(weekStart = null) {
    try {
        const token = localStorage.getItem('access_token');
        let url = `${API_BASE_URL}/attendance/weekly`;
        if (weekStart) {
            url += `?week_start=${weekStart}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load weekly data');
        }

        const data = await response.json();
        weeklyData = data.weekly_data;
        activeSession = data.active_session;
        currentWeekStart = data.week_start;

        renderWeeklyView();
        updateWeekRange();
        updateTimerButton();
        startActiveSessionUpdate();
    } catch (error) {
        console.error('Error loading weekly data:', error);
        alert('Hiba történt az adatok betöltése során.');
    }
}

function renderWeeklyView() {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

    days.forEach((day) => {
        const contentDiv = document.getElementById(`${day.toLowerCase()}-content`);
        const dateDiv = document.getElementById(`${day.toLowerCase()}-date`);
        if (!contentDiv || !dateDiv) return;

        contentDiv.innerHTML = '';

        const dayData = weeklyData[day];

        if (dayData && dayData.date) {
            const date = new Date(dayData.date);
            dateDiv.textContent = formatDate(date);
        } else {
            dateDiv.textContent = '';
        }

        if (dayData && dayData.sessions && dayData.sessions.length > 0) {
            dayData.sessions.forEach(session => {
                const bar = createWorkBar(session, day);
                if (bar) {
                    contentDiv.appendChild(bar);
                }
            });
        }
    });
}

function formatDate(date) {
    const months = ['január', 'február', 'március', 'április', 'május', 'június',
        'július', 'augusztus', 'szeptember', 'október', 'november', 'december'];
    return `${date.getFullYear()}. ${months[date.getMonth()]} ${date.getDate()}.`;
}

function formatWeekRange(weekStart, weekEnd) {
    const start = new Date(weekStart);
    const end = new Date(weekEnd);
    const months = ['január', 'február', 'március', 'április', 'május', 'június',
        'július', 'augusztus', 'szeptember', 'október', 'november', 'december'];

    if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
        return `${start.getFullYear()}. ${months[start.getMonth()]} ${start.getDate()}. - ${end.getDate()}.`;
    } else {
        return `${start.getFullYear()}. ${months[start.getMonth()]} ${start.getDate()}. - ${end.getFullYear()}. ${months[end.getMonth()]} ${end.getDate()}.`;
    }
}

function updateWeekRange() {
    if (weeklyData && currentWeekStart) {
        const monday = new Date(currentWeekStart);
        const sunday = new Date(monday);
        sunday.setDate(sunday.getDate() + 6);
        weekRangeSpan.textContent = formatWeekRange(monday, sunday);
    }
}

function navigateWeek(direction) {
    if (!currentWeekStart) return;

    const currentDate = new Date(currentWeekStart);
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() + (direction * 7));

    loadWeeklyData(newDate.toISOString().split('T')[0]);
}

function goToCurrentWeek() {
    loadWeeklyData();
}

function createWorkBar(session, day) {
    const bar = document.createElement('div');
    bar.className = 'work-bar';
    if (session.is_active) {
        bar.classList.add('active');
    }

    // Store session data in the bar
    bar.dataset.sessionId = session.id;
    bar.dataset.checkIn = session.check_in;
    bar.dataset.checkOut = session.check_out || '';
    bar.dataset.location = session.work_location || 'office';
    bar.dataset.overtimeStatus = session.overtime_status || '';

    const checkInTime = parseTime(session.check_in_time);
    const checkOutTime = session.check_out_time ? parseTime(session.check_out_time) : null;

    if (!checkInTime) return null;

    // Calculate top position
    const startMinutes = timeToMinutes(checkInTime);
    const topPercent = ((startMinutes - (TIME_START_HOUR * 60)) / TOTAL_MINUTES) * 100;

    // Calculate height
    let heightPercent;
    if (session.is_active && activeSession) {
        // Active session - use current duration
        const currentMinutes = activeSession.duration_minutes || 0;
        heightPercent = (currentMinutes / TOTAL_MINUTES) * 100;
    } else if (checkOutTime) {
        // Completed session
        const endMinutes = timeToMinutes(checkOutTime);
        const duration = endMinutes - startMinutes;
        heightPercent = (duration / TOTAL_MINUTES) * 100;

        // Apply overtime styling if pending
        if (session.overtime_status === 'pending') {
            bar.classList.add('pending-overtime');
            bar.title += ' (Túlóra jóváhagyásra vár)';
        } else if (session.overtime_status === 'approved') {
            bar.classList.add('approved-overtime');
            bar.title += ' (Túlóra jóváhagyva)';
        } else if (session.overtime_status === 'rejected') {
            bar.classList.add('rejected-overtime');
            bar.title += ' (Túlóra elutasítva)';
        }
    } else {
        // Fallback to duration_minutes
        heightPercent = (session.duration_minutes / TOTAL_MINUTES) * 100;
    }

    // Ensure bar doesn't go outside bounds
    const maxTop = 100 - heightPercent;
    const finalTop = Math.max(0, Math.min(topPercent, maxTop));

    bar.style.top = `${finalTop}%`;
    bar.style.height = `${heightPercent}%`;

    const label = document.createElement('div');
    label.className = 'work-bar-label';
    label.textContent = `${session.check_in_time}${session.check_out_time ? ` - ${session.check_out_time}` : ''}`;
    bar.appendChild(label);

    bar.title = `${session.check_in_time}${session.check_out_time ? ` - ${session.check_out_time}` : ' (aktív)'}`;

    // Add click event listener to open modification modal (only for completed sessions)
    if (!session.is_active && session.check_out) {
        bar.style.cursor = 'pointer';
        bar.addEventListener('click', () => openModificationModal(session));
    }

    return bar;
}

function parseTime(timeStr) {
    if (!timeStr) return null;
    const parts = timeStr.split(':');
    if (parts.length !== 2) return null;
    return {
        hours: parseInt(parts[0], 10),
        minutes: parseInt(parts[1], 10)
    };
}

function timeToMinutes(time) {
    return time.hours * 60 + time.minutes;
}

function updateTimerButton() {
    if (activeSession) {
        timerBtn.classList.add('active');
        timerText.textContent = 'Stop';
    } else {
        timerBtn.classList.remove('active');
        timerText.textContent = 'Start';
    }
}

function startActiveSessionUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    if (timerUpdateInterval) {
        clearInterval(timerUpdateInterval);
    }

    if (activeSession) {
        // Update bar every 10 seconds for smoother real-time updates
        updateInterval = setInterval(() => {
            if (activeSession) {
                // Update duration in active session
                const checkInTime = new Date(activeSession.check_in);
                const now = new Date();
                const diffMs = now - checkInTime;
                activeSession.duration_minutes = Math.floor(diffMs / 60000);

                updateActiveBar();
            }
        }, 10000);
    }
}

function updateActiveBar() {
    if (!activeSession) return;

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    let dayName = null;

    for (const day of days) {
        const sessions = weeklyData[day]?.sessions || [];
        if (sessions.some(s => s.is_active)) {
            dayName = day;
            break;
        }
    }

    if (!dayName) return;

    const contentDiv = document.getElementById(`${dayName.toLowerCase()}-content`);
    if (!contentDiv) return;

    // Find and update active bar
    const activeBar = contentDiv.querySelector('.work-bar.active');
    if (activeBar) {
        const session = weeklyData[dayName]?.sessions?.find(s => s.is_active);
        if (session) {
            const checkInTime = parseTime(session.check_in_time);
            if (checkInTime) {
                const startMinutes = timeToMinutes(checkInTime);
                const topPercent = ((startMinutes - (TIME_START_HOUR * 60)) / TOTAL_MINUTES) * 100;
                const heightPercent = (activeSession.duration_minutes / TOTAL_MINUTES) * 100;

                const maxTop = 100 - heightPercent;
                const finalTop = Math.max(0, Math.min(topPercent, maxTop));

                activeBar.style.top = `${finalTop}%`;
                activeBar.style.height = `${heightPercent}%`;
            }
        }
    }
}

async function handleTimerClick() {
    if (timerBtn.disabled) return;

    timerBtn.disabled = true;

    try {
        const token = localStorage.getItem('access_token');
        const endpoint = activeSession ? '/attendance/checkout' : '/attendance/checkin';

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: activeSession ? JSON.stringify({}) : JSON.stringify({ location: 'office' })
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Hiba történt');
        }

        // After check-in/check-out, reload current week (where the action happened)
        // Then navigate to current week if viewing a different week
        const today = new Date();
        const daysSinceMonday = today.getDay() === 0 ? 6 : today.getDay() - 1;
        const currentWeekMonday = new Date(today);
        currentWeekMonday.setDate(today.getDate() - daysSinceMonday);

        await loadWeeklyData(currentWeekMonday.toISOString().split('T')[0]);

    } catch (error) {
        console.error('Error with check-in/check-out:', error);
        alert(error.message || 'Hiba történt a művelet során.');
    } finally {
        timerBtn.disabled = false;
    }
}

// Modal functions
function openModificationModal(session) {
    // Fill in the form with session data
    document.getElementById('workSessionId').value = session.id;
    document.getElementById('originalCheckIn').value = formatDateTimeForDisplay(session.check_in);
    document.getElementById('originalCheckOut').value = session.check_out ? formatDateTimeForDisplay(session.check_out) : 'N/A';

    // Show overtime status if present
    const modalHeader = document.querySelector('.modal-header h2');
    if (session.overtime_status === 'pending') {
        modalHeader.innerHTML = 'Módosítási kérelem <span class="status-badge pending">Túlóra jóváhagyásra vár</span>';
    } else if (session.overtime_status === 'approved') {
        modalHeader.innerHTML = 'Módosítási kérelem <span class="status-badge approved">Túlóra jóváhagyva</span>';
    } else if (session.overtime_status === 'rejected') {
        modalHeader.innerHTML = 'Módosítási kérelem <span class="status-badge rejected">Túlóra elutasítva</span>';
    } else {
        modalHeader.textContent = 'Módosítási kérelem';
    }

    // Pre-fill requested times with original times
    if (session.check_in) {
        document.getElementById('requestedCheckIn').value = formatDateTimeForInput(session.check_in);
    }
    if (session.check_out) {
        document.getElementById('requestedCheckOut').value = formatDateTimeForInput(session.check_out);
    }

    // Reset other fields
    document.getElementById('requestedLocation').value = '';
    document.getElementById('reason').value = '';

    // Show modal
    modificationModal.classList.add('show');
}

function closeModificationModal() {
    modificationModal.classList.remove('show');
    modificationForm.reset();
    if (successCheckmark) successCheckmark.style.display = 'none';
}

function formatDateTimeForDisplay(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleString('hu-HU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDateTimeForInput(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    // Format as YYYY-MM-DDTHH:MM for datetime-local input
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

// Event listeners for modal
closeModalBtn.addEventListener('click', closeModificationModal);
cancelBtn.addEventListener('click', closeModificationModal);

// Close modal when clicking outside of it
window.addEventListener('click', (event) => {
    if (event.target === modificationModal) {
        closeModificationModal();
    }
});

// Handle modification form submission
modificationForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const submitBtn = modificationForm.querySelector('.btn-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Küldés...';

    try {
        const token = localStorage.getItem('access_token');
        const formData = {
            work_session_id: parseInt(document.getElementById('workSessionId').value),
            reason: document.getElementById('reason').value
        };

        console.log('Submitting modification request:', formData);

        // Add optional fields only if they have values
        const requestedCheckIn = document.getElementById('requestedCheckIn').value;
        if (requestedCheckIn) {
            formData.requested_check_in = new Date(requestedCheckIn).toISOString();
        }

        const requestedCheckOut = document.getElementById('requestedCheckOut').value;
        if (requestedCheckOut) {
            formData.requested_check_out = new Date(requestedCheckOut).toISOString();
        }

        const requestedLocation = document.getElementById('requestedLocation').value;
        if (requestedLocation) {
            formData.requested_location = requestedLocation;
        }

        console.log('Final form data:', formData);

        const response = await fetch(`${API_BASE_URL}/attendance/modifications`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        if (response.status === 401) {
            handleLogout();
            return;
        }

        if (!response.ok) {
            const data = await response.json().catch(() => ({ error: 'Unknown error' }));
            console.error('Server error response:', data);
            throw new Error(data.error || `Server error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();

        // Success
        if (successCheckmark) {
            successCheckmark.style.display = 'flex';
            // Wait for animation then close
            setTimeout(() => {
                closeModificationModal();
            }, 2000);
        } else {
            alert('Módosítási kérelem sikeresen beküldve!');
            closeModificationModal();
        }

    } catch (error) {
        console.error('Error submitting modification request:', error);
        alert(error.message || 'Hiba történt a kérelem beküldése során.');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Kérelem beküldése';
    }
});

