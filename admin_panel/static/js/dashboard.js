document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("salesChart");
  if (!canvas || typeof window.salesChartData === "undefined") return;

  const data = window.salesChartData || [];
  if (!data.length) return;

  const ctx = canvas.getContext("2d");
  const width = canvas.parentElement.clientWidth - 16;
  const height = 240;
  canvas.width = width * 2;
  canvas.height = height * 2;
  canvas.style.width = width + "px";
  canvas.style.height = height + "px";
  ctx.scale(2, 2);

  const values = data.map((d) => Number(d.value) || 0);
  const labels = data.map((d) => d.label || "");
  const max = Math.max(...values, 1);
  const padding = { top: 20, right: 16, bottom: 36, left: 40 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;
  const barW = Math.max(10, chartW / values.length - 12);

  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#e7e5e4";
  ctx.fillStyle = "#78716c";
  ctx.font = "12px Segoe UI, sans-serif";

  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartH / 4) * i;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(width - padding.right, y);
    ctx.stroke();
    const val = Math.round(max - (max / 4) * i);
    ctx.fillText(String(val), 8, y + 4);
  }

  values.forEach((v, i) => {
    const x = padding.left + i * (chartW / values.length) + 6;
    const h = (v / max) * chartH;
    const y = padding.top + chartH - h;
    ctx.fillStyle = "#b54a2e";
    ctx.beginPath();
    ctx.roundRect(x, y, barW, h, 6);
    ctx.fill();
    ctx.fillStyle = "#78716c";
    const label = String(labels[i]).slice(5) || String(labels[i]);
    ctx.fillText(label, x, height - 12);
  });
});
