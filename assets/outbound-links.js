(function () {
  var STYLE_ID = "tb-outbound-links-style";
  var BLOCK_SELECTOR = '[data-outbound-links="true"]';
  var DEFAULT_LINKS = [
    {
      href: "https://www.lto.org/",
      title: "LTO Program",
      label: "Official format",
      description: "Generation specs, roadmap details, and compatibility guidance for the LTO ecosystem.",
    },
    {
      href: "https://www.ibm.com/products/tape-storage",
      title: "IBM Tape Storage",
      label: "Vendor reference",
      description: "Enterprise tape storage platform information for backup, archive, and library planning.",
    },
    {
      href: "https://www.hpe.com/us/en/storage/storeever-tape.html",
      title: "HPE StoreEver Tape",
      label: "Infrastructure guide",
      description: "Tape hardware overview covering drives, libraries, and long-term retention use cases.",
    },
  ];
  var SECURITY_LINKS = [
    {
      href: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
      title: "CISA KEV Catalog",
      label: "Security advisories",
      description: "Known exploited vulnerability tracking and remediation guidance for active enterprise risks.",
    },
    {
      href: "https://nvd.nist.gov/",
      title: "NVD",
      label: "Vulnerability data",
      description: "National Vulnerability Database records, severity scoring, and CVE reference material.",
    },
    {
      href: "https://www.cisa.gov/stopransomware",
      title: "StopRansomware",
      label: "Ransomware guidance",
      description: "CISA ransomware prevention, recovery, and incident-response resources for organizations.",
    },
  ];
  var PRICE_LINKS = [
    {
      href: "https://www.lto.org/",
      title: "LTO Program",
      label: "Format baseline",
      description: "Official LTO generation specs for capacity, throughput, and roadmap comparisons.",
    },
    {
      href: "https://www.ibm.com/products/tape-storage",
      title: "IBM Tape Storage",
      label: "Price context",
      description: "Tape platform context for drive, library, and enterprise archive buying decisions.",
    },
    {
      href: "https://www.hpe.com/us/en/storage/storeever-tape.html",
      title: "HPE StoreEver Tape",
      label: "Vendor comparison",
      description: "A second enterprise ecosystem reference when comparing media and tape infrastructure options.",
    },
  ];

  function ensureStyles() {
    if (document.getElementById(STYLE_ID)) {
      return;
    }

    var style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent =
      ".tb-outbound-links{margin-top:clamp(2rem,4vw,3.5rem);}" +
      ".tb-outbound-links__inner{display:grid;gap:1.2rem;padding:clamp(1.3rem,2vw,1.8rem);border:1px solid color-mix(in oklab, #183976 14%, #bcd1ee 86%);border-radius:1.5rem;background:linear-gradient(135deg, rgba(255,255,255,.95), rgba(234,244,255,.92));box-shadow:0 18px 48px rgba(24,57,118,.08);}" +
      ".tb-outbound-links__eyebrow{margin:0;font-size:.78rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#184f99;}" +
      ".tb-outbound-links__title{margin:0;font-size:clamp(1.3rem,2vw,1.75rem);line-height:1.1;letter-spacing:-.04em;color:#172433;}" +
      ".tb-outbound-links__copy{margin:0;color:#52667e;font-size:1rem;line-height:1.75;max-width:62ch;}" +
      ".tb-outbound-links__grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem;}" +
      ".tb-outbound-links__card{display:grid;gap:.6rem;padding:1rem 1.05rem;border-radius:1.2rem;border:1px solid color-mix(in oklab, #183976 10%, #d8e3f1 90%);background:rgba(255,255,255,.85);text-decoration:none;transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;}" +
      ".tb-outbound-links__card:hover,.tb-outbound-links__card:focus-visible{transform:translateY(-2px);border-color:rgba(24,79,153,.28);box-shadow:0 16px 30px rgba(24,57,118,.12);outline:none;}" +
      ".tb-outbound-links__label{font-size:.72rem;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:#2e6e8b;}" +
      ".tb-outbound-links__card-title{font-size:1.02rem;font-weight:800;line-height:1.3;color:#172433;}" +
      ".tb-outbound-links__description{color:#5b6f87;font-size:.95rem;line-height:1.65;}" +
      ".tb-outbound-links__cta{font-size:.88rem;font-weight:800;color:#184f99;}" +
      ".tb-outbound-links--article .tb-outbound-links__inner,.tb-outbound-links--stack .tb-outbound-links__inner,.tb-outbound-links--hub .tb-outbound-links__inner{padding:1.35rem 1.4rem;}" +
      ".tb-outbound-links--page{padding-inline:clamp(1rem,3vw,2rem);}" +
      ".tb-outbound-links--page .tb-outbound-links__inner{max-width:min(1180px,100%);margin:0 auto;}" +
      "@media (max-width:960px){.tb-outbound-links__grid{grid-template-columns:1fr;}}" +
      "@media (max-width:640px){.tb-outbound-links__inner{padding:1.1rem;}.tb-outbound-links__copy{font-size:.95rem;line-height:1.65;}}";
    document.head.appendChild(style);
  }

  function currentPath() {
    var path = window.location.pathname || "/";
    if (path.length > 1) {
      path = path.replace(/\/+$/, "");
    }
    return path || "/";
  }

  function pageText() {
    var source =
      document.querySelector("main") ||
      document.querySelector(".page") ||
      document.body;
    return (source && source.textContent ? source.textContent : "").toLowerCase();
  }

  function isSecurityContext(path, text) {
    if (!/^\/tape-q-and-a\/[^/]+$/.test(path)) {
      return false;
    }
    return /(ransomware|vulnerability|security|attack|cve|mitigate|shellshock|heartbleed|log4j|wannacry|petya|spectre|meltdown|sambacry|struts)/.test(text);
  }

  function resolveLinks(path, text) {
    if (/^\/lto-tape-price-trend(?:\/|$)/.test(path)) {
      return {
        title: "Continue with official pricing references",
        copy: "Use a few outbound sources to compare LTO generation specs and vendor ecosystems alongside the price guidance on this page.",
        links: PRICE_LINKS,
      };
    }
    if (isSecurityContext(path, text)) {
      return {
        title: "Continue with external security references",
        copy: "These outbound links add broader vulnerability and ransomware context beyond the summary on this TapeBackup page.",
        links: SECURITY_LINKS,
      };
    }
    return {
      title: "Continue with official LTO references",
      copy: "These outbound links give readers a few trusted places to compare LTO specifications, tape platforms, and archive infrastructure context.",
      links: DEFAULT_LINKS,
    };
  }

  function buildBlock(config, variant, path) {
    var section = document.createElement("section");
    section.className = "tb-outbound-links tb-outbound-links--" + variant;
    section.setAttribute("data-outbound-links", "true");
    section.setAttribute("data-route", path);
    section.setAttribute("aria-labelledby", "tb-outbound-links-title");

    var grid = config.links
      .map(function (link) {
        return (
          '<a class="tb-outbound-links__card" href="' +
          link.href +
          '" target="_blank" rel="noopener noreferrer">' +
          '<span class="tb-outbound-links__label">' +
          link.label +
          "</span>" +
          '<span class="tb-outbound-links__card-title">' +
          link.title +
          "</span>" +
          '<span class="tb-outbound-links__description">' +
          link.description +
          "</span>" +
          '<span class="tb-outbound-links__cta">Open external site</span>' +
          "</a>"
        );
      })
      .join("");

    section.innerHTML =
      '<div class="tb-outbound-links__inner">' +
      '<p class="tb-outbound-links__eyebrow">External resources</p>' +
      '<h2 class="tb-outbound-links__title" id="tb-outbound-links-title">' +
      config.title +
      "</h2>" +
      '<p class="tb-outbound-links__copy">' +
      config.copy +
      "</p>" +
      '<div class="tb-outbound-links__grid">' +
      grid +
      "</div>" +
      "</div>";
    return section;
  }

  function resolveMount(path) {
    if (path === "/tape-q-and-a") {
      return {
        node:
          document.querySelector(".hub-main") ||
          document.querySelector(".hub-layout") ||
          document.querySelector("main"),
        variant: "hub",
      };
    }
    if (/^\/tape-q-and-a\/[^/]+$/.test(path)) {
      return {
        node:
          document.querySelector(".article-card") ||
          document.querySelector(".article-layout") ||
          document.querySelector("main"),
        variant: "article",
      };
    }
    if (/^\/lto-tape-price-trend(?:\/|$)/.test(path)) {
      return {
        node:
          document.querySelector(".section-stack") ||
          document.querySelector("main"),
        variant: "stack",
      };
    }
    return {
      node: document.querySelector("main") || document.querySelector("#root"),
      variant: "page",
    };
  }

  function placeBlock(block, mount) {
    if (!mount.node) {
      return false;
    }

    if (mount.variant === "article") {
      var related = mount.node.querySelector(".related-section");
      if (related && related.parentNode === mount.node) {
        related.insertAdjacentElement("afterend", block);
        return true;
      }
    }

    if (mount.variant === "hub") {
      var grid = mount.node.querySelector(".card-grid");
      if (grid && grid.parentNode === mount.node) {
        grid.insertAdjacentElement("afterend", block);
        return true;
      }
    }

    mount.node.appendChild(block);
    return true;
  }

  function render() {
    ensureStyles();
    var path = currentPath();
    var existing = document.querySelector(BLOCK_SELECTOR);
    if (existing && existing.getAttribute("data-route") === path) {
      return true;
    }
    if (existing) {
      existing.remove();
    }

    var mount = resolveMount(path);
    if (!mount.node) {
      return false;
    }

    var block = buildBlock(resolveLinks(path, pageText()), mount.variant, path);
    return placeBlock(block, mount);
  }

  function scheduleRender() {
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        render();
      });
    });
  }

  var observer = new MutationObserver(function () {
    scheduleRender();
  });

  function patchHistory(method) {
    var original = history[method];
    history[method] = function () {
      var result = original.apply(this, arguments);
      scheduleRender();
      return result;
    };
  }

  patchHistory("pushState");
  patchHistory("replaceState");
  window.addEventListener("popstate", scheduleRender);
  window.addEventListener("load", scheduleRender);

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      scheduleRender();
      observer.observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    });
  } else {
    scheduleRender();
    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  }
})();
