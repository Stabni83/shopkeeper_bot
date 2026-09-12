document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("#sidebar");
  const overlay = document.querySelector("[data-sidebar-overlay]");
  const toast = document.querySelector("#toast");

  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("show");
    clearTimeout(window.__toastTimer);
    window.__toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
  };

  document.querySelectorAll("[data-sidebar-open]").forEach((btn) => {
    btn.addEventListener("click", () => {
      sidebar?.classList.add("open");
      overlay?.classList.add("show");
    });
  });

  document.querySelectorAll("[data-sidebar-close], [data-sidebar-overlay]").forEach((el) => {
    el.addEventListener("click", () => {
      sidebar?.classList.remove("open");
      overlay?.classList.remove("show");
    });
  });

  // Client-side filter for dashboard recent orders table only
  const orderSearch = document.querySelector("#orderSearch");
  const orderStatusFilter = document.querySelector("#orderStatusFilter");
  const ordersTable = document.querySelector("#ordersTable tbody");

  const filterOrdersTable = () => {
    if (!ordersTable) return;
    const q = (orderSearch?.value || "").toLowerCase().trim();
    const status = (orderStatusFilter?.value || "").toLowerCase();
    ordersTable.querySelectorAll("tr").forEach((row) => {
      if (row.querySelector(".empty-cell")) return;
      const text = row.textContent.toLowerCase();
      const rowStatus = (row.getAttribute("data-status") || "").toLowerCase();
      const matchText = !q || text.includes(q);
      const matchStatus = !status || rowStatus === status;
      row.style.display = matchText && matchStatus ? "" : "none";
    });
  };

  orderSearch?.addEventListener("input", filterOrdersTable);
  orderStatusFilter?.addEventListener("change", filterOrdersTable);

  // Modal open/close (products page)
  document.querySelectorAll("[data-open-modal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-open-modal");
      const modal = document.getElementById(id);
      if (!modal) return;
      if (id === "edit-product") {
        document.getElementById("edit-product-id").value = btn.getAttribute("data-id") || "";
        document.getElementById("edit-product-name").value = btn.getAttribute("data-name") || "";
        document.getElementById("edit-product-price").value = btn.getAttribute("data-price") || "";
        document.getElementById("edit-product-quantity").value = btn.getAttribute("data-quantity") || "";
        document.getElementById("edit-product-image").value = btn.getAttribute("data-image") || "";
        document.getElementById("edit-product-information").value = btn.getAttribute("data-information") || "";
      }
      modal.hidden = false;
    });
  });

  document.querySelectorAll("[data-close-modal]").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".modal").hidden = true;
    });
  });

  document.querySelectorAll(".modal").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.hidden = true;
    });
  });

  // Expose toast if needed later
  window.showToast = showToast;
});
