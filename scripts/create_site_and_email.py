"""
Automated Blog Post Email Sender
Detects new blog posts, converts them to HTML emails, and sends to subscribers
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml


def parse_qmd_file(file_path):
    """Parse a Quarto markdown file and extract metadata and content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    yaml_match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
    if not yaml_match:
        return None
    
    yaml_content = yaml_match.group(1)
    markdown_content = yaml_match.group(2)
    
    # Parse YAML
    metadata = yaml.safe_load(yaml_content)
    
    return {
        'metadata': metadata,
        'content': markdown_content,
        'file_path': file_path
    }


def markdown_to_html(markdown_text):
    """Convert basic markdown to HTML for email"""
    html = markdown_text
    
    # Headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # Bold and italic
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Code blocks
    html = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Paragraphs
    paragraphs = html.split('\n\n')
    html = ''.join([f'<p>{p.strip()}</p>' if p.strip() and not p.strip().startswith('<') else p for p in paragraphs])
    
    return html


def get_new_or_modified_posts(posts_dir, hours_threshold=24):
    """Get posts that were created or modified in the last N hours"""
    posts = []
    posts_path = Path(posts_dir)
    
    # Get the threshold time
    threshold_time = datetime.now() - timedelta(hours=hours_threshold)
    
    # Iterate through all .qmd files in posts directory
    for qmd_file in posts_path.rglob('*.qmd'):
        # Skip metadata files
        if qmd_file.name == '_metadata.yml':
            continue
        
        # Check modification time
        mod_time = datetime.fromtimestamp(qmd_file.stat().st_mtime)
        
        if mod_time > threshold_time:
            post_data = parse_qmd_file(qmd_file)
            if post_data:
                posts.append(post_data)
    
    return posts


def create_email_html(post_data, site_url):
    """Create beautiful HTML email from post data"""
    metadata = post_data['metadata']
    content_html = markdown_to_html(post_data['content'])
    
    title = metadata.get('title', 'New Blog Post')
    author = metadata.get('author', 'Blog Author')
    date = metadata.get('date', '')
    categories = metadata.get('categories', [])
    
    # Get post URL (extract relative path from file_path)
    post_path = Path(post_data['file_path'])
    post_dir = post_path.parent.name
    post_url = f"{site_url}/posts/{post_dir}/"
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .email-container {{
                background-color: white;
                border-radius: 8px;
                padding: 30px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                font-size: 28px;
                margin-bottom: 10px;
                line-height: 1.3;
            }}
            .meta {{
                color: #7f8c8d;
                font-size: 14px;
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
            }}
            .categories {{
                margin-top: 10px;
            }}
            .category-tag {{
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-size: 12px;
                margin-right: 5px;
            }}
            .content {{
                margin: 20px 0;
            }}
            .content p {{
                margin: 15px 0;
            }}
            .content h2 {{
                color: #34495e;
                margin-top: 25px;
                margin-bottom: 15px;
            }}
            .content h3 {{
                color: #34495e;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            .content code {{
                background-color: #f8f9fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
            }}
            .content pre {{
                background-color: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            .content pre code {{
                background-color: transparent;
                color: #f8f8f2;
                padding: 0;
            }}
            .read-more {{
                display: inline-block;
                background-color: #3498db;
                color: white;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 5px;
                margin-top: 20px;
                font-weight: 500;
            }}
            .read-more:hover {{
                background-color: #2980b9;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                color: #7f8c8d;
                font-size: 12px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <h1>{title}</h1>
            <div class="meta">
                <div>By {author} • {date}</div>
                {f'<div class="categories">{"".join([f"<span class=\"category-tag\">{cat}</span>" for cat in categories])}</div>' if categories else ''}
            </div>
            <div class="content">
                {content_html}
            </div>
            <a href="{post_url}" class="read-more">Read Full Post on Website →</a>
            <div class="footer">
                <p>You're receiving this email because you subscribed to our blog.</p>
                <p><a href="{site_url}">Visit Website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


def send_email(to_emails, subject, html_content, smtp_config):
    """Send email using SMTP"""
    from_email = smtp_config['from_email']
    smtp_server = smtp_config['smtp_server']
    smtp_port = smtp_config['smtp_port']
    smtp_user = smtp_config['smtp_user']
    smtp_password = smtp_config['smtp_password']
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print(f"✓ Email sent successfully to {len(to_emails) if isinstance(to_emails, list) else 1} recipients")
            return True
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        return False


def load_email_list(file_path='scripts/email_list.json'):
    """Load email list from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('emails', [])
    except FileNotFoundError:
        print(f"Warning: Email list file not found at {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {file_path}")
        return []


def main():
    """Main function to orchestrate the email sending process"""
    print("=" * 60)
    print("Blog Post Email Sender")
    print("=" * 60)
    
    # Configuration
    POSTS_DIR = 'posts'
    HOURS_THRESHOLD = int(os.getenv('HOURS_THRESHOLD', '24'))  # Check posts from last 24 hours
    SITE_URL = os.getenv('SITE_URL', 'https://your-website-url.example.com')
    
    # SMTP Configuration from environment variables
    smtp_config = {
        'from_email': os.getenv('FROM_EMAIL'),
        'smtp_server': os.getenv('SMTP_SERVER'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'smtp_user': os.getenv('SMTP_USER'),
        'smtp_password': os.getenv('SMTP_PASSWORD')
    }
    
    # Validate SMTP configuration
    if not all([smtp_config['from_email'], smtp_config['smtp_server'], 
                smtp_config['smtp_user'], smtp_config['smtp_password']]):
        print("✗ Error: Missing SMTP configuration. Please set environment variables:")
        print("  - FROM_EMAIL")
        print("  - SMTP_SERVER")
        print("  - SMTP_PORT (optional, defaults to 587)")
        print("  - SMTP_USER")
        print("  - SMTP_PASSWORD")
        sys.exit(1)
    
    # Load email list
    email_list = load_email_list()
    if not email_list:
        print("✗ No email subscribers found. Add emails to scripts/email_list.json")
        print("\nExample format:")
        print(json.dumps({"emails": ["subscriber1@example.com", "subscriber2@example.com"]}, indent=2))
        sys.exit(1)
    
    print(f"\n📧 Found {len(email_list)} subscribers")
    
    # Get new/modified posts
    print(f"\n🔍 Checking for posts modified in the last {HOURS_THRESHOLD} hours...")
    new_posts = get_new_or_modified_posts(POSTS_DIR, HOURS_THRESHOLD)
    
    if not new_posts:
        print("✓ No new posts found. Nothing to send.")
        return
    
    print(f"\n📝 Found {len(new_posts)} new/modified post(s):")
    for post in new_posts:
        print(f"  - {post['metadata'].get('title', 'Untitled')}")
    
    # Send emails for each post
    print(f"\n📤 Sending emails...")
    for post in new_posts:
        title = post['metadata'].get('title', 'New Blog Post')
        print(f"\n  Processing: {title}")
        
        # Create email HTML
        email_html = create_email_html(post, SITE_URL)
        
        # Send to all subscribers
        subject = f"New Post: {title}"
        success = send_email(email_list, subject, email_html, smtp_config)
        
        if success:
            print(f"  ✓ Successfully sent email for '{title}'")
        else:
            print(f"  ✗ Failed to send email for '{title}'")
    
    print("\n" + "=" * 60)
    print("✓ Email sending process completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
