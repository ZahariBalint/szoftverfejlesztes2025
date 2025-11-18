const API_BASE = "/api/admin"; // Igazítsd a meglévő admin útvonalhoz

function getToken() {
    return localStorage.getItem("access_token");
}

function authHeaders() {
    const token = getToken();
    return {
        "Content-Type": "application/json",
        "Authorization": token ? "Bearer " + token : ""
    };
}

function goToDashboard() {
    window.location.href = "/dashboard";
}

function logout() {
    localStorage.removeItem("access_token");
    window.location.href = "/login";
}

// --- Felhasználó jelenlétek betöltése ---
async function loadUserAttendance() {
    const userIdentifier = document.getElementById("userIdentifier").value.trim();
    const fromDate = document.getElementById("fromDate").value;
    const toDate = document.getElementById("toDate").value;
    const statusEl = document.getElementById("attendanceStatus");
    const tbody = document.querySelector("#attendanceTable tbody");
    tbody.innerHTML = "";
    statusEl.textContent = "Jelenlétek lekérése folyamatban...";

    if (!userIdentifier) {
        statusEl.textContent = "Adj meg egy felhasználó azonosítót vagy felhasználónevet.";
        statusEl.classList.add("error");
        return;
    }

    try {
        const params = new URLSearchParams();
        if (fromDate) params.append("from", fromDate);
        if (toDate) params.append("to", toDate);

        const response = await fetch(`${API_BASE}/users/${encodeURIComponent(userIdentifier)}/attendance?` + params.toString(), {
            method: "GET",
            headers: authHeaders()
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            statusEl.textContent = err.error || "Hiba történt a jelenlétek lekérése közben.";
            statusEl.classList.add("error");
            return;
        }

        const data = await response.json();
        statusEl.textContent = `Összesen ${data.length || 0} jelenléti rekord.`;
        statusEl.classList.remove("error");
        statusEl.classList.add("success");

        if (!data || data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='5'>Nincs jelenléti adat a megadott szűrőkkel.</td></tr>";
            return;
        }

        data.forEach(rec => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${escapeHtml(rec.date || "")}</td>
                <td>${escapeHtml(rec.check_in || "")}</td>
                <td>${escapeHtml(rec.check_out || "")}</td>
                <td>${escapeHtml(rec.work_location || "")}</td>
                <td>${rec.work_duration != null ? rec.work_duration/60 : ""}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        console.error(e);
        statusEl.textContent = "Váratlan hiba történt.";
        statusEl.classList.add("error");
    }
}

// --- Módosítási kérelmek betöltése ---
async function loadModificationRequests() {
    const statusEl = document.getElementById("modReqStatus");
    const tbody = document.querySelector("#modRequestsTable tbody");
    tbody.innerHTML = "";
    statusEl.textContent = "Módosítási kérelmek betöltése...";

    try {
        const response = await fetch(`${API_BASE}/modification-requests?status=pending`, {
            method: "GET",
            headers: authHeaders()
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            statusEl.textContent = err.error || "Hiba történt a módosítási kérelmek lekérésekor.";
            statusEl.classList.add("error");
            return;
        }

        const data = await response.json();
        statusEl.textContent = `Összesen ${data.length || 0} függő módosítási kérelem.`;
        statusEl.classList.remove("error");

        if (!data || data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='6'>Nincs függő módosítási kérelem.</td></tr>";
            return;
        }

        data.forEach(req => {
            const tr = document.createElement("tr");
            const statusClass = statusTagClass(req.status);
            tr.innerHTML = `
                <td>${req.id}</td>
                <td>${escapeHtml(req.username || req.user_id || "")}</td>
                <td>${escapeHtml(req.period || req.date || "")}</td>
                <td>${escapeHtml(req.reason || "")}</td>
                <td><span class="tag ${statusClass}">${escapeHtml(req.status || "")}</span></td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="reviewModificationRequest(${req.id}, true)">Elfogadás</button>
                    <button class="btn btn-sm btn-danger" onclick="reviewModificationRequest(${req.id}, false)">Elutasítás</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
        statusEl.textContent = "Váratlan hiba történt.";
        statusEl.classList.add("error");
    }
}

async function reviewModificationRequest(id, approve) {
    const reason = !approve ? prompt("Elutasítás indoka:") : null;
    const statusEl = document.getElementById("modReqStatus");

    try {
        // Igazítsd az endpointot:
        // pl.: POST /api/admin/modification-requests/<id>/review { "approve": true/false, "reason": "..." }
        const response = await fetch(`${API_BASE}/modification-requests/${id}/review`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({
                approve: approve,
                reason: reason || null
            })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            statusEl.textContent = err.error || "Nem sikerült a kérelem elbírálása.";
            statusEl.classList.add("error");
            return;
        }

        statusEl.textContent = approve ? "Kérelem elfogadva." : "Kérelem elutasítva.";
        statusEl.classList.remove("error");
        statusEl.classList.add("success");
        await loadModificationRequests();
    } catch (e) {
        console.error(e);
        statusEl.textContent = "Váratlan hiba történt elbírálás közben.";
        statusEl.classList.add("error");
    }
}

// --- Túlóra kérelmek betöltése ---
async function loadOvertimeRequests() {
    const statusEl = document.getElementById("overtimeStatus");
    const tbody = document.querySelector("#overtimeTable tbody");
    tbody.innerHTML = "";
    statusEl.textContent = "Túlóra kérelmek betöltése...";

    try {
        // Igazítsd az endpointot:
        // pl.: GET /api/admin/overtime-requests?status=pending
        const response = await fetch(`${API_BASE}/overtime-requests?status=pending`, {
            method: "GET",
            headers: authHeaders()
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            statusEl.textContent = err.error || "Hiba történt a túlóra kérelmek lekérésekor.";
            statusEl.classList.add("error");
            return;
        }

        const data = await response.json();
        statusEl.textContent = `Összesen ${data.length || 0} függő túlóra kérelem.`;
        statusEl.classList.remove("error");

        if (!data || data.length === 0) {
            tbody.innerHTML = "<tr><td colspan='8'>Nincs függő túlóra kérelem.</td></tr>";
            return;
        }

        data.forEach(req => {
            const tr = document.createElement("tr");
            const statusClass = statusTagClass(req.status);
            tr.innerHTML = `
                <td>${req.id}</td>
                <td>${escapeHtml(req.username || req.user_id || "")}</td>
                <td>${escapeHtml(req.work_session_id || "")}</td>
                <td>${req.overtime_minutes}</td>
                <td>${escapeHtml(req.request_date || "")}</td>
                <td><span class="tag ${statusClass}">${escapeHtml(req.status || "")}</span></td>
                <td>
                    <input class="reason-input" type="text" id="ot-reason-${req.id}" placeholder="Elutasítás indoka (opcionális)">
                </td>
                <td>
                    <button class="btn btn-sm btn-success" onclick="reviewOvertimeRequest(${req.id}, true)">Elfogadás</button>
                    <button class="btn btn-sm btn-danger" onclick="reviewOvertimeRequest(${req.id}, false)">Elutasítás</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
        statusEl.textContent = "Váratlan hiba történt.";
        statusEl.classList.add("error");
    }
}

async function reviewOvertimeRequest(id, approve) {
    const reasonInput = document.getElementById(`ot-reason-${id}`);
    const reason = !approve && reasonInput ? reasonInput.value.trim() : null;
    const statusEl = document.getElementById("overtimeStatus");

    try {
        // Igazítsd az endpointot:
        // pl.: POST /api/admin/overtime-requests/<id>/review { "approve": true/false, "reason": "..." }
        const response = await fetch(`${API_BASE}/overtime-requests/${id}/review`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({
                approve: approve,
                reason: reason || null
            })
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            statusEl.textContent = err.error || "Nem sikerült a túlóra kérelem elbírálása.";
            statusEl.classList.add("error");
            return;
        }

        statusEl.textContent = approve ? "Túlóra kérelem elfogadva." : "Túlóra kérelem elutasítva.";
        statusEl.classList.remove("error");
        statusEl.classList.add("success");
        await loadOvertimeRequests();
    } catch (e) {
        console.error(e);
        statusEl.textContent = "Váratlan hiba történt elbírálás közben.";
        statusEl.classList.add("error");
    }
}

// --- Segédfüggvények ---
function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function statusTagClass(status) {
    if (!status) return "tag";
    const s = String(status).toLowerCase();
    if (s === "pending") return "tag tag-pending";
    if (s === "approved") return "tag tag-approved";
    if (s === "rejected") return "tag tag-rejected";
    return "tag";
}

// Oldal betöltésekor automatikusan lekérjük a függő kérelmeket
document.addEventListener("DOMContentLoaded", () => {
    if (!getToken()) {
        // Ha nincs token, irány a login
        window.location.href = "/login";
        return;
    }
    loadModificationRequests();
    loadOvertimeRequests();
});