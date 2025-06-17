const ideaForm = document.getElementById("ideaForm");
const reportsDiv = document.getElementById("reports");
const chatForm = document.getElementById("chatForm");
const chatbox = document.getElementById("chatbox");
const clearChat = document.getElementById("clearChat");
const resetBtn = document.getElementById("resetBtn");
const ideaContainer = document.getElementById("ideaContainer");
const loadingOverlay = document.getElementById("loadingOverlay");
const chatToggle = document.getElementById("chatToggle");
const chatPanel = document.getElementById("chatPanel");
const topCountryEl = document.getElementById("topCountry");
const sectorListEl = document.getElementById("sectorList");
const darkToggle = document.getElementById("darkToggle");


let topCountries = [];
const countryNames = {
  "AGO": "Angola",
  "ARE": "United Arab Emirates",
  "ARG": "Argentina",
  "ARM": "Armenia",
  "AUS": "Australia",
  "AUT": "Austria",
  "AZE": "Azerbaijan",
  "BDI": "Burundi",
  "BEL": "Belgium",
  "BEN": "Benin",
  "BFA": "Burkina Faso",
  "BGD": "Bangladesh",
  "BGR": "Bulgaria",
  "BHR": "Bahrain",
  "BHS": "Bahamas",
  "BIH": "Bosnia and Herzegovina",
  "BLR": "Belarus",
  "BLZ": "Belize",
  "BOL": "Bolivia",
  "BRA": "Brazil",
  "BRN": "Brunei",
  "BTN": "Bhutan",
  "BWA": "Botswana",
  "CAF": "Central African Republic",
  "CAN": "Canada",
  "CHE": "Switzerland",
  "CHL": "Chile",
  "CHN": "China",
  "CMR": "Cameroon",
  "COG": "Republic of the Congo",
  "COL": "Colombia",
  "COM": "Comoros",
  "CRI": "Costa Rica",
  "CYP": "Cyprus",
  "CZE": "Czech Republic",
  "DEU": "Germany",
  "DJI": "Djibouti",
  "DNK": "Denmark",
  "DOM": "Dominican Republic",
  "DZA": "Algeria",
  "ECU": "Ecuador",
  "EGY": "Egypt",
  "ERI": "Eritrea",
  "ESP": "Spain",
  "EST": "Estonia",
  "ETH": "Ethiopia",
  "FIN": "Finland",
  "FJI": "Fiji",
  "FRA": "France",
  "FSM": "Micronesia",
  "GAB": "Gabon",
  "GBR": "United Kingdom",
  "GEO": "Georgia",
  "GHA": "Ghana",
  "GIN": "Guinea",
  "GMB": "Gambia",
  "GNB": "Guinea-Bissau",
  "GRC": "Greece",
  "GTM": "Guatemala",
  "GUY": "Guyana",
  "HKG": "Hong Kong",
  "HND": "Honduras",
  "HRV": "Croatia",
  "HUN": "Hungary",
  "IDN": "Indonesia",
  "IND": "India",
  "IRL": "Ireland",
  "IRN": "Iran",
  "IRQ": "Iraq",
  "ISL": "Iceland",
  "ISR": "Israel",
  "ITA": "Italy",
  "JAM": "Jamaica",
  "JOR": "Jordan",
  "JPN": "Japan",
  "KAZ": "Kazakhstan",
  "KEN": "Kenya",
  "KGZ": "Kyrgyzstan",
  "KHM": "Cambodia",
  "KIR": "Kiribati",
  "KOR": "South Korea",
  "KWT": "Kuwait",
  "LBN": "Lebanon",
  "LBR": "Liberia",
  "LBY": "Libya",
  "LCA": "Saint Lucia",
  "LKA": "Sri Lanka",
  "LSO": "Lesotho",
  "LTU": "Lithuania",
  "LUX": "Luxembourg",
  "LVA": "Latvia",
  "MAR": "Morocco",
  "MCO": "Monaco",
  "MDA": "Moldova",
  "MDG": "Madagascar",
  "MDV": "Maldives",
  "MEX": "Mexico",
  "MKD": "North Macedonia",
  "MLI": "Mali",
  "MLT": "Malta",
  "MMR": "Myanmar",
  "MNE": "Montenegro",  
  "MNG": "Mongolia",
  "MOZ": "Mozambique",
  "MRT": "Mauritania",
  "MUS": "Mauritius",
  "MWI": "Malawi",
  "MYS": "Malaysia",
  "NAM": "Namibia",
  "NGA": "Nigeria",
  "NIC": "Nicaragua",
  "NLD": "Netherlands",
  "NOR": "Norway",
  "NPL": "Nepal",
  "NZL": "New Zealand",
  "OMN": "Oman",
  "PAK": "Pakistan",
  "PAN": "Panama",
  "PER": "Peru",
  "PHL": "Philippines",
  "PLW": "Palau",
  "PNG": "Papua New Guinea",
  "POL": "Poland",
  "PRT": "Portugal",
  "PRY": "Paraguay",
  "QAT": "Qatar",
  "ROU": "Romania", 
  "RUS": "Russia",
  "RWA": "Rwanda",
  "SAU": "Saudi Arabia",
  "SUD": "Sudan",
  "SEN": "Senegal",
  "SGP": "Singapore",
  "SLB": "Solomon Islands",
  "SLE": "Sierra Leone",
  "SLV": "El Salvador",
  "SMR": "San Marino",
  "SOM": "Somalia",
  "SRB": "Serbia", 
  "SSD": "South Sudan",
  "SUR": "Suriname",
  "SVK": "Slovakia",
  "SVN": "Slovenia",
  "SWE": "Sweden",
  "SWZ": "Eswatini",
  "SYC": "Seychelles",
  "SYR": "Syria",
  "TCD": "Chad",
  "TGO": "Togo",
  "THA": "Thailand",
  "TJK": "Tajikistan",
  "TKM": "Turkmenistan",
  "TON": "Tonga",
  "TTO": "Trinidad and Tobago",
  "TUN": "Tunisia",
  "TUR": "Turkey",
  "TUV": "Tuvalu",
  "TZA": "Tanzania",
  "UGA": "Uganda",
  "UKR": "Ukraine",
  "URY": "Uruguay",
  "USA": "United States",
  "UZB": "Uzbekistan",
  "VEN": "Venezuela",
  "VNM": "Vietnam",
  "VUT": "Vanuatu",
  "WSM": "Samoa",
  "YEM": "Yemen",
  "ZAF": "South Africa",
  "ZMB": "Zambia",
  "ZWE": "Zimbabwe"
};

