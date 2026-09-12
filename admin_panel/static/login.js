document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector("[data-password-toggle]");
  const password = document.querySelector("#password");

  if (!toggle || !password) return;

  toggle.addEventListener("click", () => {
    const hidden = password.type === "password";
    password.type = hidden ? "text" : "password";
    toggle.textContent = hidden ? "Hide" : "Show";
    toggle.setAttribute("aria-label", hidden ? "Hide password" : "Show password");
  });
});