document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("#sidebar");
  const overlay = document.querySelector("[data-sidebar-overlay]");
  const openBtn = document.querySelector("[data-open-sidebar]");
  const toast = document.querySelector("#toast");

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    window.setTimeout(() => toast.classList.remove("show"), 2200);
  };

  if (openBtn && sidebar) {
    openBtn.addEventListener("click", () => {
      sidebar.classList.add("open");
      if (overlay) overlay.classList.add("show");
    });
  }

  if (overlay && sidebar) {
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("show");
    });
  }

  document.querySelectorAll("[data-open-modal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-open-modal");
      const modal = document.getElementById(id);
      if (!modal) return;
      if (id === "edit-product") {
        const form = modal.querySelector("form");
        if (form) {
          const idInput = form.querySelector("#edit-product-id");
          const nameInput = form.querySelector("#edit-product-name");
          const priceInput = form.querySelector("#edit-product-price");
          const qtyInput = form.querySelector("#edit-product-quantity");
          const currentImageInput = form.querySelector("#edit-product-current-image");
          const currentImageHint = form.querySelector("#edit-product-image-current");
          const infoInput = form.querySelector("#edit-product-information");
          const currentImage = btn.getAttribute("data-image") || "";
          if (idInput) idInput.value = btn.getAttribute("data-id") || "";
          if (nameInput) nameInput.value = btn.getAttribute("data-name") || "";
          if (priceInput) priceInput.value = btn.getAttribute("data-price") || "";
          if (qtyInput) qtyInput.value = btn.getAttribute("data-quantity") || "";
          if (infoInput) infoInput.value = btn.getAttribute("data-information") || "";
          // A file input can't be pre-filled by JS, so we keep the current
          // filename in a hidden field and only replace it if the admin
          // actually picks a new file.
          if (currentImageInput) currentImageInput.value = currentImage;
          if (currentImageHint) {
            currentImageHint.textContent = currentImage
              ? `Current image: ${currentImage}`
              : "No image set yet.";
          }
        }
      }
      modal.hidden = false;
    });
  });

  document.querySelectorAll("[data-close-modal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const modal = btn.closest(".modal");
      if (modal) modal.hidden = true;
    });
  });

  document.querySelectorAll(".modal").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.hidden = true;
    });
  });

  const highlight = new URLSearchParams(window.location.search).get("highlight");
  if (highlight) {
    const row = document.querySelector(`[data-highlight-id="${highlight}"]`);
    if (row) {
      row.classList.add("is-highlight");
      row.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  window.showToast = showToast;
});