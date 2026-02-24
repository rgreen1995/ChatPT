# ChatPT Deployment Guide

## 🚀 Quick Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account
- At least one LLM API key (OpenAI, Anthropic, or Gemini)

### Steps

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/ChatPT.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Select your repository
   - Main file: `app.py`
   - Click "Deploy"

3. **Add Secrets (API Keys):**
   - In app settings, click "Secrets"
   - Add your API keys:
     ```toml
     OPENAI_API_KEY = "sk-..."
     ANTHROPIC_API_KEY = "sk-ant-..."
     GEMINI_API_KEY = "..."
     ```

4. **Access on Mobile:**
   - Open the provided URL in your phone browser
   - Click "Share" → "Add to Home Screen" for app-like experience

---

## 📱 Local Network Access (Development)

Run on your computer and access from phone:

```bash
# Find your local IP address
ipconfig  # Windows
ifconfig  # Mac/Linux

# Run with network access
poetry run streamlit run app.py --server.address 0.0.0.0 --server.port 8501

# Access from phone browser at:
# http://YOUR_LOCAL_IP:8501
```

---

## 🔧 Alternative Deployments

### Railway
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### Render
1. Connect GitHub repo to https://render.com
2. Create "Web Service"
3. Add environment variables
4. Deploy

### Docker (Advanced)
```bash
docker build -t chatpt .
docker run -p 8501:8501 --env-file .env chatpt
```

---

## 🔒 Security Notes

- Never commit `.env` files or API keys to GitHub
- Use secrets management in production
- Consider adding authentication for public deployments

---

## 📊 Database Persistence

The SQLite database is stored locally. For production:
- Use environment-based storage
- Consider PostgreSQL for multi-user deployments
- Backup regularly

---

## 🐛 Troubleshooting

**Issue: API keys not working**
- Ensure keys are in Streamlit secrets (not .env)
- Check key format matches provider requirements

**Issue: App is slow**
- Free tier has resource limits
- Consider upgrading Streamlit Cloud plan

**Issue: Database resets on deploy**
- Expected behavior - SQLite is ephemeral on Streamlit Cloud
- Use persistent storage or cloud database for production
