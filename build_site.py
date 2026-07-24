import pandas as pd
import datetime
import re

EXCEL_FILE = 'Portfolio main.xlsx'

def format_text_block(text):
    """Formats text paragraphs, automatically bolding key section headers."""
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Split text blocks separated by double line breaks
    paragraphs = [p.strip() for p in text.strip().split('\n\n') if p.strip()]
    formatted_paragraphs = []

    for p in paragraphs:
        # Automatically bold common section titles if present
        p_html = re.sub(
            r'^(Project summary:|Technologies used:|Process and challenges:|Results and impact:|Project title and summary:|Projectand summary:)', 
            r'<strong>\1</strong>', 
            p
        )
        # Convert single newlines inside paragraph to break tags
        p_html = p_html.replace('\n', '<br>')
        formatted_paragraphs.append(f"          <p>{p_html}</p>")

    return "\n".join(formatted_paragraphs)


def build_index_html(df_main):
    """Generates index.html from the main tab."""
    bio_cards_html = ""

    for idx, row in df_main.iterrows():
        img_url = str(row.get('Image address', '')).strip()
        title = str(row.get('Title', '')).strip()
        raw_text = str(row.get('Text', '')).strip()
        row_type = str(row.get('Number / type', '')).lower()

        # Format lines inside the bio box
        text_lines = [f'<p class="bio-line">{line.strip()}</p>' for line in raw_text.split('\n') if line.strip()]
        formatted_lines_html = "\n          ".join(text_lines)

        # Distinguish between Bio card and Work experience cards
        if 'bio' in row_type or idx == 0:
            card = f"""    <section class="bio-card">
      <div class="bio-left">
        <img src="{img_url}" alt="{title}" class="profile-photo">
        <p class="photo-caption">Noah Walsh Portfolio</p>
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
        # Date handling
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

        # Split title/subtitle if separated by semicolon
        title_parts = title.split(';')
        main_header = title_parts[0].strip()
        sub_header = f'        <h3 class="project-header-2"><em>{title_parts[1].strip()}</em></h3>\n' if len(title_parts) > 1 else ''

        # GitHub URL markup
        github_markup = f'        <p class="github-link">Github URL: <a href="{github_url}" target="_blank">{github_url}</a></p>\n' if github_url and github_url.lower() != 'nan' else ''

        # Formatted main text
        formatted_body = format_text_block(main_text)

        card = f"""      <article class="project-card" data-date="{date_str}" data-pride="{pride_rank}">
{github_markup}        <h2 class="project-header-1">{main_header}</h2>
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
        
        # Load sheets (fallback to sheet index if tab names vary slightly)
        df_projects = pd.read_excel(xls, sheet_name=0 if len(xls.sheet_names) == 1 else 0)
        df_main = pd.read_excel(xls, sheet_name=1 if len(xls.sheet_names) > 1 else 0)

        # Detect sheets by content if needed
        for sheet in xls.sheet_names:
            temp_df = pd.read_excel(xls, sheet_name=sheet)
            temp_df.columns = temp_df.columns.str.strip()
            if 'Disciplines' in temp_df.columns or 'Main Text' in temp_df.columns:
                df_projects = temp_df
            elif 'Number / type' in temp_df.columns or 'Image address' in temp_df.columns:
                df_main = temp_df

        build_index_html(df_main)
        build_projects_html(df_projects)

    except FileNotFoundError:
        print(f"Error: Could not find '{EXCEL_FILE}' in this directory.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()