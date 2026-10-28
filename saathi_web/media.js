"use strict";
// Uses the existing same-origin session/CSRF helpers; no credentials persist in JS storage.
async function renderMedia() {
  const records = await api("/api/media"), list = $("#audio-list");
  list.replaceChildren();
  if (!records.length) list.append(node("p", "No audio stored in this local workspace."));
  for (const record of records) {
    const card = node("article");
    card.className = "audio-card";
    card.append(node("h4", record.state === "active" ? "Audio ready for local playback" : "Audio expired · playback unavailable"));
    if (record.duration_ms !== null) card.append(node("p", `${record.duration_ms / 1000} seconds · ${Math.ceil(record.bytes / 1024)}KB`));
    card.append(node("p", `Access expiry: ${new Date(record.expires_at).toLocaleString("en-IN", {timeZone:"Asia/Kolkata"})} IST`));
    if (record.state === "active") {
      const audio = node("audio");
      audio.controls = true;
      audio.preload = "none";
      audio.src = `/api/media/${record.id}/content`;
      audio.setAttribute("aria-label", "Play locally stored audio");
      card.append(audio);
    }
    card.append(button("Delete stored audio", async () => {
      await api(`/api/media/${record.id}`, {}, "DELETE");
      await renderMedia();
      $("#audio-status").textContent = "Stored audio deleted. No transcription or task was created.";
    }, "secondary", $("#refresh-audio")));
    list.append(card);
  }
}
$("#audio-form").addEventListener("submit", event => {
  event.preventDefault();
  run(async () => {
    const file = $("#review-audio").files[0];
    if (!file || file.size > 2000000 || !$("#audio-consent").checked) throw new Error("Choose a WAV up to2MB and confirm local-review permission.");
    const response = await fetch("/api/media", {method:"POST", headers:{"Content-Type":"audio/wav", "X-Saathi-CSRF":csrf, "X-Saathi-Media-Consent":"local-review"}, body:file});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error?.message || "Audio could not be stored.");
    $("#audio-form").reset();
    await renderMedia();
    $("#audio-status").textContent = "Stored for local playback only. Not transcribed or sent to a provider.";
  });
});
$("#refresh-audio").addEventListener("click", () => run(renderMedia));

// A resumed session can arrive before this deferred script finishes downloading.
function mediaSessionReady() {
  if (csrf) renderMedia().catch(error => { $("#audio-status").textContent = error.message; });
}
document.addEventListener("saathi-session-ready", mediaSessionReady);
mediaSessionReady();
