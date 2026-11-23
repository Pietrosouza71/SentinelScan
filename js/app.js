    (() => {
      const sidebar = document.getElementById("sidebar");
      const overlay = document.getElementById("mobileOverlay");
      const menuToggle = document.getElementById("menuToggle");
      const toast = document.getElementById("toast");
      const toastMessage = document.getElementById("toastMessage");
      const breadcrumb = document.getElementById("breadcrumbCurrent");
      const pageTitle = document.getElementById("pageTitle");
      let toastTimer;

      const showToast = (message, title = "Demonstração") => {
        document.getElementById("toastTitle").textContent = title;
        toastMessage.textContent = message;
        toast.classList.add("show");
        window.clearTimeout(toastTimer);
        toastTimer = window.setTimeout(() => toast.classList.remove("show"), 4200);
      };

      const closeMenu = () => {
        sidebar.classList.remove("open");
        overlay.classList.remove("visible");
        menuToggle.setAttribute("aria-expanded", "false");
      };

      menuToggle.addEventListener("click", () => {
        const isOpen = sidebar.classList.toggle("open");
        overlay.classList.toggle("visible", isOpen);
        menuToggle.setAttribute("aria-expanded", String(isOpen));
      });
      overlay.addEventListener("click", closeMenu);

      document.querySelectorAll(".nav-link").forEach((link) => {
        link.addEventListener("click", () => {
          document.querySelectorAll(".nav-link").forEach((item) => {
            item.classList.remove("active");
            item.removeAttribute("aria-current");
          });
          link.classList.add("active");
          link.setAttribute("aria-current", "page");
          const page = link.dataset.page;
          breadcrumb.textContent = page;
          if (page !== "Painel") {
            pageTitle.textContent = page;
            showToast("Prévia de um fluxo Red Team autorizado. A funcionalidade real será conectada ao backend nas próximas etapas.");
          } else {
            pageTitle.textContent = "Painel de operações";
          }
          closeMenu();
        });
      });

      document.querySelectorAll("[data-page-link]").forEach((button) => {
        button.addEventListener("click", () => {
          const target = document.querySelector(`.nav-link[data-page="${button.dataset.pageLink}"]`);
          if (target) target.click();
        });
      });

      document.querySelectorAll("[data-toast]").forEach((button) => {
        button.addEventListener("click", () => showToast(button.dataset.toast));
      });

      document.getElementById("newScanButton").addEventListener("click", () => {
        showToast("Esta demonstração não inicia engajamentos. A execução real exigirá autorização registrada, escopo definido e regras de engajamento.", "Engajamento não iniciado");
      });

      document.querySelector(".period-select").addEventListener("change", (event) => {
        showToast(`Período "${event.target.value}" selecionado. Os dados do gráfico são ilustrativos.`);
      });

      const date = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric" })
        .format(new Date()).replace(/\./g, "").toUpperCase();
      document.getElementById("currentDate").textContent = date;
    })();
