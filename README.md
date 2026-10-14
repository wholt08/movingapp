# Seattle ➔ San Diego Move Command Center 📦 ☀️

A lightweight, high-performance web app designed to coordinate our move from Seattle, WA to Encinitas / San Diego, CA. Built for mobile & desktop, fully offline capable (`localStorage`), and ready for zero-friction hosting on **GitHub Pages** (meaning it stays online even after the home server is boxed into the POD!).

---

## 🚀 Key Modules Built-in

1. **📅 Timeline & Focus View**:
   - Live **T-Minus countdowns** for POD Drop-off (Oct 28), POD Pick-up (Oct 30), and Drive Day (Oct 31).
   - **Today's Focus cards**: Surfacing top-priority actions so you don't get overwhelmed looking at 40 tasks at once.
   - **5-Phase Moving Journey Roadmap**: Step-by-step phases from permitting and purging to the California road trip.

2. **📋 Master Task Hub**:
   - All tasks from your Google Drive tracking sheet pre-loaded with status, owner, priority, and timing notes.
   - Real-time search, owner filter (William, Camille, Shared), and category accordions.
   - Quick check-off with persistent local storage.

3. **🛠️ Home Repairs & Deposit Security**:
   - Dedicated punch-list for apartment move-out inspection (Brian / Apartments.com).
   - Tracks hole spackling, scratch repairs, window sill touch-ups, and the critical Oct 30 doorbell & bidet fixture swap-backs.

4. **🏷️ Marketplace & Purge Tracker**:
   - Tracks items to sell, rehome, donate, or curb alert.
   - Target prices, buyer notes, and instant status dropdowns (Ready to List, Listed, Pending Pickup, Given Away, Sold).

5. **📦 Dual Packing Lists (POD vs. Subaru Outback)**:
   - **16' POD Container**: Heavy items, furniture, bikes, boxes, water sports gear.
   - **2015 Subaru Outback**: 10-day road trip survival kit, work/personal tech, padded computer monitors, and Scout's dog zone essentials.

6. **🤖 AI Assistant Bridge & Backup**:
   - **Copy Prompt for AI**: In one click, compiles your exact moving progress and pending tasks into a structured prompt you can paste into Gemini, Claude, or ChatGPT to ask for daily prioritization or Marketplace listing copy.
   - **Import JSON**: Allows any AI to return updated JSON that you can paste directly into the dashboard to update all lists automatically.
   - **Download Backup**: Save timestamped JSON backups to your computer or drive.

---

## 💻 How to View Locally

Simply double-click `index.html` to open it in any web browser, or launch a quick local server:

```bash
python3 -m http.server 8080
```
Then visit: `http://localhost:8080`

---

## 🌐 How to Host on GitHub Pages (Recommended)

1. Create a new repository on GitHub (e.g. `moving-app`).
2. Run these commands in this directory:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of moving command center"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```
3. In your GitHub repository:
   - Go to **Settings** ➔ **Pages**.
   - Under **Build and deployment**, select **Source: Deploy from a branch**.
   - Select Branch: `main` / `/ (root)` and click **Save**.
4. In under 60 seconds, your site is live at:
   `https://<your-username>.github.io/<your-repo-name>/`
   *(Bookmark it on your phone home screen for easy check-offs on the go!)*
