"""Generate the LTO roadmap post for tapebackup.org and rebuild the site.
"""
import html
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path("/Users/dali/coldmail/tapebackup")
sys.path.insert(0, str(ROOT / "scripts"))
import generate_blog_posts as G  # noqa: E402

PUBLISHED = date(2026, 10, 31)

post_data = {
    "slug": "lto-roadmap-365tb-tape-cartridge-capacity",
    "title": "LTO Roadmap: 365 TB Tape vs Cloud TCO",
    "description": "The LTO roadmap targets 365 TB per cartridge. Here is why enterprise cold archives choose tape density and zero-idle power over cloud storage bills.",
    "category": "Storage",
    "body": """<p><strong>The LTO Program roadmap officially targets up to 365 TB of native capacity per cartridge across future generations without altering the standard physical form factor. With enterprise AI training checkpoints and long-term compliance archives outgrowing disk arrays, tape remains the most economical tier for petabyte-scale data that must be kept safe for decades at zero idle power.</strong></p>

<h2>The 400x scaling curve without form factor changes</h2>
<p>Linear Tape-Open began twenty-five years ago with LTO-1, storing 100 GB on a single half-inch magnetic tape cartridge. Current mainstream deployments run on 18 TB LTO-9 and 30 to 40 TB LTO-10 media. The extended technology roadmap mapped by HPE, IBM, and Quantum projects capacity scaling through LTO-14 to 365 TB native per cartridge.</p>
<p>What makes this trajectory unique in enterprise infrastructure is physical consistency. Robotic library frames, automated tape arms, picker mechanisms, and rack dimensions designed for early LTO formats still accommodate modern generations. Upgrading a data center from petabytes to exabytes requires replacing tape drives and media cartridges rather than purchasing new floor space and structural frames.</p>

<h2>Media density versus spinning disk physical limits</h2>
<p>Hard drive manufacturers rely on heat-assisted magnetic recording (HAMR) and dual-actuator mechanics to reach 30 to 40 TB per 3.5-inch drive. While engineering achievements in hard disk density continue, spinning disks face strict physical boundaries: platter count, rotational vibration, power draw, and mechanical wear on spindle bearings.</p>
<p>Magnetic tape operates under different physics. Because tape media unrolls across a recording head only during read and write operations, the surface area available to store bits is hundreds of times larger than rigid platters. Advanced barium ferrite and strontium ferrite particulate formulations allow areal density to double repeatedly without exceeding the mechanical tolerances of tape drives.</p>

<h2>Zero idle power in the AI data center</h2>
<p>Power constraints have overtaken hardware budgets as the primary bottleneck in hyperscale and enterprise data centers. An active hard disk drive consumes six to nine watts even while idling in a storage shelf. Multiplied across tens of thousands of archive drives, spinning disk arrays generate constant heat loads and demand megawatt-scale power allocations.</p>
<p>In contrast, a tape cartridge resting in a library slot consumes zero watts of electricity and produces zero heat. For AI organizations retaining multi-terabyte model weights, raw training corpuses, and multi-year compliance archives, tape decouples storage capacity from facilities power budgets.</p>

<h2>The cost equation against cloud cold storage</h2>
<p>Public cloud providers market cold archive tiers as inexpensive storage, but the pricing model conceals severe operational risks. Storing petabytes incurs perpetual monthly charges, while data retrieval triggers punitive per-gigabyte egress fees and API transaction penalties.</p>
<p>Our September 2026 US price tracker lists 18 TB LTO-9 media at $5.14 to $6.20 per native terabyte. Once the hardware capital cost of the drive is amortized across an archive, tape media requires no monthly subscription and no retrieval fees during forensic audits or full disaster recoveries.</p>

<h2>Frequently asked questions</h2>
<h3>What is the native capacity of LTO-10?</h3>
<p>Standard LTO-10 cartridges provide 30 TB of native uncompressed capacity, with extended-length media providing 40 TB native (and up to 100 TB with standard 2.5:1 compression).</p>

<h3>How does LTO plan to reach 365 TB per cartridge?</h3>
<p>The LTO roadmap achieves 365 TB across generations through advanced magnetic particles such as strontium ferrite, narrower track widths, smoother tape substrates, and higher linear recording densities.</p>

<h3>Do newer LTO drives read older tape formats?</h3>
<p>LTO-8 and LTO-9 drives read and write the previous generation (for example, LTO-9 drives read and write LTO-8 tapes). Due to the transition to narrower tracks, LTO-10 drives focus natively on LTO-10 media to maximize throughput and reliability.</p>

<h3>What is the shelf life of modern LTO tape?</h3>
<p>Under recommended environmental conditions (15 to 25 degrees Celsius and 20 to 50 percent relative humidity), barium ferrite LTO tape cartridges have an archival lifespan exceeding thirty years.</p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What is the native capacity of LTO-10?","acceptedAnswer":{"@type":"Answer","text":"Standard LTO-10 cartridges provide 30 TB of native uncompressed capacity, with extended-length media providing 40 TB native (and up to 100 TB with standard 2.5:1 compression)."}},{"@type":"Question","name":"How does LTO plan to reach 365 TB per cartridge?","acceptedAnswer":{"@type":"Answer","text":"The LTO roadmap achieves 365 TB across generations through advanced magnetic particles such as strontium ferrite, narrower track widths, smoother tape substrates, and higher linear recording densities."}},{"@type":"Question","name":"Do newer LTO drives read older tape formats?","acceptedAnswer":{"@type":"Answer","text":"LTO-8 and LTO-9 drives read and write the previous generation (for example, LTO-9 drives read and write LTO-8 tapes). Due to the transition to narrower tracks, LTO-10 drives focus natively on LTO-10 media to maximize throughput and reliability."}},{"@type":"Question","name":"What is the shelf life of modern LTO tape?","acceptedAnswer":{"@type":"Answer","text":"Under recommended environmental conditions (15 to 25 degrees Celsius and 20 to 50 percent relative humidity), barium ferrite LTO tape cartridges have an archival lifespan exceeding thirty years."}}]}</script>

<p>Track current media and drive pricing on our <a href="/lto-tape-price-trend">LTO price tracker</a>, review our <a href="/lto-tape-capacity">LTO capacity comparison chart</a>, or test your numbers in the <a href="/backup-calculator">tape backup calculator</a>.</p>
"""
}

