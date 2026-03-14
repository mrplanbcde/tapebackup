# TapeBackup.org

Standalone static site for `tapebackup.org`.

## Contents

- Mirrored core site pages and assets
- Dedicated Tape Q&A hub
- Individual Q&A pages under `/tape-q-and-a/*`
- `vercel.json` routing for static deployment on Vercel

## Local Deploy

```bash
npx vercel deploy -y
```

## Notes

- DNS currently points `tapebackup.org` and `www.tapebackup.org` at Vercel.
- The Q&A section is implemented as static HTML for predictable routing and easy publishing.
