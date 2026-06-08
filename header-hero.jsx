/* global React, Icon, Social, Brand */

const NAV = [
  { label: "About Tape", items: [
    ["Why LTO Tape", "Air-gap, WORM & economics"],
    ["LTO Generations", "From LTO-6 to LTO-14"],
    ["Air-Gap Security", "Offline ransomware defense"],
    ["WORM Media", "Write-once compliance"],
  ]},
  { label: "LTO Prices", items: [
    ["LTO-6 Price", "12 TB — archive workhorse"],
    ["LTO-7 Price", "15 TB — mid-gen value"],
    ["LTO-8 Price", "12 TB native — cost leader"],
    ["LTO-9 Price", "18 TB — balanced modern choice"],
    ["LTO-10 Price", "30 TB — highest density"],
  ]},
  { label: "Resources", items: [
    ["Tape Q&A", "62 standalone answers"],
    ["Blog", "Real-world LTO workflows"],
    ["Buying Guide", "How to choose a generation"],
  ]},
  { label: "Contact", items: [
    ["Get Pricebook", "Latest LTO media pricing"],
    ["Contact Us", "Talk to TapeBackup"],
  ]},
];

function Header() {
  const [open, setOpen] = React.useState(false);
  return (
    <React.Fragment>
      <div className="topbar">
        <div className="wrap">
          <a href="/tape-q-and-a">Tape Q&amp;A</a>
          <span className="sep" />
          <a href="/lto-tape-price-trend">LTO Prices</a>
          <span className="sep" />
          <a href="/contact">Contact Us</a>
        </div>
      </div>

      <header className="site-header">
        <div className="wrap">
          <Brand />
          <nav className="nav">
            {NAV.map((n) => (
              <div className="nav-item" key={n.label}>
                <a className="nav-link" href="#" onClick={(e) => e.preventDefault()}>
                  {n.label}
                  <span className="car"><Icon name="chevron" size={15} /></span>
                </a>
                <div className="dropdown">
                  {n.items.map(([t, s]) => (
                    <a className="dd-link" href="#" key={t} onClick={(e) => e.preventDefault()}>
                      {t}<span>{s}</span>
                    </a>
                  ))}
                </div>
              </div>
            ))}
          </nav>
          <div className="header-right">
            <a className="btn btn-primary btn-sm" href="/contact">
              Get Pricebook
              <span className="arr"><Icon name="arrow" size={16} /></span>
            </a>
            <button className="burger" aria-label="Menu" onClick={() => setOpen(!open)}>
              <Icon name="menu" size={22} />
            </button>
          </div>
        </div>
      </header>
    </React.Fragment>
  );
}

function Cartridge() {
  return (
    <div className="cart-stage">
      <span className="cart-rings" />
      <span className="cart-halo" />
      <div className="cartridge">
        <span className="cart-corner" />
        <span className="cart-window" />
        <span className="cart-chip">LTFS · WORM READY</span>
        <div className="cart-grip"><i /><i /><i /><i /></div>
        <div className="cart-label">
          <div className="lt">ULTRIUM</div>
          <div className="gen">10<small>+</small></div>
        </div>
      </div>
    </div>
  );
}

const SLIDES = [
  {
    eyebrow: "LTO Tape Backup · 2025",
    title: <>Built for your <span className="accent">long-term archive.</span></>,
    sub: "LTO tape delivers the lowest cost per terabyte in storage — open, interchangeable, and ready for data you need to keep for decades. Air-gapped and offline by design.",
    primary: "Why Choose Tape",
    primaryHref: "/why-tape",
    secondary: "View LTO Prices",
    secondaryHref: "/lto-tape-price-trend",
  },
  {
    eyebrow: "Security",
    title: <>Air-gapped. <span className="accent">Ransomware-proof.</span></>,
    sub: "An offline LTO cartridge is completely invisible to ransomware. Hardware AES-256 encryption and WORM media give you a last line of defense that simply cannot be reached over a network.",
    primary: "How Air-Gap Works",
    primaryHref: "/why-tape",
    secondary: "WORM & Encryption",
    secondaryHref: "/tape-q-and-a",
  },
  {
    eyebrow: "Economics",
    title: <>The lowest cost <span className="accent">per terabyte.</span></>,
    sub: "Idle tape draws zero power and scales by adding cartridges — not arrays. LTO-9 delivers ~$5/TB native. For cold archive and long-term retention, nothing else comes close on TCO.",
    primary: "See LTO-9 Pricing",
    primaryHref: "/lto-tape-price-trend/lto9-price",
    secondary: "Compare Generations",
    secondaryHref: "/lto-tape-price-trend",
  },
];

function Hero() {
  const [i, setI] = React.useState(0);
  const [paused, setPaused] = React.useState(false);
  const go = (n) => setI((n + SLIDES.length) % SLIDES.length);

  React.useEffect(() => {
    if (paused) return;
    const t = setInterval(() => setI((v) => (v + 1) % SLIDES.length), 6500);
    return () => clearInterval(t);
  }, [paused]);

  const s = SLIDES[i];
  return (
    <section className="hero" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
      <div className="wrap">
        <div className="hero-grid">
          <div className="hero-copy">
            <div className="slide-fade" key={"c" + i}>
              <span className="eyebrow"><span className="dot" />{s.eyebrow}</span>
              <h1>{s.title}</h1>
              <p className="hero-sub">{s.sub}</p>
              <div className="hero-cta">
                <a className="btn btn-primary" href={s.primaryHref}>
                  {s.primary}<span className="arr"><Icon name="arrow" size={18} /></span>
                </a>
                <a className="btn btn-ghost" href={s.secondaryHref}>{s.secondary}</a>
              </div>
            </div>
            <div className="hero-controls">
              <div className="dots">
                {SLIDES.map((_, n) => (
                  <button key={n} className={"dot-btn" + (n === i ? " on" : "")} onClick={() => go(n)} aria-label={"Slide " + (n + 1)} />
                ))}
              </div>
              <div className="arrows">
                <button className="arrow" onClick={() => go(i - 1)} aria-label="Previous"><Icon name="left" size={18} /></button>
                <button className="arrow" onClick={() => go(i + 1)} aria-label="Next"><Icon name="right" size={18} /></button>
              </div>
              <span className="slide-count"><b>{String(i + 1).padStart(2, "0")}</b> / {String(SLIDES.length).padStart(2, "0")}</span>
            </div>
          </div>
          <Cartridge />
        </div>
      </div>
    </section>
  );
}

Object.assign(window, { Header, Hero, Cartridge });
