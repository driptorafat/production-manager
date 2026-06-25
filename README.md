# 🏭 Production Manager

A single-file web app for tracking manufacturing/production of your export orders —
from raw material through to shipment. It is the companion to **Export Manager** and
**syncs orders and production data** with it through a shared private GitHub Gist.

Like Export Manager, the whole app is one self-contained `index.html` (no build step,
no server, no dependencies). Data is stored locally in IndexedDB and synced to the cloud.

---

## Features

- **Dashboard** — KPIs (active orders, due ≤7 days, overdue, shipped, on-time rate,
  active units/value), stage-distribution donut, orders-by-month bars, upcoming deadlines.
- **Production Board (Kanban)** — drag order cards between stages; progress auto-updates.
- **Orders** — searchable/filterable table with progress bars, deadlines, priority.
- **Order editor** — stage pipeline, production checklist, raw-material/BOM tracking
  (needed vs received), quality-check status, photos, notes, priority.
- **Deadlines** — active orders grouped Overdue / This week / Next 30 days / Later.
- **Reports** — printable Production Status, Deadline/WIP, and Outstanding Materials.
- **Configurable pipeline** — rename/reorder/add/remove stages (the last stage = "shipped").
- **6 themes**, login, CSV export, JSON backup/restore, multi-year.

---

## How it connects to Export Manager

Both apps share **one private GitHub Gist** and **one gist-scoped token**.

| File in the Gist     | Written by        | Read by                       |
|----------------------|-------------------|-------------------------------|
| `exportmanager.json` | Export Manager    | Production Manager (orders →) |
| `production.json`    | Production Manager| Production Manager (devices)   |

- **Import Orders** — Production reads `exportmanager.json` and creates/updates a
  production order per shipment (matched by Order No). Your production progress is
  preserved on re-import; it never writes to `exportmanager.json` during import.
- **Push / Pull Production Data** — saves/loads `production.json` so multiple devices
  stay in sync.
- **Push Shipped Status → Export Manager** *(opt-in)* — safely read-modify-writes only
  the `shipped` field of matching orders inside `exportmanager.json`; everything else is
  left untouched.

### Linking the two apps (one time)
1. In **Export Manager** → Settings → Cloud Sync, set up your token and run **Sync Now**.
   Copy the **Gist ID** it generates.
2. In **Production Manager** → Settings → Cloud Sync, paste the **same token** and the
   **same Gist ID**, then **Save Cloud Config**.
3. Click **Import Orders from Export Manager**. Done.

---

## Run locally
Just open `index.html` in a browser. Default login: **admin / admin123**
(change it in Settings → Login Credentials).

## Deploy online (GitHub Pages)
```bash
cd "/Users/rafat/Personal/Production"
echo "ghp_yourTokenHere" > .deploy_token   # token needs 'repo' (and 'gist' for sync)
python3 deploy.py
```
Your app goes live at `https://YOUR_USERNAME.github.io/production-manager/`.

After any change to `index.html`, just run `python3 deploy.py` again.
