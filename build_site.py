import pandas as pd
import datetime
import re

EXCEL_FILE = 'Portfolio main.xlsx'

def format_text_block(text):
    """Formats text paragraphs, automatically bolding key section headers."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    paragraphs = [p.strip() for p in text.strip().split('\n\n') if p.strip()]
    formatted_paragraphs = []

    for p in paragraphs:
        p_html = re.sub(
            r'^(Project summary:|Technologies used:|Process and challenges:|Results and impact:|Project title and summary:|Projectand summary:)', 
            r'<strong>\1</strong>', 
            p
        )
        p_html = p_html.replace('\n', '<br>')
        formatted_paragraphs.append(f"          <p>{p_html}</p>")

    return "\n".join(formatted_paragraphs)


def get_media_element(url, caption=""):
    """Determines whether a link is a YouTube video or an Image and returns proper HTML."""
    if not isinstance(url, str) or not url.strip() or url.strip().lower() == 'nan':
        return ""

    url = url.strip()
    caption_html = f'<p class="media-caption">{caption.strip()}</p>' if isinstance(caption, str) and caption.strip() and caption.strip().lower() != 'nan' else ''

    # Handle YouTube Videos
    if "youtube.com" in url or "youtu.be" in url:
        # Convert youtube watch URL to embed URL
        video_id = ""
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        
        embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else url

        return f"""
          <div class="media-main">
            <iframe src="{embed_url}" title="Project Video" allowfullscreen></iframe>
            {caption_html}
          </div>"""
    
    # Handle Images
    else:
        return f"""
          <div class="media-main">
            <img src="{url}" alt="Project Media">
            {caption_html}
          </div>"""


def build_index_html(df_main):
    """Generates index.html from the main tab."""
    bio_cards_html = ""

    for idx, row in df_main.iterrows():
        img_url = str(row.get('Img1 address', '')).strip()
        img_caption = str(row.get('Img1 caption', '')).strip()
        title = str(row.get('Title', '')).strip()
        raw_text = str(row.get('Text', '')).strip()
        row_type = str(row.get('Number / type', '')).lower()

        caption_html = f'<p class="photo-caption">{img_caption}</p>' if img_caption and img_caption.lower() != 'nan' else ''

        # Clean text lines
        raw_text = raw_text.strip('"')
        text_lines = [f'<p class="bio-line">{line.strip()}</p>' for line in raw_text.split('\n') if line.strip()]
        formatted_lines_html = "\n          ".join(text_lines)

        if 'bio' in row_type or idx == 0:
            card = f"""    <section class="bio-card">
      <div class="bio-left">
        <img src="{img_url}" alt="{title}" class="profile-photo">
        {caption_html}
      </div>
      <div class="bio-right">
        <h1 class="bio-title">{title}</h1>
        <div class="bio-text">
          {formatted_lines_html}
        </div>
      </div>
    </section>"""
        else:
            card = f"""    <section class="bio-card">
      <div class="bio-left">
        <img src="{img_url}" alt="{title}" class="company-logo clean-logo">
      </div>
      <div class="bio-right">
        <h2 class="job-title">{title}</h2>
        <div class="bio-text">
          {formatted_lines_html}
        </div>
      </div>
    </section>"""
        
        bio_cards_html += card + "\n\n"

    full_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Noah Walsh - Bio & Work</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Gentium+Basic:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <nav class="navbar">
    <div class="logo">Noah Walsh</div>
    <ul class="nav-links">
      <li><a href="index.html" class="active">Bio & Work</a></li>
      <li><a href="projects.html">Projects</a></li>
    </ul>
  </nav>

  <main class="container">
{bio_cards_html.rstrip()}
  </main>

</body>
</html>"""

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_index)
    print("✓ Successfully generated index.html")


