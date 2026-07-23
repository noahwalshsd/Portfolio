import pandas as pd
import datetime

# File name of your Excel portfolio
EXCEL_FILE = 'Portfolio main.xlsx'

def generate_projects_page():
    try:
        # Load the Excel file
        df = pd.read_excel(EXCEL_FILE)
        df.columns = df.columns.str.strip()  # Clean up extra spaces in header names

        cards_html = ""

        # Loop through each row in your Excel sheet
        for _, row in df.iterrows():
            # Format Date
            raw_date = row.get('Creation Date', '')
            if isinstance(raw_date, (pd.Timestamp, datetime.date)):
                date_str = raw_date.strftime('%Y-%m-%d')
            else:
                date_str = str(raw_date).strip() if pd.notna(raw_date) else "2025-01-01"

            # Extract fields with fallbacks
            pride_rank = str(row.get('Pride Rank (1 = Highest)', 99)).strip()
            title = str(row.get('Title', '')).strip()
            disciplines = str(row.get('Disciplines', '')).strip()
            main_text = str(row.get('Main Text', '')).strip()

            # Skip empty rows
            if not title or title.lower() == 'nan':
                continue

            # Build HTML string for individual project card
            card = f"""
      <article class="project-card" data-date="{date_str}" data-pride="{pride_rank}">
        <h2 class="project-header-1">{title}</h2>
        <h4 class="project-header-3">{disciplines}</h4>

        <div class="project-body">
          <p>{main_text}</p>
        </div>
      </article>"""
            
            cards_html += card

        # Full HTML structure for projects.html
        full_html = f"""<!DOCTYPE html>
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
{cards_html}
    </div>
  </main>

  <script src="script.js"></script>
</body>
</html>"""

        # Overwrite projects.html with updated content
        with open('projects.html', 'w', encoding='utf-8') as f:
            f.write(full_html)

        print("Successfully generated projects.html from Portfolio main.xlsx!")

    except Exception as e:
        print(f"Error generating projects page: {e}")

if __name__ == "__main__":
    generate_projects_page()