// Restore topCountries and sectors if returning from report page
if (sessionStorage.getItem("topCountries")) {
  topCountries = JSON.parse(sessionStorage.getItem("topCountries"));
  const storedSectors = JSON.parse(sessionStorage.getItem("detectedSectors"));
  if (topCountries.length && topCountryEl) {
    const topCode = topCountries[0];
    topCountryEl.innerText = countryNames[topCode] || topCode;
  }
  if (storedSectors && sectorListEl) {
    sectorListEl.innerText = storedSectors.length ? storedSectors.join(", ") : "None";
  }
}

if (localStorage.theme === 'dark') document.documentElement.classList.add('dark');
darkToggle.onclick = () => {
  document.documentElement.classList.toggle('dark');
  localStorage.theme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
};

if (sessionStorage.getItem("backFromReport") === "1") {
  sessionStorage.removeItem("backFromReport");
  ideaContainer.style.display = "none";
  resetBtn.style.display = "inline-block";
  fetch("/get_reports")
    .then(res => res.json())
    .then(data => renderReports(data));
}

ideaForm.onsubmit = async (e) => {
  e.preventDefault();
  const file = document.getElementById("pdfUpload").files[0];
  let ideaText = document.getElementById("ideaText").value.trim();
  let sectors = [];

  ideaContainer.style.display = "none";
  loadingOverlay.classList.remove("hidden");

  if (file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/upload_pdf", { method: "POST", body: formData });
    const data = await res.json();
    ideaText = data.text;
    sectors = data.sectors;
    document.getElementById("ideaText").value = ideaText;
  }

  const submitForm = new FormData();
  submitForm.append("text", ideaText);
  const submitRes = await fetch("/submit_text", { method: "POST", body: submitForm });
  const submitData = await submitRes.json();
  if (!sectors.length) sectors = submitData.sectors;
  if (sectorListEl) {
    sectorListEl.innerText = sectors.length ? sectors.join(", ") : "None";
  }

  const runForm = new FormData();
  runForm.append("idea", ideaText);
  try {
    const runRes = await fetch("/run_pipeline", { method: "POST", body: runForm });
    if (!runRes.ok) throw new Error(`Pipeline error: ${runRes.status} ${runRes.statusText}`);

    const runData = await runRes.json();
    topCountries = runData.top_countries;
    sessionStorage.setItem("topCountries", JSON.stringify(topCountries));
    sessionStorage.setItem("detectedSectors", JSON.stringify(sectors));
  } catch (err) {
    console.error("❌ Error during run_pipeline:", err);
    alert("Something went wrong while generating the country shortlist. Please try again.");
    loadingOverlay.classList.add("hidden");
    ideaContainer.style.display = "block";
    return;
  }

  try {
    const reportRes = await fetch("/get_reports");
    if (!reportRes.ok) throw new Error(`Fetch failed: ${reportRes.statusText}`);

    const reportData = await reportRes.json();
    console.log("📦 Reports received:", reportData);

    if (!Array.isArray(reportData) || reportData.length === 0) {
      throw new Error("No reports received or invalid format.");
    }

    renderReports(reportData);
    loadingOverlay.classList.add("hidden");
    resetBtn.style.display = "inline-block";

    if (topCountries.length && topCountryEl) {
      const topCode = topCountries[0];
      topCountryEl.innerText = countryNames[topCode] || topCode;
    }
  } catch (err) {
    console.error("❌ Error in report fetch/render:", err);
    loadingOverlay.classList.add("hidden");
    alert("Failed to load reports. Check console for more info.");
  }
};

