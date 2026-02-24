# 📱 Accessing ChatPT on Your Phone

## Option 1: Quick Test (Same WiFi) - 5 minutes

1. **On your computer, find your IP address:**
   - Windows: Open Command Prompt → type `ipconfig` → look for "IPv4 Address"
   - Mac: System Preferences → Network → look for IP address
   - Linux: type `ifconfig` or `ip addr`

2. **Start the app with network access:**
   ```bash
   streamlit run app.py --server.address 0.0.0.0 --server.port 8501
   ```

3. **On your phone:**
   - Connect to the same WiFi
   - Open browser
   - Go to: `http://YOUR_IP:8501` (e.g., `http://192.168.1.100:8501`)

✅ **Pros:** Works immediately, private  
❌ **Cons:** Only works on same WiFi, computer must stay on

---

## Option 2: Deploy Online (Anywhere Access) - 15 minutes

### Deploy to Streamlit Cloud (FREE):

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Deploy ChatPT"
   git remote add origin https://github.com/YOUR_USERNAME/ChatPT.git
   git push -u origin main
   ```

2. **Deploy:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your ChatPT repository
   - Main file: `app.py`
   - Click "Deploy" (takes ~5 min)

3. **Add your API keys:**
   - In the app dashboard, click "⚙️ Settings"
   - Click "Secrets"
   - Paste:
     ```toml
     ANTHROPIC_API_KEY = "your-key-here"
     ```

4. **Access on phone:**
   - You get a URL like: `https://chatpt-yourname.streamlit.app`
   - Open in mobile browser
   - Tap "Share" → "Add to Home Screen"
   - Now it works like a native app!

✅ **Pros:** Access from anywhere, works offline after loading, free  
❌ **Cons:** Public URL (shareable), database resets on redeploy

---

## Making It Feel Like a Native App

### On iPhone:
1. Open your ChatPT URL in Safari
2. Tap the Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Name it "ChatPT" and tap "Add"

### On Android:
1. Open your ChatPT URL in Chrome
2. Tap the menu (⋮)
3. Tap "Add to Home screen"
4. Name it "ChatPT" and tap "Add"

Now you have a ChatPT icon on your home screen! 🎉

---

## Tips for Mobile Use

- **Portrait mode works best** for the chat interface
- **Sidebar collapsed by default** - tap menu (☰) to access settings
- **Add to home screen** for fastest access
- **Works offline** once loaded (until you navigate away)

---

## Need Help?

- Deployment not working? Check `DEPLOYMENT.md`
- API issues? Verify your keys in secrets
- Can't connect locally? Make sure firewall allows port 8501
