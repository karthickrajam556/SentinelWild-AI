console.log("Dashboard JS Loaded");
const BASE_URL = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", function () {
  const role = localStorage.getItem("userRole");
  const name = localStorage.getItem("userName");

  if (!role) {
    window.location.href = "login.html";
    return;
  }

  document.getElementById("usernameDisplay").innerText = name;

  applyRoleAccess(role);

  loadStatus();
  loadIncidents();
  loadIncidentSummary();

  setInterval(loadStatus, 3000);
  setInterval(loadIncidents, 5000);
  setInterval(loadIncidentSummary, 5000);
  setInterval(checkForAlerts, 2000);
});

/* PROFILE */
function toggleProfile() {
  const dropdown = document.getElementById("profileDropdown");
  dropdown.style.display =
    dropdown.style.display === "block" ? "none" : "block";
}

function logout() {
  // Clear stored session data
  localStorage.removeItem("userRole");
  localStorage.removeItem("userName");

  // Optional: clear everything
  // localStorage.clear();

  // Redirect to login page
  window.location.href = "login.html";
}

function showToast(message, level) {
  const container = document.getElementById("toastContainer");

  const toast = document.createElement("div");
  toast.className = "toast " + level.toLowerCase();
  toast.innerText = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "fadeOut 0.5s forwards";
    setTimeout(() => toast.remove(), 500);
  }, 6000);
}

/* IMAGE UPLOAD */
async function uploadImage() {
  const fileInput = document.getElementById("imageInput");
  const file = fileInput.files[0];

  if (!file) {
    alert("Please select an image first");
    return;
  }

  const button = document.getElementById("imageUploadBtn");
  const spinner = document.getElementById("uploadSpinner");

  button.disabled = true;
  button.innerText = "Processing...";
  spinner.style.display = "block";

  // Show temporary status
  document.getElementById("statusText").innerText = "Processing";
  document.getElementById("statusDot").className = "status-dot status-active";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${BASE_URL}/input/upload-image`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      throw new Error("Server error");
    }

    const data = await res.json();

    if (data && data.decision) {
      showDetectionSummary(data);
    }
  } catch (error) {
    console.error("Upload Error:", error);
    alert("Upload failed. Check backend.");
  }

  // Reset UI
  document.getElementById("statusText").innerText = "Idle";
  document.getElementById("statusDot").className = "status-dot status-idle";

  button.disabled = false;
  button.innerText = "Upload";
  spinner.style.display = "none";
}

/* VIDEO UPLOAD */
async function uploadVideo() {
  const file = document.getElementById("videoInput").files[0];

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/input/upload-video-stream`, {
    method: "POST",
    body: formData,
  });

  if (response.ok) {
    document.getElementById("liveStream").src =
      `${BASE_URL}/input/video-stream`;
  }
}

/* WEBCAM */
function startWebcam() {
  document.getElementById("liveStream").src = `${BASE_URL}/input/webcam-stream`;
}

function stopWebcam() {
  fetch(`${BASE_URL}/input/stop-stream`, { method: "POST" });
  document.getElementById("liveStream").src = "";
  loadStatus();
}

/* LOAD STATUS */
async function loadStatus() {
  try {
    // ===== Threat Level =====
    const threatRes = await fetch(`${BASE_URL}/analytics/threat-level`);
    const threatData = await threatRes.json();

    console.log("Threat API Response:", threatData);

    // Try multiple possible keys
    const threat =
      threatData.threat_level ||
      threatData.level ||
      threatData.category ||
      threatData.current_threat ||
      "LOW";

    const threatElement = document.getElementById("threatLevel");
    threatElement.innerText = threat;
    threatElement.className = "threat-text threat-" + threat.toLowerCase();

    // ===== System Status =====
    const statusRes = await fetch(`${BASE_URL}/analytics/system-status`);

    if (statusRes.ok) {
      const statusData = await statusRes.json();
      const statusDot = document.getElementById("statusDot");
      const statusText = document.getElementById("statusText");

      if (statusData.status === "Active") {
        statusDot.className = "status-dot status-active";
        statusText.innerText = "Active";
      } else {
        statusDot.className = "status-dot status-idle";
        statusText.innerText = "Idle";
      }
    } else {
      document.getElementById("systemStatus").innerText = "Unknown";
    }
  } catch (error) {
    console.error("Dashboard Load Error:", error);
  }
}

