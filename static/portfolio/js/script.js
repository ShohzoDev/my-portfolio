/* ==========================================================================
   Shohzod — portfolio interactions.

   Everything here is progressive enhancement: the server renders the full
   page in the right language (/uz/, /ru/, /en/), the contact form posts
   normally, language links are plain links. This script only adds polish:
   reveal animations, scrollspy, mobile menu, copy-email, AJAX form submit
   and the ⌘K command palette.
   ========================================================================== */
(() => {
  "use strict";

  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scrollBehavior = prefersReducedMotion ? "auto" : "smooth";

  /* ---------------------------------------------------------------- toast */

  let toastTimer = null;
  function toast(text) {
    let el = document.getElementById("toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "toast";
      el.className = "toast";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      document.body.appendChild(el);
    }
    el.textContent = text;
    el.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => el.classList.remove("show"), 2200);
  }

  async function copyText(text) {
    if (!navigator.clipboard) return false;
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      return false; /* blocked (permissions / insecure context) */
    }
  }

  /* ------------------------------------------------------------ header */

  function initHeaderScroll() {
    const header = document.getElementById("site-header");
    if (!header) return;
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* -------------------------------------------------------- mobile nav */

  function initMobileNav() {
    const toggle = document.getElementById("nav-toggle");
    const mobile = document.getElementById("nav-mobile");
    const main = document.querySelector("main");
    const footer = document.querySelector(".site-footer");
    if (!toggle || !mobile) return;

    const setInert = (el, value) => { if (el) el.inert = value; };

    function onKeydown(e) {
      if (e.key === "Escape") { closeMenu(); return; }
      if (e.key !== "Tab") return;
      const focusables = mobile.querySelectorAll("a, button");
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }

    function openMenu() {
      mobile.classList.add("open");
      mobile.setAttribute("aria-hidden", "false");
      document.body.classList.add("no-scroll");
      toggle.classList.add("open");
      toggle.setAttribute("aria-expanded", "true");
      setInert(main, true);
      setInert(footer, true);
      const firstLink = mobile.querySelector("a");
      if (firstLink) firstLink.focus();
      document.addEventListener("keydown", onKeydown);
    }

    function closeMenu(restoreFocus = true) {
      mobile.classList.remove("open");
      mobile.setAttribute("aria-hidden", "true");
      document.body.classList.remove("no-scroll");
      toggle.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      setInert(main, false);
      setInert(footer, false);
      document.removeEventListener("keydown", onKeydown);
      if (restoreFocus) toggle.focus();
    }

    toggle.addEventListener("click", () => {
      if (mobile.classList.contains("open")) closeMenu();
      else openMenu();
    });
    mobile.querySelectorAll("a[href^='#']").forEach((a) => {
      a.addEventListener("click", () => closeMenu(false));
    });
  }

  /* ------------------------------------------------------ language links */

  // Keep the visitor's place when switching language: /uz/#projects → /ru/#projects
  function initLangLinks() {
    document.querySelectorAll(".lang-switch a").forEach((a) => {
      a.addEventListener("click", () => {
        if (window.location.hash) a.href = a.getAttribute("href").split("#")[0] + window.location.hash;
      });
    });
  }

  /* --------------------------------------------------- scrollspy, reveal */

  function initScrollspy() {
    if (!("IntersectionObserver" in window)) return;
    const links = Array.from(document.querySelectorAll(".nav-links a[href^='#']"));
    const sections = links.map((l) => document.querySelector(l.getAttribute("href"))).filter(Boolean);
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = `#${entry.target.id}`;
          links.forEach((l) => {
            const active = l.getAttribute("href") === id;
            l.classList.toggle("active", active);
            if (active) l.setAttribute("aria-current", "true");
            else l.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px", threshold: 0 }
    );
    sections.forEach((s) => observer.observe(s));
  }

  function initReveal() {
    const items = document.querySelectorAll(".reveal");
    if (!("IntersectionObserver" in window) || prefersReducedMotion) {
      items.forEach((el) => el.classList.add("in-view"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("in-view");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
    );
    items.forEach((el) => observer.observe(el));
  }

  /* ---------------------------------------------------------- copy email */

  function initCopyEmail() {
    const btn = document.getElementById("copy-email-btn");
    if (!btn || !navigator.clipboard) return; // stays hidden — mailto still works
    btn.hidden = false;
    const label = btn.querySelector(".copy-label");
    btn.addEventListener("click", async () => {
      if (!(await copyText(btn.dataset.email))) return;
      btn.classList.add("copied");
      if (label) label.textContent = btn.dataset.copiedLabel;
      window.setTimeout(() => {
        btn.classList.remove("copied");
        if (label) label.textContent = btn.dataset.label;
      }, 2000);
    });
  }

  /* -------------------------------------------------------- contact form */

  function initContactForm() {
    const form = document.getElementById("contact-form");
    if (!form || !window.fetch || !window.FormData) return;
    const status = document.getElementById("form-status");
    const submit = form.querySelector(".form-submit");
    const submitLabel = submit.textContent;

    function setFieldError(name, message) {
      const input = form.elements[name];
      if (!input) return;
      const field = input.closest(".field");
      const err = document.getElementById(`${input.id}-err`);
      if (field) field.classList.toggle("has-error", Boolean(message));
      if (message) input.setAttribute("aria-invalid", "true");
      else input.removeAttribute("aria-invalid");
      if (err) err.textContent = message || "";
    }

    function setStatus(text, kind) {
      status.textContent = text || "";
      status.classList.toggle("is-success", kind === "success");
      status.classList.toggle("is-error", kind === "error");
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      ["name", "contact", "message"].forEach((n) => setFieldError(n, ""));
      setStatus("", null);
      submit.disabled = true;
      submit.textContent = form.dataset.sendingLabel;

      try {
        const response = await fetch(form.action.split("#")[0], {
          method: "POST",
          body: new FormData(form),
          headers: { "X-Requested-With": "fetch", Accept: "application/json" },
          credentials: "same-origin",
        });
        const data = await response.json();
        if (data.ok) {
          form.reset();
          setStatus(data.message, "success");
        } else {
          const errors = data.errors || {};
          Object.entries(errors).forEach(([name, msg]) => setFieldError(name, msg));
          setStatus(data.message, "error");
          const firstInvalid = form.querySelector("[aria-invalid='true']");
          if (firstInvalid) firstInvalid.focus();
        }
      } catch (err) {
        // Network/JSON trouble — fall back to a classic form submit, which
        // the server handles fully on its own.
        HTMLFormElement.prototype.submit.call(form);
        return;
      } finally {
        submit.disabled = false;
        submit.textContent = submitLabel;
      }
    });
  }

  /* ---------------------------------------------------- ⌘K command palette */

  function normalize(text) {
    return text
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[ʻʼ'‘’`]/g, "");
  }

  function initCommandPalette() {
    const dialog = document.getElementById("cmdk");
    const input = document.getElementById("cmdk-input");
    const list = document.getElementById("cmdk-list");
    const empty = document.getElementById("cmdk-empty");
    const dataEl = document.getElementById("cmdk-commands");
    if (!dialog || !input || !list || !dataEl || typeof dialog.showModal !== "function") return;

    let commands = [];
    try { commands = JSON.parse(dataEl.textContent); } catch (e) { return; }
    commands.forEach((c, i) => { c.id = `cmdk-opt-${i}`; c.haystack = normalize(`${c.label} ${c.group}`); });

    const isMac = /Mac|iPhone|iPad/.test(navigator.userAgentData?.platform || navigator.platform || "");
    document.querySelectorAll("[data-mod-key]").forEach((k) => { k.textContent = isMac ? "⌘" : "Ctrl"; });
    document.querySelectorAll("[data-cmdk-open]").forEach((btn) => {
      btn.hidden = false;
      btn.addEventListener("click", open);
    });

    let visible = [];
    let active = 0;

    function render() {
      const terms = normalize(input.value.trim()).split(/\s+/).filter(Boolean);
      visible = commands.filter((c) => terms.every((t) => c.haystack.includes(t)));
      active = Math.min(active, Math.max(visible.length - 1, 0));
      list.innerHTML = "";
      let group = null;
      visible.forEach((c, i) => {
        if (c.group !== group) {
          group = c.group;
          const g = document.createElement("li");
          g.className = "cmdk-group";
          g.setAttribute("role", "presentation");
          g.textContent = group;
          list.appendChild(g);
        }
        const li = document.createElement("li");
        li.id = c.id;
        li.className = "cmdk-item" + (c.current ? " is-current" : "");
        li.setAttribute("role", "option");
        li.setAttribute("aria-selected", i === active ? "true" : "false");
        const label = document.createElement("span");
        label.textContent = c.label;
        li.appendChild(label);
        const meta = document.createElement("span");
        meta.className = "cmdk-meta";
        meta.textContent = c.current ? "●" : c.external ? "↗" : c.kind === "copy" ? "⧉" : "";
        li.appendChild(meta);
        li.addEventListener("mousemove", () => { if (active !== i) { active = i; highlight(); } });
        li.addEventListener("click", () => run(c));
        list.appendChild(li);
      });
      empty.hidden = visible.length > 0;
      highlight();
    }

    function highlight() {
      list.querySelectorAll(".cmdk-item").forEach((el) => {
        el.setAttribute("aria-selected", el.id === visible[active]?.id ? "true" : "false");
      });
      const current = visible[active];
      if (current) {
        input.setAttribute("aria-activedescendant", current.id);
        document.getElementById(current.id)?.scrollIntoView({ block: "nearest" });
      } else {
        input.removeAttribute("aria-activedescendant");
      }
    }

    function open() {
      if (dialog.open) return;
      input.value = "";
      active = 0;
      render();
      dialog.showModal();
      input.focus();
    }

    function close() { if (dialog.open) dialog.close(); }

    async function run(c) {
      close();
      if (c.kind === "scroll") {
        const target = document.querySelector(c.target);
        if (!target) return;
        target.scrollIntoView({ behavior: scrollBehavior, block: "start" });
        if (!target.hasAttribute("tabindex")) target.setAttribute("tabindex", "-1");
        target.focus({ preventScroll: true });
        history.replaceState(null, "", c.target);
      } else if (c.kind === "href") {
        if (c.external) window.open(c.href, "_blank", "noopener");
        else window.location.href = c.href;
      } else if (c.kind === "copy") {
        const btn = document.getElementById("copy-email-btn");
        if (await copyText(c.value)) toast(btn ? btn.dataset.copiedLabel : "✓");
      }
    }

    input.addEventListener("input", () => { active = 0; render(); });
    input.addEventListener("keydown", (e) => {
      if (!visible.length) return;
      if (e.key === "ArrowDown") { e.preventDefault(); active = (active + 1) % visible.length; highlight(); }
      else if (e.key === "ArrowUp") { e.preventDefault(); active = (active - 1 + visible.length) % visible.length; highlight(); }
      else if (e.key === "Home") { e.preventDefault(); active = 0; highlight(); }
      else if (e.key === "End") { e.preventDefault(); active = visible.length - 1; highlight(); }
      else if (e.key === "Enter") { e.preventDefault(); run(visible[active]); }
    });
    // Click on the backdrop (the <dialog> itself, outside the panel) closes it.
    dialog.addEventListener("click", (e) => { if (e.target === dialog) close(); });

    document.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (dialog.open) close(); else open();
      }
    });
  }

  /* ---------------------------------------------------------------- boot */

  function boot() {
    initHeaderScroll();
    initMobileNav();
    initLangLinks();
    initScrollspy();
    initReveal();
    initCopyEmail();
    initContactForm();
    initCommandPalette();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
