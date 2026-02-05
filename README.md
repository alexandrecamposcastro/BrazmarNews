# Brazmar News

A self-updating news platform that bridges Python automation with a Node.js backend. This project utilizes an AI-driven engine to process data and a decoupled frontend structure deployed on Vercel.

## ⚙️ How it Works

1. **Intelligence Layer:** The `bot.py` script fetches and processes news data using AI models (managed via `.env`).
2. **Automation:** **GitHub Actions** runs the Python engine on a schedule.
3. **Deployment:** The bot updates files within the `public/` directory and commits them. Vercel then automatically deploys the latest version.
4. **Backend:** A Node.js API (`api/index.js`) handles serverless logic and data delivery.

## 🛠 Tech Stack

* **Automation/AI:** Python 3.x
* **Backend:** Node.js (Vercel Serverless Functions)
* **CI/CD:** GitHub Actions
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
* **Hosting:** Vercel

## 📁 Project Structure

* **`api/index.js`**: Serverless function serving the backend API.
* **`public/`**: The core frontend application.
    * `index.html`: Main entry point for the news portal.
    * `styles.css`: Custom stylesheets for the visual interface.
    * `script.js`: Client-side logic for dynamic content rendering.
    * `noticias.json`: The database file updated by the Python bot.
    * `images/`: Static assets and processed media.
* **`bot.py`**: Python script responsible for news aggregation and AI integration.
* **`.github/workflows/`**: Automation pipelines for content updates and code revision.
* **`vercel.json`**: Routing and deployment configuration.
