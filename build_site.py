import os
import re
import datetime
import urllib.parse
import pandas as pd

# Excel File Name
EXCEL_FILE = 'Portfolio main.xlsx'


def clean_val(val, default=""):
    """Safely cleans and stringifies dataframe values and fixes paths."""
    if pd.isna(val) or val is None:
        return default
    val_str = str(val).strip()
    if val_str.lower() == 'nan':
        return default
    
    # Strip unnecessary GitHub repository prefixes from local image paths
    val_str = re.sub(r'^(?:noahwalshsd/Portfolio/)+', '', val_str)
    return val_str


def encode_url_path(path):
    """Encodes spaces and special characters in local relative image paths."""
    if not path or path.startswith(('http://', 'https://')):
        return path
    # Quote path while preserving forward slashes
    return urllib.parse.quote(path, safe='/')


def format_text_block(text):
    """Formats project text blocks, bolding key sections and spacing them perfectly."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    formatted_paragraphs = []

    for p in lines:
        p_html = re.sub(
            r'^(Project summary:|Technologies used:|Process and challenges:|Results and impact:|Project title and summary:|Projectand summary:)', 
            r'<strong>\1</strong>', 
            p, 
            flags=re.IGNORECASE
        )
        formatted_paragraphs.append(f"          <p>{p_html}</p>")

    return "\n".join(formatted_paragraphs)


def format_work_text(text):
    """Formats work experience text into bullets or paragraphs."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    has_bullets = any(line.startswith('-') or line.startswith('•') for line in lines)
    
    if has_bullets:
        bullet_items = []
        for line in lines:
            cleaned_line = re.sub(r'^[-•]\s*', '', line)
            bullet_items.append(f"              <li>{cleaned_line}</li>")
        bullets_html = "\n".join(bullet_items)
        return f'<ul class="bullet-list">\n{bullets_html}\n            </ul>'
    else:
        p_items = [f"<p>{line}</p>" for line in lines]
        return "\n            ".join(p_items)


def extract_youtube_id(url):
    """Extracts YouTube video ID from various YouTube URL formats."""
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def get_media_element(url, caption=""):
    """Determines whether a link is a YouTube video or an Image and returns HTML dict."""
    url = clean_val(url)
    caption = clean_val(caption)
    
    if not url:
        return None

    caption_html = f'<p class="media-caption">{caption}</p>' if caption else ''

    # Handle YouTube Videos
    if "youtube.com" in url or "youtu.be" in url:
        video_id = extract_youtube_id(url)
        embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else url

        return {
            "type": "video",
            "html": f"""<div class="media-main">
            <iframe src="{embed_url}" title="Project Video" allowfullscreen></iframe>
            {caption_html}
          </div>"""
        }
    
    # Handle Images
    else:
        encoded_url = encode_url_path(url)
        return {
            "type": "image",
            "html": f"""<div class="media-main">
            <img src="{encoded_url}" alt="Project Media">
            {caption_html}
          </div>"""
        }


def render_project_media_layout(media_items):
    """Renders clean responsive grid layouts for media items."""
    if not media_items:
        return ""
    
    if len(media_items) == 1:
        return f"""        <div class="media-layout single">
{media_items[0]['html']}
        </div>\n"""
    
    combined_media = "\n".join([item['html'] for item in media_items])
    return f"""        <div class="media-grid-2x2">
{combined_media}
        </div>\n"""


