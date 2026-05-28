# MKCinemas Madurai — Website

Static website for MKCinemas Madurai (movies, web series, ad shoots, casting).

## Host locally

1. Open this folder in VS Code / Cursor.
2. Right-click `index.html` → **Open with Live Server**  
   Or open `index.html` directly in your browser.

## Deploy (production)

Upload these to any static host (Netlify, Vercel, GitHub Pages, cPanel, etc.):

- `index.html`
- `assets/` (all images)

**Entry file:** `index.html`

## Regenerate banner & logo from `sample.png`

```bash
pip install -r requirements.txt
python scripts/process_assets.py
```

Outputs:

- `assets/hero-banner.png` — cropped hero (no text)
- `assets/logo-gold-silhouette.png` — gold silhouette logo

## Contact

- **Madurai Mani** — +91 98425 20272 (phone & WhatsApp)
- **Address:** 39, 2nd Floor, Nehru Nagar, Bypass Road, Madurai – 625016