console.log("loadStatus running...");

async function loadIncidents() {
  const res = await fetch(`${BASE_URL}/operations/incidents`);
  const data = await res.json();

  const tableBody = document.getElementById("incidentTableBody");
  tableBody.innerHTML = "";

  if (!Array.isArray(data) || data.length === 0) {
    tableBody.innerHTML = "<tr><td colspan='6'>No Incidents</td></tr>";
    return;
  }

  data.forEach((incident) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${incident.id}</td>
            <td>${incident.camera_id}</td>
            <td>${incident.animal_type}</td>
            <td>${incident.alert_level}</td>
            <td>${incident.zone}</td>
            <td>${incident.status}</td>
            <td>
              <button class="ack-btn"
                onclick="acknowledgeIncident(${incident.id})">
                Ack
              </button>

              <button class="resolve-btn"
                onclick="resolveIncident(${incident.id})">
                Resolve
              </button>

              <button class="feedback-btn"
                onclick="openFeedbackModal(${incident.id}, '${incident.animal_type}')">
                Give Feedback
              </button>
            </td>
        `;

    tableBody.appendChild(row);
  });
}

async function acknowledgeIncident(id) {
  await fetch(`${BASE_URL}/operations/acknowledge/${id}`, {
    method: "POST",
  });
  loadIncidents();
}

async function resolveIncident(id) {
  await fetch(`${BASE_URL}/operations/resolve/${id}`, {
    method: "POST",
  });
  loadIncidents();
}

async function checkForAlerts() {
  try {
    const res = await fetch(`${BASE_URL}/alerts/`);
    const data = await res.json();

    if (!data.alerts || data.alerts.length === 0) return;

    const latest = data.alerts[data.alerts.length - 1];

    const storedTime = localStorage.getItem("lastAlertTime");

    if (latest.timestamp !== storedTime) {
      showToast(
        `🚨 ${latest.alert_level} ALERT
    Animal: ${latest.animal_type}
    Camera-ID: ${latest.camera_id}
    Zone: ${latest.zone}
    Level: ${latest.alert_level}
    Risk Score: ${latest.risk_score}`,
        latest.alert_level,
      );

      localStorage.setItem("lastAlertTime", latest.timestamp);
    }
  } catch (error) {
    console.error("Alert Check Error:", error);
  }
}

function hideAllSections() {
  document.querySelector(".live-section").style.display = "none";
  document.getElementById("analyticsSection").style.display = "none";
  document.getElementById("reportSection").style.display = "none";
  document.getElementById("feedbackSection").style.display = "none";
}

function applyRoleAccess(role) {
  const reportBtn = document.querySelector("button[onclick='showReport()']");
  const feedbackBtn = document.querySelector(
    "button[onclick='showFeedback()']",
  );

  if (role === "forest") {
    // Forest Department cannot access reports & feedback
    if (reportBtn) reportBtn.style.display = "none";
    if (feedbackBtn) feedbackBtn.style.display = "none";
  }

  if (role === "admin") {
    // Admin sees everything
  }
}

function showAnalytics() {
  document.querySelector(".live-section").style.display = "none";
  document.getElementById("analyticsSection").style.display = "block";

  if (!wildlifeMap) {
    loadAnalytics();
    loadMap();
    loadDetectionMap();
  }
}
function showLive() {
  hideAllSections();
  document.querySelector(".live-section").style.display = "flex";
}

function loadAnalytics() {
  loadAnimalFrequency();
  loadTimePattern();
  loadRiskTrend();
  loadZoneVulnerability();
  loadPrediction();
  loadModelAccuracy();
}

async function loadAnimalFrequency() {
  const res = await fetch(`${BASE_URL}/analytics/animal-frequency`);
  const data = await res.json();

  new Chart(document.getElementById("animalChart"), {
    type: "bar",
    data: {
      labels: Object.keys(data),
      datasets: [
        {
          label: "Detections",
          data: Object.values(data),
          backgroundColor: [
            "#1abc9c", // Cow
            "#3498db", // Deer
            "#9b59b6", // Elephant
            "#e74c3c", // Human
            "#f39c12", // Wild_boar
          ],
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              const animal = context.label;
              const value = context.raw;

              return `${animal} detected ${value} times`;
            },
            afterLabel: function (context) {
              return "Higher value indicates frequent intrusion risk.";
            },
          },
        },
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Animal Type",
            color: "white",
          },
          ticks: { color: "white" },
        },
        y: {
          title: {
            display: true,
            text: "Detection Count",
            color: "white",
          },
          ticks: { color: "white" },
        },
      },
    },
  });
}

async function loadTimePattern() {
  const res = await fetch(`${BASE_URL}/analytics/time-pattern`);
  const data = await res.json();

  console.log("Time Pattern Data:", data);

  let labels = [];
  let values = [];

  // If backend returns array
  if (Array.isArray(data)) {
    labels = data.map((item) => item.hour);
    values = data.map((item) => item.count);
  }
  // If backend returns object
  else {
    labels = data.hours || [];
    values = data.counts || [];
  }

  const ctx = document.getElementById("timeChart");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Detections",
          data: values,
          borderColor: "#3498db",
          backgroundColor: "rgba(52,152,219,0.2)",
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              return `Detections at ${context.label}: ${context.raw}`;
            },
          },
        },
      },
      scales: {
        x: {
          title: { display: true, text: "Hour of Day" },
        },
        y: {
          title: { display: true, text: "Number of Detections" },
        },
      },
    },
  });
}

async function loadRiskTrend() {
  try {
    const res = await fetch(`${BASE_URL}/analytics/risk-trend`);
    const data = await res.json();

    if (!data.timestamps || !data.risk_scores) {
      console.log("Invalid risk trend format:", data);
      return;
    }

    const ctx = document.getElementById("riskChart").getContext("2d");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: data.timestamps.map((t) => t.slice(11, 16)),
        datasets: [
          {
            label: "Average Risk",
            data: data.risk_scores,
            borderColor: "#f39c12",
            backgroundColor: "rgba(243,156,18,0.2)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: "index",
          intersect: false,
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                const value = context.raw;

                let riskLevel = "Low";

                if (value >= 80) riskLevel = "Critical";
                else if (value >= 60) riskLevel = "High";
                else if (value >= 40) riskLevel = "Moderate";

                return `Avg Risk: ${value} (${riskLevel})`;
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Time (30-minute Interval)",
              color: "white",
            },
            ticks: {
              color: "white",
            },
          },
          y: {
            title: {
              display: true,
              text: "Average Risk Score",
              color: "white",
            },
            ticks: {
              color: "white",
            },
          },
        },
        plugins: {
          legend: {
            labels: {
              color: "white",
            },
          },
        },
      },
    });
  } catch (error) {
    console.error("Risk Trend Error:", error);
  }
}

async function loadZoneVulnerability() {
  try {
    const res = await fetch(`${BASE_URL}/analytics/zone-vulnerability`);
    const data = await res.json();

    console.log("Zone API Response:", data);

    // Since backend returns object
    const labels = Object.keys(data);
    const values = Object.values(data);

    const ctx = document.getElementById("zoneChart").getContext("2d");

    if (window.zoneChartInstance) {
      window.zoneChartInstance.destroy();
    }

    window.zoneChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Total Risk Incidents",
            data: values,
            backgroundColor: ["#e74c3c", "#f39c12", "#3498db"],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: function (context) {
                const zone = context.label;
                const value = context.raw;

                return `${zone} has ${value} high-risk incidents`;
              },
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Zone",
              color: "white",
            },
            ticks: { color: "white" },
          },
          y: {
            title: {
              display: true,
              text: "Total Risk Incidents",
              color: "white",
            },
            ticks: { color: "white" },
          },
        },
        plugins: {
          legend: {
            labels: { color: "white" },
          },
        },
      },
    });
  } catch (error) {
    console.error("Zone Vulnerability Error:", error);
  }
}

async function loadPrediction() {
  const res = await fetch(`${BASE_URL}/analytics/prediction`);
  const data = await res.json();

  document.getElementById("predictionText").innerText = data.prediction;
}

async function loadModelAccuracy() {
  const res = await fetch(`${BASE_URL}/feedback/accuracy`);
  const data = await res.json();

  document.getElementById("accuracyText").innerText = data.accuracy + "%";
}

function showReport() {
  hideAllSections();
  document.getElementById("reportSection").style.display = "block";
  loadMonthlyReport();
}

let monthlyReportData = [];

async function loadMonthlyReport() {
  const res = await fetch(`${BASE_URL}/analytics/monthly-report`);
  const data = await res.json();

  monthlyReportData = data;

  const container = document.getElementById("reportContainer");
  container.innerHTML = "";

  data.forEach((report) => {
    container.innerHTML += `
      <div class="report-card">

        <div class="report-top">
          <h3>${report.month}</h3>
        </div>

        <div class="kpi-grid">

          <div class="kpi-box total">
            <span class="kpi-number" data-value="${report.total_incidents}">0</span>
            <p>Total Incidents</p>
          </div>

          <div class="kpi-box critical">
            <span class="kpi-number" data-value="${report.critical_cases}">0</span>
            <p>Critical Cases</p>
          </div>

          <div class="kpi-box high">
            <span class="kpi-number" data-value="${report.high_cases}">0</span>
            <p>High Cases</p>
          </div>

          <div class="kpi-box avg">
            <span>${report.average_risk}</span>
            <p>Average Risk</p>
          </div>

        </div>

        <canvas id="miniChart-${report.month}" height="80"></canvas>

        <div class="summary">
          ${generateSummary(report)}
        </div>

      </div>
    `;

    // Create mini chart
    new Chart(document.getElementById(`miniChart-${report.month}`), {
      type: "bar",
      data: {
        labels: report.zone_distribution.map((z) => z.zone),
        datasets: [
          {
            data: report.zone_distribution.map((z) => z.count),
            backgroundColor: "#3498db",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { display: false }, y: { display: false } },
      },
    });
  });

  // Animate numbers
  document.querySelectorAll(".kpi-number").forEach((el) => {
    const value = parseInt(el.dataset.value);
    animateValue(el, 0, value);
  });
}

function downloadCSV() {
  if (!monthlyReportData.length) return;

  let csv = "Month,Total Incidents,Critical Cases,High Cases,Average Risk\n";

  monthlyReportData.forEach((r) => {
    csv += `${r.month},${r.total_incidents},${r.critical_cases},${r.high_cases},${r.average_risk}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "Monthly_Report.csv";
  a.click();

  window.URL.revokeObjectURL(url);
}

let currentIncidentId = null;
let feedbackCorrect = null;

function openFeedbackModal(id, animal) {
  currentIncidentId = id;
  feedbackCorrect = null;

  document.getElementById("feedbackAnimal").innerText =
    "Animal Detected: " + animal;

  document.getElementById("feedbackModal").style.display = "flex";
}

function closeFeedbackModal() {
  document.getElementById("feedbackModal").style.display = "none";
}

function selectFeedback(value) {
  feedbackCorrect = value;

  document.getElementById("yesBtn").classList.remove("selected");
  document.getElementById("noBtn").classList.remove("selected");

  if (value) {
    document.getElementById("yesBtn").classList.add("selected");
  } else {
    document.getElementById("noBtn").classList.add("selected");
  }
}

async function submitFeedback() {
  if (feedbackCorrect === null) {
    alert("Please select Yes or No");
    return;
  }

  const comment = document.getElementById("feedbackComment").value;

  const aiAnimal = document
    .getElementById("feedbackAnimal")
    .innerText.replace("Animal Detected: ", "")
    .trim();

  const payload = {
    incident_id: currentIncidentId,
    ai_animal_type: aiAnimal,
    corrected_animal_type: feedbackCorrect ? aiAnimal : "Wrong",
    feedback_type: "User Review",
    reviewer_name: "Karthick",
    comment: comment,
  };

  const res = await fetch(`${BASE_URL}/feedback/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const result = await res.json();
  console.log("Feedback response:", result);

  closeFeedbackModal();
  loadFeedbackHistory();
}

function animateValue(element, start, end, duration = 1000) {
  let startTime = null;

  function step(timestamp) {
    if (!startTime) startTime = timestamp;

    const progress = timestamp - startTime;
    const value = Math.min(start + (end - start) * (progress / duration), end);

    element.innerText = Math.floor(value);

    if (progress < duration) {
      window.requestAnimationFrame(step);
    }
  }

  window.requestAnimationFrame(step);
}

function generateSummary(report) {
  let severity = "moderate";

  if (report.average_risk >= 70) severity = "high";
  if (report.average_risk >= 85) severity = "critical";

  return `
  <p>
  This month recorded <b>${report.total_incidents}</b> incidents.
  Risk level remained <b>${severity}</b> with
  <b>${report.critical_cases}</b> critical alerts.
  Increased monitoring recommended in high activity zones.
  </p>
  `;
}

function showFeedback() {
  hideAllSections();
  document.getElementById("feedbackSection").style.display = "block";
  loadFeedbackHistory();
}

async function loadFeedbackHistory() {
  const res = await fetch(`${BASE_URL}/feedback/`);
  const data = await res.json();

  const tbody = document.getElementById("feedbackTableBody");
  tbody.innerHTML = "";

  data.forEach((f) => {
    // Determine Correct or Not
    const isCorrect =
      f.ai_animal_type.toLowerCase().trim() ===
      f.corrected_animal_type.toLowerCase().trim()
        ? "Yes"
        : "No";

    tbody.innerHTML += `
      <tr>
        <td>${f.id}</td>
        <td>${f.ai_animal_type || "-"}</td>
        <td>${isCorrect}</td>
        <td>${f.comment || "-"}</td>
        <td>${f.reviewed_at || "-"}</td>
      </tr>
    `;
  });
}

function showDetectionSummary(data) {
  const resultBox = document.getElementById("detectionResult");
  const listDiv = document.getElementById("detectionList");
  const riskDecision = document.getElementById("riskDecision");
  const alertStatus = document.getElementById("alertStatus");

  listDiv.innerHTML = "";

  if (!data.decision || data.decision.length === 0) {
    listDiv.innerHTML = "<p>No animals detected.</p>";
    resultBox.style.display = "block";
    return;
  }

  // Loop through detected decisions
  data.decision.forEach((item) => {
    listDiv.innerHTML += `
      <div class="detection-item">
        <p><strong>Animal:</strong> ${item.animal_type}</p>
        <p><strong>Zone:</strong> ${item.zone}</p>
        <p><strong>Time:</strong> ${item.timestamp || "-"}</p>
        <p><strong>Risk Score:</strong> ${item.risk_score ?? "-"}</p>
        <p><strong>Alert Level:</strong> ${item.alert_level || "-"}</p>
      </div>
      <hr/>
    `;
  });

  // Use highest alert level for display
  const mainAlert = data.decision?.[0]?.alert_level || "LOW";

  riskDecision.innerText = mainAlert;

  alertStatus.innerText =
    data.decision?.[0]?.requires_immediate_action === true ? "YES 🚨" : "NO";

  // Color coding risk level
  riskDecision.style.color =
    mainAlert === "CRITICAL"
      ? "red"
      : mainAlert === "HIGH"
        ? "orange"
        : mainAlert === "MEDIUM"
          ? "yellow"
          : "lightgreen";

  resultBox.style.display = "block";
}

async function loadIncidentSummary() {
  try {
    const res = await fetch(`${BASE_URL}/operations/incident-summary`);
    const data = await res.json();

    document.getElementById("totalIncidents").innerText = data.total;
    document.getElementById("activeIncidents").innerText = data.active;
    document.getElementById("resolvedIncidents").innerText = data.resolved;
  } catch (error) {
    console.error("Incident summary error:", error);
  }
}

const greenIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
  iconSize: [32, 32],
});

const yellowIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
  iconSize: [32, 32],
});

const redIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
  iconSize: [32, 32],
});

const blackIcon = new L.Icon({
  iconUrl: "https://maps.google.com/mapfiles/ms/icons/purple-dot.png",
  iconSize: [32, 32],
});

function getAlertIcon(level) {
  if (level === "LOW") return greenIcon;

  if (level === "MEDIUM") return yellowIcon;

  if (level === "HIGH") return redIcon;

  if (level === "CRITICAL") return blackIcon;

  return greenIcon;
}

let wildlifeMap;

function loadMap() {
  wildlifeMap = L.map("wildlifeMap").setView([10.046381, 79.079616], 10);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap",
  }).addTo(wildlifeMap);
}

async function loadDetectionMap() {
  try {
    const res = await fetch(`${BASE_URL}/operations/incidents`);
    const data = await res.json();

    data.forEach((d) => {
      if (d.latitude && d.longitude) {
        const icon = getAlertIcon(d.alert_level);

        L.marker([d.latitude, d.longitude], { icon: icon })
          .addTo(wildlifeMap)
          .bindPopup(
            `<b>${d.animal_type}</b><br>
         Zone: ${d.zone}<br>
         Camera: ${d.camera_id}<br>
         Alert: ${d.alert_level}`,
          );
      }
    });
  } catch (err) {
    console.error("Map Load Error", err);
  }
}
