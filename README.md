# Alex's Blog

Automated blog with email notifications powered by Quarto and GitHub Actions.

## 🚀 Features

- **Obsidian Integration**: Write posts in Obsidian, push to GitHub
- **Automatic Email Sending**: New posts automatically sent to subscribers via email
- **GitHub Actions**: Fully automated workflow runs on every push
- **Beautiful HTML Emails**: Professional email templates with responsive design

## 📧 Setup Email Automation

### 1. Add Email Subscribers

Edit `scripts/email_list.json` and add your subscribers:

```json
{
  "emails": [
    "subscriber1@example.com",
    "subscriber2@example.com"
  ]
}
```

### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `FROM_EMAIL` | Your sender email address | `blog@yourdomain.com` |
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (usually 587) | `587` |
| `SMTP_USER` | SMTP username (usually your email) | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password or app password | `your-app-password` |
| `SITE_URL` | Your blog URL | `https://yourblog.com` |

### 3. SMTP Provider Options

#### Gmail
- SMTP Server: `smtp.gmail.com`
- Port: `587`
- **Important**: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password
- Enable 2FA and generate app password at: https://myaccount.google.com/apppasswords

#### SendGrid
- SMTP Server: `smtp.sendgrid.net`
- Port: `587`
- Username: `apikey`
- Password: Your SendGrid API key

#### Mailgun
- SMTP Server: `smtp.mailgun.org`
- Port: `587`
- Username: Your Mailgun SMTP username
- Password: Your Mailgun SMTP password

#### Other Providers
- Outlook/Office365: `smtp.office365.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`
- Custom SMTP: Use your provider's settings

## 📝 How It Works

1. **Write in Obsidian**: Create a new post in the `posts/` directory with `.qmd` format
2. **Push to GitHub**: Commit and push your changes
3. **GitHub Actions Triggers**: Automatically runs when `.qmd` files in `posts/` are modified
4. **Email Sent**: Script detects new posts and sends beautiful HTML emails to all subscribers

## 🧪 Testing Locally

Run the email script locally to test:

```bash
# Set environment variables
export FROM_EMAIL="your-email@gmail.com"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
export SMTP_USER="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
export SITE_URL="https://yourblog.com"
export HOURS_THRESHOLD="24"

# Run the script
python scripts/create_site_and_email.py
```

On Windows PowerShell:

```powershell
$env:FROM_EMAIL="your-email@gmail.com"
$env:SMTP_SERVER="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="your-email@gmail.com"
$env:SMTP_PASSWORD="your-app-password"
$env:SITE_URL="https://yourblog.com"
$env:HOURS_THRESHOLD="24"

python scripts/create_site_and_email.py
```

## 📂 Project Structure

```
AlexBlog/
├── posts/               # Blog posts directory
│   ├── post-with-code/
│   │   └── index.qmd   # Individual post files
│   └── welcome/
│       └── index.qmd
├── scripts/
│   ├── create_site_and_email.py  # Main automation script
│   └── email_list.json           # Subscriber emails
├── .github/
│   └── workflows/
│       └── send-blog-emails.yml  # GitHub Actions workflow
├── _quarto.yml         # Quarto configuration
└── README.md
```

## 🎨 Customizing Email Templates

Edit the `create_email_html()` function in `scripts/create_site_and_email.py` to customize:
- Email styling (colors, fonts, layout)
- Header/footer content
- Call-to-action buttons
- Branding elements

## 🔧 Configuration Options

### Time Threshold
By default, the script checks for posts modified in the last 48 hours. Adjust in `.github/workflows/send-blog-emails.yml`:

```yaml
env:
  HOURS_THRESHOLD: "48"  # Change this value
```

### Manual Trigger
You can manually trigger the email workflow from GitHub:
1. Go to Actions tab
2. Select "Send Blog Post Emails"
3. Click "Run workflow"

## 📚 Post Format

Posts should be in Quarto markdown format (`.qmd`) with YAML frontmatter:

```markdown
---
title: "Your Post Title"
author: "Your Name"
date: "2025-12-16"
categories: [news, tutorial, code]
image: "featured-image.jpg"
---

Your post content here...

## Section heading

Content with **bold** and *italic* text.
```

## 🐛 Troubleshooting

### Emails not sending?
1. Check GitHub Actions logs in the "Actions" tab
2. Verify all secrets are set correctly
3. Ensure SMTP credentials are valid
4. Check if your SMTP provider requires app passwords

### No new posts detected?
1. Ensure you're modifying `.qmd` files in the `posts/` directory
2. Check the `HOURS_THRESHOLD` setting
3. Verify files were actually modified (not just touched)

### Testing failed?
Run locally first with the test commands above to debug before pushing to GitHub.

## 📄 License

MIT License - Feel free to use and modify!
