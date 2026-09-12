document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".login-card form");
  if (!form) return;
  form.addEventListener("submit", () => {
    const btn = form.querySelector("button[type='submit']");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Signing in...";
    }
  });
});