function renderReports(reports) {
  reportsDiv.innerHTML = "";
  if (!Array.isArray(reports) || !reports.length) {
    reportsDiv.innerHTML = "<p class='text-red-500'>No reports found or invalid format.</p>";
    return;
  }

  reports.forEach((report, idx) => {
    const countryCode = report.country_code || `C${idx + 1}`;
    const countryFullName = countryNames[countryCode] || countryCode;

    const card = document.createElement("div");
    card.className = "card bg-white dark:bg-gray-700 p-4 rounded-lg shadow";

    card.innerHTML = `
      <h3 class="text-xl font-bold">${idx + 1}. ${countryFullName} <span class="text-sm text-gray-500">(${countryCode})</span></h3>
      <a onclick="sessionStorage.setItem('navigatingToReport', '1');" href="/report.html?country=${countryCode}" class="mt-2 inline-block text-indigo-600 dark:text-indigo-300 hover:underline">View Full Report</a>
    `;
    reportsDiv.appendChild(card);
  });

  const refreshBtnContainer = document.createElement("div");
  refreshBtnContainer.className = "flex justify-center mt-4";
  refreshBtnContainer.innerHTML = `
    <button class="refresh-btn bg-red-600 text-white text-sm font-semibold py-2 px-4 rounded-lg hover:bg-red-700" onclick="resetAndRefresh()">Start New Idea</button>
  `;
  reportsDiv.appendChild(refreshBtnContainer);
}

async function resetAndRefresh() {
  await fetch("/reset", { method: "POST" });
  sessionStorage.removeItem("hasActiveReports");
  sessionStorage.removeItem("topCountries");
  sessionStorage.removeItem("detectedSectors");
  window.location.reload();
}

chatToggle.onclick = () => {
  chatPanel.classList.toggle("hidden");
};

chatForm.onsubmit = async (e) => {
  e.preventDefault();
  const input = document.getElementById("userInput");
  const msg = input.value.trim();
  if (!msg) return;
  addMessage(msg, true);
  input.value = "";
  const chatFormData = new FormData();
  chatFormData.append("question", msg);
  topCountries.forEach(code => chatFormData.append("top_countries", code));
  const res = await fetch("/chat", { method: "POST", body: chatFormData });
  const data = await res.json();
  addMessage(data.response, false);
};

function addMessage(text, isUser) {
  const message = document.createElement("div");
  message.textContent = text;
  message.className = `p-3 rounded-lg w-fit max-w-[80%] break-words ${
    isUser ? "bg-gray-200 dark:bg-gray-600 self-start" : "bg-emerald-600 text-white self-end"
  }`;
  chatbox.appendChild(message);
  chatbox.scrollTop = chatbox.scrollHeight;
}

resetBtn.onclick = async () => {
  await fetch("/reset", { method: "POST" });
  reportsDiv.innerHTML = "";
  chatbox.innerHTML = "";
  document.getElementById("ideaText").value = "";
  ideaContainer.style.display = "block";
  resetBtn.style.display = "none";
  topCountryEl.innerText = "N/A";
  sectorListEl.innerText = "None";
};

document.getElementById("reportSearch")?.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  const reports = document.querySelectorAll("#reports > div");
  reports.forEach(report => {
    report.style.display = report.textContent.toLowerCase().includes(query) ? "block" : "none";
  });
});

window.addEventListener("pagehide", async function (event) {
  if (sessionStorage.getItem("navigatingToReport") === "1") return;
  if (event.persisted) return;
  await fetch("/reset", { method: "POST" });
  sessionStorage.removeItem("hasActiveReports");
  sessionStorage.removeItem("topCountries");
  sessionStorage.removeItem("detectedSectors");
});

ideaForm.addEventListener("submit", () => {
  sessionStorage.setItem("hasActiveReports", "true");
});

setTimeout(() => {
  if (sessionStorage.getItem("hasActiveReports") === "true") {
    fetch("/reset", { method: "POST" });
    sessionStorage.removeItem("hasActiveReports");
  }
}, 15 * 60 * 1000);

resetBtn.addEventListener("click", () => {
  fetch("/reset", { method: "POST" });
  sessionStorage.removeItem("hasActiveReports");
});
