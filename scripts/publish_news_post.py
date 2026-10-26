"""Generate the air-gap-backup post for tapebackup.org and rebuild the site.
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

PUBLISHED = date(2026, 10, 26)

post_data = {
    "slug": "air-gap-backup-physical-tape-vs-cloud",
    "title": "Air Gap Backup: Physical Tape vs Cloud",
    "description": "Air gap backup is surging as ransomware hits cloud accounts. Here is why physical LTO tape isolation stops attacks that bypass logical cloud locks.",
    "category": "Security",
    "body": """<p><strong>Air gap backup has split into two competing designs: physical isolation and logical software locks. While cloud providers sell immutable object storage as a modern air gap, ransomware groups increasingly hijack administrative identity planes to delete cloud repositories. A physical LTO tape sitting on a shelf or unmounted inside an automated library remains the only recovery copy that network credentials cannot reach or destroy.</strong></p>

<h2>What broke logical air gaps</h2>
<p>For several years, storage teams replaced offline media with cloud-based immutable buckets and separate backup accounts. The theory seemed sound: configure object lock with compliance retention, lock the policy for thirty days, and treat the bucket as an air-gapped copy.</p>
<p>Modern threat actors bypass this safeguard without touching the storage protocol. Instead of breaking cryptographic locks, attackers target the identity plane. Through session token theft, compromised identity provider credentials, or elevated role abuse, intruders gain access to the root tenancy. From that vantage point, attackers do not need to modify locked objects. They can delete the entire cloud subscription, alter billing permissions to cause account termination, or destroy the encryption keys stored in key management services. When the management plane fails, logical isolation vanishes with it.</p>

<h2>Why physical tape isolation cannot be reached over IP</h2>
<p>A physical air gap relies on an absolute boundary: the absence of an electrical and network path. An LTO cartridge stores data on barium ferrite or metal particle tape inside a plastic housing. When the write process finishes and the drive unloads the cartridge, all electrical contact ends.</p>
<p>Inside an automated tape library, robotic arms place the media into passive storage slots. Even if an attacker gains root credentials on your backup server, controls your hypervisors, and compromises your switches, the unmounted tape cannot execute commands. It has no IP address, no operating system kernel, no remote management port, and no firmware listener. Modifying an offline cartridge requires physical human presence in the data room.</p>

<h2>The economics of offline archive storage</h2>
<p>Security is the initial reason teams reintroduce tape, but operating costs keep it in place. Our September 2026 US price tracker lists 18 TB LTO-9 cartridges at $92 to $112, which comes to $5.14 to $6.20 per native terabyte. An LTO-8 cartridge costs between $70 and $80 for 12 TB, or $5.83 to $6.67 per native terabyte.</p>
<p>Storing that same petabyte in hot or cold cloud storage requires perpetual monthly capacity charges. When an enterprise suffers a catastrophic incident and must restore hundreds of terabytes immediately, cloud egress fees and retrieval penalties create massive emergency expenses. A tape cartridge sitting on a shelf draws zero watts of electricity, produces zero heat, and incurs zero monthly cloud subscription bills.</p>

<h2>How to build a practical air-gapped workflow</h2>
<p>Adopting an air-gapped tape backup does not mean abandoning disk snapshots or cloud replication. Fast daily recoveries for individual lost files belong on local disk arrays. Tape provides the deep, immutable foundation underneath them.</p>
<p>A standard resilience pattern keeps daily and weekly recovery points on primary storage, writes monthly and quarterly full archives to LTO tape, and ejects those tapes to an offsite fireproof vault or separate facility. In an automated library, dedicated air-gap software partitions isolate vault cartridges from active drive pools. If ransomware encrypts every server on the network, the offline tape set guarantees a clean restoration baseline.</p>

<h2>Frequently asked questions</h2>
<h3>What is the difference between a physical air gap and a logical air gap?</h3>
<p>A physical air gap disconnects the storage media entirely from electrical and network connections, as with an ejected LTO tape. A logical air gap keeps storage connected to the network but restricts access through software rules, access control lists, or immutable bucket policies. Logical gaps can be bypassed if administrative credentials are compromised.</p>

<h3>Can ransomware infect an unmounted tape cartridge?</h3>
<p>No. An unmounted tape sits in a slot or storage shelf with no electrical connection, no processor, and no network interface. Remote software cannot write to, read from, or delete data on an unmounted cartridge.</p>

<h3>Do tape drives support hardware-based encryption?</h3>
<p>Yes. All LTO tape drives from LTO-4 through LTO-10 support hardware-level 256-bit AES encryption directly on the drive ASIC. Data is encrypted before being written to media, with no performance penalty.</p>

<h3>How does the total cost of tape compare to cloud archive tiers?</h3>
<p>For archives above 100 terabytes held longer than two years, LTO tape costs significantly less than cloud cold storage. Tape media requires a one-time purchase with no recurring monthly capacity charges and no egress fees during restores.</p>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"What is the difference between a physical air gap and a logical air gap?","acceptedAnswer":{"@type":"Answer","text":"A physical air gap disconnects the storage media entirely from electrical and network connections, as with an ejected LTO tape. A logical air gap keeps storage connected to the network but restricts access through software rules, access control lists, or immutable bucket policies. Logical gaps can be bypassed if administrative credentials are compromised."}},{"@type":"Question","name":"Can ransomware infect an unmounted tape cartridge?","acceptedAnswer":{"@type":"Answer","text":"No. An unmounted tape sits in a slot or storage shelf with no electrical connection, no processor, and no network interface. Remote software cannot write to, read from, or delete data on an unmounted cartridge."}},{"@type":"Question","name":"Do tape drives support hardware-based encryption?","acceptedAnswer":{"@type":"Answer","text":"Yes. All LTO tape drives from LTO-4 through LTO-10 support hardware-level 256-bit AES encryption directly on the drive ASIC. Data is encrypted before being written to media, with no performance penalty."}},{"@type":"Question","name":"How does the total cost of tape compare to cloud archive tiers?","acceptedAnswer":{"@type":"Answer","text":"For archives above 100 terabytes held longer than two years, LTO tape costs significantly less than cloud cold storage. Tape media requires a one-time purchase with no recurring monthly capacity charges and no egress fees during restores."}}]}</script>

<p>Compare current media options on our <a href="/lto-tape-price-trend">LTO price tracker</a>, calculate your capacity with the <a href="/backup-calculator">backup calculator</a>, or read our guide on <a href="/why-tape/lto-vs-cloud">LTO tape vs cloud storage</a>.</p>
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
