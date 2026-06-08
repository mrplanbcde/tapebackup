/* global React, Icon, Social, Brand */

const STATS = [
  { n: "30", u: "yr", l: "Archival shelf life per cartridge" },
  { n: "~$5", u: "/TB", l: "Cost per terabyte on LTO-9" },
  { n: "WORM", l: "Write-once compliance media" },
  { n: "Air-gap", l: "True offline ransomware defense" },
];

function Stats() {
  return (
    <div className="stats">
      <div className="wrap">
        {STATS.map((s) => (
          <div className="stat" key={s.l}>
            <div className="n">{s.n}{s.u && <span className="u">{s.u}</span>}</div>
            <div className="l">{s.l}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const WHY = [
  {
    ico: "database", h: "Capacity that scales",
    p: "LTO density roughly doubles every generation. Grow your archive by adding cartridges to a shelf — not arrays to a rack. LTO-9 holds 18 TB native; LTO-10 jumps to 30 TB.",
    feats: ["Open, interchangeable media", "Vendor-neutral standard", "Petabyte-class library support"],
  },
  {
    ico: "shield", h: "Security by design",
    p: "A removed cartridge simply cannot be reached over the network. Pair that physical air-gap with hardware AES-256 encryption and write-once WORM media for true data immutability.",
    feats: ["Hardware AES-256 encryption", "WORM tamper-proof media", "True physical air-gap"],
  },
  {
    ico: "leaf", h: "Cost & sustainability",
    p: "Idle tape draws no power. With the lowest cost per terabyte in storage and near-zero energy at rest, LTO keeps both your budget and your carbon footprint down.",
    feats: ["Lowest TCO per terabyte", "Near-zero idle energy draw", "Decades without forced migration"],
  },
];

function WhyTape() {
  return (
    <section className="block why" id="why">
      <div className="wrap">
        <div className="sec-head">
          <span className="eyebrow"><span className="dot" />Why LTO Tape</span>
          <h2>Three reasons tape still wins the archive.</h2>
          <p>For storage and backup teams managing data that must survive — and stay recoverable — for years, LTO Ultrium remains the quiet workhorse behind the world's most resilient archives.</p>
        </div>
        <div className="why-grid">
          {WHY.map((c) => (
            <article className="why-card" key={c.h}>
              <div className="why-ico"><Icon name={c.ico} size={24} /></div>
              <h3>{c.h}</h3>
              <p>{c.p}</p>
              <ul className="feats">
                {c.feats.map((f) => (
                  <li key={f}><Icon name="check" size={16} />{f}</li>
                ))}
              </ul>
              <a className="textlink" href="/why-tape">Learn more<span className="arr"><Icon name="arrow" size={16} /></span></a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

const GENS = [
  { g: "LTO-6", cap: "2.5 TB", st: "done", href: "/lto-tape-price-trend/lto6-price" },
  { g: "LTO-7", cap: "6 TB", st: "done", href: "/lto-tape-price-trend/lto7-price" },
  { g: "LTO-8", cap: "12 TB", st: "done", href: "/lto-tape-price-trend/lto8-price" },
  { g: "LTO-9", cap: "18 TB", st: "done", href: "/lto-tape-price-trend/lto9-price" },
  { g: "LTO-10", cap: "30 TB", st: "cur", href: "/lto-tape-price-trend/lto10-price" },
  { g: "LTO-11", cap: "Planned", st: "next", href: "#" },
  { g: "LTO-12", cap: "Planned", st: "next", href: "#" },
  { g: "LTO-13", cap: "Planned", st: "next", href: "#" },
  { g: "LTO-14", cap: "Planned", st: "next", href: "#" },
];

function Roadmap() {
  const curIndex = GENS.findIndex((x) => x.st === "cur");
  const fill = (curIndex / (GENS.length - 1)) * 100;
  return (
    <section className="block roadmap" id="roadmap">
      <div className="wrap">
        <div className="sec-head">
          <span className="eyebrow"><span className="dot" />LTO Roadmap</span>
          <h2>A format with a decade of headroom.</h2>
          <p>The published LTO roadmap extends through Generation 14 — so the format you adopt today has a clear, committed upgrade path. Native capacities shown; compressed is typically 2.5×.</p>
        </div>
        <div className="rm-track">
          <div className="rm-line"><span className="fill" style={{ width: fill + "%" }} /></div>
          <div className="rm-nodes">
            {GENS.map((n) => (
              <a className={"rm-node " + n.st} key={n.g} href={n.href} style={{textDecoration:"none"}}>
                {n.st === "cur" && <span className="tag">Current</span>}
                <span className="cap">{n.cap}</span>
                <span className="pt" />
                <span className="gen">{n.g}</span>
              </a>
            ))}
          </div>
        </div>
        <div className="rm-legend">
          <span><i style={{ background: "var(--accent)" }} />Shipping</span>
          <span><i style={{ background: "#fff", border: "2px solid var(--accent)" }} />Current generation</span>
          <span><i style={{ background: "var(--line-2)" }} />On the roadmap</span>
        </div>
      </div>
    </section>
  );
}

const BLOG = [
  {
    cat: "Analysis",
    date: "May 2026",
    h: "Tape Is Dead, Right? Then Why Are People Quietly Building Backup Systems Around It Again",
    href: "/blog/tape-is-dead-right-then-why-are-people-quietly-building-backup-systems-around-it-again",
  },
  {
    cat: "Guide",
    date: "Apr 2026",
    h: "Why an Air-Gapped Copy Belongs in Every 3-2-1 Backup Strategy",
    href: "/blog/offsite-tape-backups-still-beat-most-good-enough-plans",
  },
  {
    cat: "Pricing",
    date: "Mar 2026",
    h: "Buying a Few Cheap LTO Tapes Is How the Rabbit Hole Starts",
    href: "/blog/buying-a-few-cheap-lto-tapes-is-how-the-rabbit-hole-starts",
  },
];

function BlogNews() {
  return (
    <section className="block news" id="blog">
      <div className="wrap">
        <div className="news-head">
          <div className="sec-head" style={{ margin: 0 }}>
            <span className="eyebrow"><span className="dot" />Latest from the Blog</span>
            <h2>Real-world LTO backup</h2>
          </div>
          <a className="btn btn-ghost btn-sm" href="/blog">
            All posts<span className="arr"><Icon name="arrow" size={16} /></span>
          </a>
        </div>
        <div className="news-grid">
          {BLOG.map((a) => (
            <article className="news-card" key={a.h}>
              <a href={a.href} style={{display:"contents"}}>
                <div className="news-thumb">
                  <span className="gloss" />
                  <span className="tcart" />
                  <span className="cat">{a.cat}</span>
                </div>
                <div className="news-body">
                  <span className="date">{a.date}</span>
                  <h3>{a.h}</h3>
                  <div className="more">
                    <span className="textlink">Read more<span className="arr"><Icon name="arrow" size={16} /></span></span>
                  </div>
                </div>
              </a>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function PriceCTA() {
  return (
    <section className="licensing">
      <div className="wrap">
        <div className="lic-panel">
          <div>
            <span className="eyebrow"><span className="dot" style={{ background: "#b69cf2" }} />LTO Tape Pricing</span>
            <h2>Get the latest LTO tape pricebook.</h2>
            <p>Compare current HPE, IBM, Dell, Fujifilm, and Sony LTO media pricing across all generations — from LTO-6 through LTO-10. Request the pricebook bundle or browse individual generation guides.</p>
          </div>
          <div className="lic-actions">
            <a className="btn btn-white" href="/contact">
              Request pricebook<span className="arr"><Icon name="arrow" size={18} /></span>
            </a>
            <a className="btn btn-outline-w" href="/lto-tape-price-trend">Browse prices</a>
          </div>
        </div>
      </div>
    </section>
  );
}

const FCOLS = [
  { h: "LTO Prices", links: [["LTO-6 Price","/lto-tape-price-trend/lto6-price"],["LTO-7 Price","/lto-tape-price-trend/lto7-price"],["LTO-8 Price","/lto-tape-price-trend/lto8-price"],["LTO-9 Price","/lto-tape-price-trend/lto9-price"],["LTO-10 Price","/lto-tape-price-trend/lto10-price"]] },
  { h: "Resources", links: [["Tape Q&A","/tape-q-and-a"],["Blog","/blog"],["Why Tape","/why-tape"],["Buying Guide","/resources"]] },
  { h: "Company", links: [["About","/about"],["Contact","/contact"],["Price Inquiry","/lto-tape-price-inquiry"]] },
  { h: "Legal", links: [["Privacy Policy","/privacy"],["Terms of Use","/terms"],["Sitemap","/sitemap.xml"]] },
];

function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer-top">
          <div>
            <Brand footer />
            <p className="blurb">TapeBackup.org — an independent resource for LTO tape backup technology, pricing, and workflows. Not affiliated with the LTO Program consortium.</p>
            <div className="soc">
              <a href="#" aria-label="LinkedIn"><Social name="in" size={17} /></a>
              <a href="#" aria-label="X"><Social name="x" size={15} /></a>
            </div>
          </div>
          {FCOLS.map((c) => (
            <div className="fcol" key={c.h}>
              <h4>{c.h}</h4>
              {c.links.map(([l, href]) => <a href={href} key={l}>{l}</a>)}
            </div>
          ))}
        </div>
        <div className="footer-bot">
          <span>© 2026 TapeBackup.org — Independent LTO tape backup resource.</span>
          <div className="links">
            <a href="/privacy">Privacy</a>
            <a href="/terms">Terms</a>
            <a href="/sitemap.xml">Sitemap</a>
          </div>
        </div>
      </div>
    </footer>
  );
}

Object.assign(window, { Stats, WhyTape, Roadmap, BlogNews, PriceCTA, Footer });