def build_index_html(df_bio, df_main):
    """Generates index.html dynamically using 'bio' and 'main' or 'work' tabs."""
    bio_row = df_bio.iloc[0] if not df_bio.empty else {}
    name = clean_val(bio_row.get('Name'), 'Noah Walsh')
    age = clean_val(bio_row.get('Age'), '17')
    img_addr = encode_url_path(clean_val(bio_row.get('img1 address'), 'images/me.png'))
    img_caption = clean_val(bio_row.get('img1 caption'))
    education = clean_val(bio_row.get('Education'), 'Senior at Scripps Ranch High School')
    w_gpa = clean_val(bio_row.get('W_GPA'), '4.48')
    uw_gpa = clean_val(bio_row.get('UW_GPA'), '3.95')
    focus = clean_val(bio_row.get('Focus'), 'Mechanical Engineering')
    linkedin = clean_val(bio_row.get('Linkedin'), '#')
    bio_text = clean_val(bio_row.get('Text'), 'High school senior with a passion for robotics, embedded systems, and rapid prototyping.')

    bio_caption_html = f'<p class="media-caption">{img_caption}</p>' if img_caption else ''
    
    bio_card_html = f"""    <section class="card showcase-card">
      <div class="card-media">
        <img src="{img_addr}" alt="{name}" class="profile-photo-uncut">
        {bio_caption_html}
      </div>

      <div class="card-content">
        <span class="badge">BIOGRAPHY</span>
        <h2 class="card-heading">{name} — {age} years old</h2>
        
        <div class="bio-stats">
          <div class="stat-item">
            <span class="stat-label">Education</span>
            <span class="stat-value">{education}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Academics</span>
            <span class="stat-value">{w_gpa} WGPA | {uw_gpa} UW</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Focus</span>
            <span class="stat-value">{focus}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">LinkedIn</span>
            <span class="stat-value"><a href="{linkedin}" target="_blank" style="color: var(--accent-silver); text-decoration: underline;">Profile Link</a></span>
          </div>
        </div>

        <div class="card-text">
          <p>{bio_text}</p>
        </div>
      </div>
    </section>"""

    work_cards_html = ""
    
    if 'Order' in df_main.columns:
        df_main['Order'] = pd.to_numeric(df_main['Order'], errors='coerce').fillna(99)
        df_main = df_main.sort_values('Order')

    for _, row in df_main.iterrows():
        title = clean_val(row.get('Title'))
        if not title:
            continue
            
        category = clean_val(row.get('Category'), 'EXPERIENCE').upper()
        role = clean_val(row.get('Role'))
        logo_addr = encode_url_path(clean_val(row.get('Img1 address')))
        text_body = format_work_text(clean_val(row.get('Text')))

        role_markup = f'<p class="role-title">{role}</p>\n' if role else ''

        card = f"""      <article class="card work-card">
        <div class="card-media">
          <img src="{logo_addr}" alt="{title}" class="logo-uncut">
        </div>
        <div class="card-content">
          <span class="badge">{category}</span>
          <h3 class="card-heading">{title}</h3>
          {role_markup}          <div class="card-text">
            {text_body}
          </div>
        </div>
      </article>"""

        work_cards_html += card + "\n\n"

    full_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name} - Bio & Work</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <nav class="navbar">
    <div class="logo">{name.upper()}</div>
    <ul class="nav-links">
      <li><a href="index.html" class="active">Bio & Work</a></li>
      <li><a href="projects.html">Projects</a></li>
    </ul>
  </nav>

  <header class="hero-section">
    <p class="hero-subtitle">ENGINEERING & ROBOTICS PORTFOLIO</p>
    <h1 class="hero-title">Overview</h1>
  </header>

  <main class="container">

{bio_card_html}

    <div class="section-divider">
      <h2>Work & Leadership Experience</h2>
    </div>

    <div class="experience-grid">

{work_cards_html.rstrip()}

    </div>

  </main>

  <footer class="site-footer">
    <p>© 2026 {name}.</p>
  </footer>

</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_index)
    print("✓ Successfully generated index.html")