def main():
    words = len(re.sub(r"<[^>]+>", " ", post_data["body"]).split())
    post = G.Post(
        slug=post_data["slug"],
        title=post_data["title"],
        description=post_data["description"],
        category=post_data["category"],
        published=PUBLISHED,
        minutes=max(3, round(words / 200)),
        body_html=post_data["body"]
    )
    
    assert len(post.title) + len(" | TapeBackup.org") <= 60, f"Title too long: {len(post.title) + len(' | TapeBackup.org')}"
    assert len(post.description) <= 155, f"Description too long: {len(post.description)}"
    
    post_dir = ROOT / "blog" / post.slug
    post_dir.mkdir(parents=True, exist_ok=True)
    post_html = G.render_article(post)
    (post_dir / "index.html").write_text(post_html, encoding="utf-8")
    print(f"Wrote {post_dir / 'index.html'} ({len(post_html)} bytes, {words} words)")
    
    # Update blog listing
    existing_posts = [
        G.parse_existing_post(f)
        for f in sorted((ROOT / "blog").glob("*/index.html"))
        if f.parent.name != post.slug
    ]
    all_posts = sorted([post] + existing_posts, key=lambda x: (x.published, x.slug), reverse=True)
    (ROOT / "blog" / "index.html").write_text(G.render_listing(all_posts), encoding="utf-8")
    print(f"Updated blog listing with {len(all_posts)} posts")
    
    # Update homepage cards
    home = [{"href": f"/blog/{p.slug}", "cat": p.category, "date": "Oct 2026", "h": p.title} for p in all_posts[:3]]
    (ROOT / "data" / "home-blog.json").write_text(json.dumps(home, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    
    # Run full build
    print("Running build_site.py...")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py")], check=True)
    print("Build complete.")

if __name__ == "__main__":
    main()
