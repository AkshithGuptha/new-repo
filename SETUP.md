# Valentine's Day Proposal Setup

## Requirements

1. **Gmail Account** - You need a Gmail account to receive notifications
2. **App Password** - Generate an app-specific password from Gmail

## Setup Steps

### 1. Generate Gmail App Password
- Go to: https://myaccount.google.com/apppasswords
- Select "Mail" and "Windows Computer"
- Copy the generated 16-character password

### 2. Update .env File
Edit `.env` file in the project root:
```
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-16-char-app-password
PORT=3001
```

### 3. Install Dependencies
```bash
npm install
```

### 4. Run Both Server and Frontend

**Option A - Run Separately (Recommended for development):**
```bash
# Terminal 1 - Start the backend server
npm run server

# Terminal 2 - Start the frontend (in another terminal)
npm run dev
```

**Option B - Run Together:**
```bash
npm run dev:all
```

### 5. Share the Link
Once running, open http://localhost:5173 in your browser and send the link to your friend.

## How It Works

1. When Anvitha clicks "Yes", it sends a notification to your email
2. You'll receive an email with the timestamp
3. The "No" button keeps moving away when clicked/hovered

## Important Notes

⚠️ **Keep your .env file private** - Never commit it to GitHub!
- The .gitignore already includes .env files
- Only share the code, not your email credentials

## Troubleshooting

**Email not received?**
- Check spam folder
- Verify your Gmail app password is correct
- Make sure you allowed "Less secure apps" access (if using regular password instead of app password)

**Connection error?**
- Make sure server is running on port 3001
- Check if port 3001 is already in use