def build_projects_html(df_projects, author_name="Noah Walsh"):
    """Generates projects.html from the 'projects' tab."""
    project_cards_html = ""

    if 'Pride Rank (1 = Highest)' in df_projects.columns:
        df_projects['Pride Rank (1 = Highest)'] = pd.to_numeric(df_projects['Pride Rank (1 = Highest)'], errors='coerce').fillna(99)

    for _, row in df_projects.iterrows():
        title = clean_val(row.get('Title'))
        if not title:
            continue

        raw_date = row.get('Creation Date', '')
        if isinstance(raw_date, (pd.Timestamp, datetime.date)):
            date_str = raw_date.strftime('%Y-%m-%d')
        else:
            date_str = clean_val(raw_date, "2025-01-01")

        pride_rank = clean_val(row.get('Pride Rank (1 = Highest)'), '99')
        github_url = clean_val(row.get('Github')).replace('Github URL:', '').strip()
        domain = clean_val(row.get('Domain'), 'PROJECT').upper()
        subtitle = clean_val(row.get('Subtitle'))
        disciplines = clean_val(row.get('Disciplines'))
        main_text = clean_val(row.get('Main Text'))

        media_items = []
        for i in range(1, 5):
            addr_col = f'Vid or photo address {i}'
            cap_col = f'Vid or photo caption {i}'
            item = get_media_element(row.get(addr_col, ''), row.get(cap_col, ''))
            if item:
                media_items.append(item)

        media_layout_html = render_project_media_layout(media_items)

        sub_header = f'        <h3 class="project-header-2"><em>{subtitle}</em></h3>\n' if subtitle else ''
        github_markup = f'        <p class="github-link">Github: <a href="{github_url}" target="_blank">{github_url}</a></p>\n' if github_url else ''
        formatted_body = format_text_block(main_text)

        card = f"""      <article class="card project-card" data-date="{date_str}" data-pride="{pride_rank}">
{media_layout_html}        <span class="badge">{domain}</span>
        <h2 class="project-header-1">{title}</h2>
{sub_header}        <h4 class="project-header-3">{disciplines}</h4>
{github_markup}
        <div class="project-body">
{formatted_body}
        </div>
      </article>"""

        project_cards_html += card + "\n\n"

    full_projects = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{author_name} - Projects</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <nav class="navbar">
    <div class="logo">{author_name.upper()}</div>
    <ul class="nav-links">
      <li><a href="index.html">Bio & Work</a></li>
      <li><a href="projects.html" class="active">Projects</a></li>
    </ul>
  </nav>

  <header class="hero-section">
    <p class="hero-subtitle">ENGINEERING & ROBOTICS PORTFOLIO</p>
    <h1 class="hero-title">Featured Projects</h1>
  </header>

  <main class="container">

    <div class="controls">
      <label for="sort-select">Sort projects by: </label>
      <select id="sort-select">
        <option value="pride">Pride Level (Highest First)</option>
        <option value="date">Creation Date (Newest First)</option>
      </select>
    </div>

    <div id="projects-container" class="projects-grid">
{project_cards_html.rstrip()}
    </div>
  </main>

  <footer class="site-footer">
    <p>© 2026 {author_name}.</p>
  </footer>

  <script src="script.js"></script>
</body>
</html>"""

    with open('projects.html', 'w', encoding='utf-8') as f:
        f.write(full_projects)
    print("✓ Successfully generated projects.html")


def main():
    target_file = EXCEL_FILE
    if not os.path.exists(target_file):
        for f in os.listdir('.'):
            if f.lower() == 'portfolio main.xlsx':
                target_file = f
                break

    try:
        xls = pd.ExcelFile(target_file)
        
        df_bio = pd.DataFrame()
        df_main = pd.DataFrame()
        df_projects = pd.DataFrame()

        for sheet_name in xls.sheet_names:
            s_clean = sheet_name.strip().lower()
            temp_df = pd.read_excel(xls, sheet_name=sheet_name)
            temp_df.columns = temp_df.columns.str.strip()

            if s_clean == 'bio':
                df_bio = temp_df
            elif s_clean in ['main', 'work']:
                df_main = temp_df
            elif s_clean == 'projects':
                df_projects = temp_df

        author_name = "Noah Walsh"
        if not df_bio.empty and 'Name' in df_bio.columns:
            author_name = clean_val(df_bio.iloc[0].get('Name'), "Noah Walsh")

        build_index_html(df_bio, df_main)
        
        if not df_projects.empty:
            build_projects_html(df_projects, author_name)

    except FileNotFoundError:
        print(f"Error: Could not find '{EXCEL_FILE}' in this directory.")
    except Exception as e:
        print(f"An error occurred while building the site: {e}")


if __name__ == "__main__":
    main()