def build_projects_html(df_projects):
    """Generates projects.html from the projects tab."""
    project_cards_html = ""

    for _, row in df_projects.iterrows():
        # Date parsing
        raw_date = row.get('Creation Date', '')
        if isinstance(raw_date, (pd.Timestamp, datetime.date)):
            date_str = raw_date.strftime('%Y-%m-%d')
        else:
            date_str = str(raw_date).strip() if pd.notna(raw_date) else "2025-01-01"

        pride_rank = str(row.get('Pride Rank (1 = Highest)', 99)).strip()
        github_url = str(row.get('Github', '')).replace('Github URL:', '').strip()
        title = str(row.get('Title', '')).strip()
        disciplines = str(row.get('Disciplines', '')).strip()
        main_text = str(row.get('Main Text', '')).strip()

        if not title or title.lower() == 'nan':
            continue

        # Extract Media slots 1 to 4 and Captions 1 to 4
        media_html_items = []
        for i in range(1, 5):
            addr_col = f'Vid or photo address {i}'
            cap_col = f'Vid or photo caption {i}'
            media_item = get_media_element(row.get(addr_col, ''), row.get(cap_col, ''))
            if media_item:
                media_html_items.append(media_item)

        media_layout_html = ""
        if media_html_items:
            combined_media = "\n".join(media_html_items)
            media_layout_html = f"""        <div class="media-layout">
{combined_media}
        </div>\n"""

        # Title formatting
        title_parts = title.split(';')
        main_header = title_parts[0].strip()
        sub_header = f'        <h3 class="project-header-2"><em>{title_parts[1].strip()}</em></h3>\n' if len(title_parts) > 1 else ''

        # Github link formatting
        github_markup = f'        <p class="github-link">Github URL: <a href="{github_url}" target="_blank">{github_url}</a></p>\n' if github_url and github_url.lower() != 'nan' else ''

        formatted_body = format_text_block(main_text)

        card = f"""      <article class="project-card" data-date="{date_str}" data-pride="{pride_rank}">
{media_layout_html}{github_markup}        <h2 class="project-header-1">{main_header}</h2>
{sub_header}        <h4 class="project-header-3">{disciplines}</h4>

        <div class="project-body">
{formatted_body}
        </div>
      </article>"""

        project_cards_html += card + "\n\n"

    full_projects = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Noah Walsh - Projects</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Gentium+Basic:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>

  <nav class="navbar">
    <div class="logo">Noah Walsh</div>
    <ul class="nav-links">
      <li><a href="index.html">Bio & Work</a></li>
      <li><a href="projects.html" class="active">Projects</a></li>
    </ul>
  </nav>

  <main class="container">
    <h1>Projects</h1>

    <div class="controls">
      <label for="sort-select">Sort projects by:</label>
      <select id="sort-select">
        <option value="pride">Pride Level (Highest/Rank 1 First)</option>
        <option value="date">Creation Date (Newest First)</option>
      </select>
    </div>

    <div id="projects-container" class="projects-grid">
{project_cards_html.rstrip()}
    </div>
  </main>

  <script src="script.js"></script>
</body>
</html>"""

    with open('projects.html', 'w', encoding='utf-8') as f:
        f.write(full_projects)
    print("✓ Successfully generated projects.html")


def main():
    try:
        xls = pd.ExcelFile(EXCEL_FILE)
        
        df_projects = None
        df_main = None

        # Automatically identify sheets by column headers
        for sheet in xls.sheet_names:
            temp_df = pd.read_excel(xls, sheet_name=sheet)
            temp_df.columns = temp_df.columns.str.strip()
            if 'Disciplines' in temp_df.columns or 'Main Text' in temp_df.columns:
                df_projects = temp_df
            elif 'Number / type' in temp_df.columns or 'Img1 address' in temp_df.columns:
                df_main = temp_df

        if df_main is not None:
            build_index_html(df_main)
        if df_projects is not None:
            build_projects_html(df_projects)

    except FileNotFoundError:
        print(f"Error: Could not find '{EXCEL_FILE}' in this directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()