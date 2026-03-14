"use strict";

const btnRecord = document.getElementById("record");
const btnStop = document.getElementById("stop");
const downloadLink = document.getElementById("download");

btnStop.disabled = true;

async function setRecordStatus(status) {
  const response = await fetch("/record_status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
  return response.json();
}

btnRecord.addEventListener("click", async () => {
  btnRecord.disabled = true;
  btnStop.disabled = false;
  downloadLink.textContent = "";
  downloadLink.href = "";

  await setRecordStatus("true");
});

btnStop.addEventListener("click", async () => {
  btnRecord.disabled = false;
  btnStop.disabled = true;

  await setRecordStatus("false");

  downloadLink.textContent = "Download Video";
  downloadLink.href = "/static/video.avi";
});
