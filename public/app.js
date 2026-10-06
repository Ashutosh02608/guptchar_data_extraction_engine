// Guptchar Client Engine | Core Architecture: Ashutosh
console.log("%c[Guptchar Engine v1.0] Core Intelligence Active | Lead Architect: Ashutosh", "color: #38bdf8; font-weight: bold;");
let currentExtractedData = [];

function applyPreset(country, city, sector) {
  document.getElementById("country").value = country;
  document.getElementById("city").value = city;
  document.getElementById("sector_keyword").value = sector;
}

function updateStage(stageId, state) {
  const el = document.getElementById(stageId);
  const ind = el.querySelector(".stage-indicator");
  el.classList.remove("active", "completed");

  if (state === "active") {
    el.classList.add("active");
    ind.textContent = "IN PROGRESS";
  } else if (state === "completed") {
    el.classList.add("completed");
    ind.textContent = "COMPLETED";
  } else {
    ind.textContent = "STANDBY";
  }
}

document.getElementById("extract-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const submitBtn = document.getElementById("submit-btn");
  const btnText = submitBtn.querySelector(".btn-text");
  const spinner = submitBtn.querySelector(".btn-spinner");

  // Input values
  const country = document.getElementById("country").value.trim();
  const city = document.getElementById("city").value.trim();
  const sector_keyword = document.getElementById("sector_keyword").value.trim();
  const limit = parseInt(document.getElementById("limit").value, 10) || 3;
  const export_json = document.getElementById("export_json").checked;
  const export_pdf = document.getElementById("export_pdf").checked;

  // Set loading state
  submitBtn.disabled = true;
  btnText.textContent = "Extracting Intelligence...";
  spinner.style.display = "inline-block";

  // Reset stages
  updateStage("stage-a-status", "active");
  updateStage("stage-b-status", "standby");
  updateStage("stage-c-status", "standby");

  // Realistic UI progression timer
  const t1 = setTimeout(() => {
    updateStage("stage-a-status", "completed");
    updateStage("stage-b-status", "active");
  }, 4000);

  const t2 = setTimeout(() => {
    updateStage("stage-b-status", "completed");
    updateStage("stage-c-status", "active");
  }, 9000);

  try {
    const response = await fetch("/api/v1/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        country,
        city,
        sector_keyword,
        limit,
        export_json,
        export_pdf,
      }),
    });

    clearTimeout(t1);
    clearTimeout(t2);

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Server extraction failed.");
    }

    const data = await response.json();
    currentExtractedData = data.leads || [];

    // Complete all stages
    updateStage("stage-a-status", "completed");
    updateStage("stage-b-status", "completed");
    updateStage("stage-c-status", "completed");

    // Render results
    renderResults(data);
  } catch (error) {
    alert("Extraction error: " + error.message);
    updateStage("stage-a-status", "standby");
    updateStage("stage-b-status", "standby");
    updateStage("stage-c-status", "standby");
  } finally {
    submitBtn.disabled = false;
    btnText.textContent = "Execute Extraction Pipeline";
    spinner.style.display = "none";
  }
});

function renderResults(data) {
  const container = document.getElementById("results-container");
  const headline = document.getElementById("results-headline");
  const submeta = document.getElementById("results-submeta");
  const cardsList = document.getElementById("leads-cards-list");
  const jsonViewer = document.getElementById("json-code-viewer");

  const jsonBtn = document.getElementById("download-json-btn");
  const pdfBtn = document.getElementById("download-pdf-btn");

  container.style.display = "flex";
  headline.textContent = `Extracted Intelligence: ${data.sector_keyword} in ${data.city}`;
  submeta.textContent = `Entities resolved: ${data.total_leads} | Execution duration: ${data.elapsed_seconds}s`;

  // Download buttons
  if (data.json_download) {
    jsonBtn.href = data.json_download;
    jsonBtn.style.display = "inline-flex";
  } else {
    jsonBtn.style.display = "none";
  }

  if (data.pdf_download) {
    pdfBtn.href = data.pdf_download;
    pdfBtn.style.display = "inline-flex";
  } else {
    pdfBtn.style.display = "none";
  }

  // Cards
  cardsList.innerHTML = "";
  (data.leads || []).forEach((lead, idx) => {
    const card = document.createElement("div");
    card.className = "lead-card glass-panel";

    let execRows = "";
    if (lead.executives_and_contacts && lead.executives_and_contacts.length > 0) {
      execRows = lead.executives_and_contacts
        .map((ex) => {
          const isSec = (ex.source || "").toLowerCase().includes("sec");
          const badgeClass = isSec ? "source-sec" : "source-web";
          return `
            <tr>
              <td><strong>${escapeHtml(ex.name)}</strong></td>
              <td>${escapeHtml(ex.title)}</td>
              <td>${escapeHtml(ex.phone)}</td>
              <td>${escapeHtml(ex.email)}</td>
              <td><span class="source-badge ${badgeClass}">${escapeHtml(ex.source)}</span></td>
            </tr>
          `;
        })
        .join("");
    } else {
      execRows = `<tr><td colspan="5" style="text-align: center; color: var(--text-dim);">No executive contacts indexed</td></tr>`;
    }

    card.innerHTML = `
      <div class="lead-card-header">
        <div class="lead-title-area">
          <h3>#${idx + 1}. ${escapeHtml(lead.company_name)}</h3>
        </div>
      </div>

      <div class="lead-summary-box">
        "${escapeHtml(lead.one_sentence_description)}"
      </div>

      <div class="lead-meta-grid">
        <div class="meta-item">
          <span class="meta-label">Gatekeeper Phone</span>
          <span class="meta-value">${escapeHtml(lead.generic_contact_number)}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Primary Email</span>
          <span class="meta-value">${escapeHtml(lead.primary_email)}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Official Website</span>
          <span class="meta-value">
            ${
              lead.website && lead.website !== "N/A"
                ? `<a href="${escapeHtml(lead.website)}" target="_blank">${escapeHtml(lead.website)}</a>`
                : "N/A"
            }
          </span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Physical Address</span>
          <span class="meta-value">${escapeHtml(lead.address)}</span>
        </div>
      </div>

      <div class="exec-table-wrap">
        <table class="exec-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Role / Title</th>
              <th>Phone</th>
              <th>Email</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            ${execRows}
          </tbody>
        </table>
      </div>
    `;
    cardsList.appendChild(card);
  });

  // JSON Preview
  jsonViewer.textContent = JSON.stringify(data.leads || [], null, 2);

  // Scroll to results smoothly
  container.scrollIntoView({ behavior: "smooth" });
}

function copyJsonOutput() {
  const jsonStr = JSON.stringify(currentExtractedData, null, 2);
  navigator.clipboard.writeText(jsonStr).then(() => {
    alert("Standardized JSON Schema copied to clipboard!");
  });
}

function escapeHtml(str) {
  if (!str) return "N/A";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
