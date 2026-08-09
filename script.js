document.addEventListener('DOMContentLoaded', () => {
  const sortSelect = document.getElementById('sort-select');
  const projectsContainer = document.getElementById('projects-container');

  if (!sortSelect || !projectsContainer) return;

  function sortProjects() {
    const value = sortSelect.value;
    const cards = Array.from(projectsContainer.querySelectorAll('.project-card'));

    cards.sort((a, b) => {
      if (value === 'pride') {
        const prideA = parseInt(a.getAttribute('data-pride') || '99', 10);
        const prideB = parseInt(b.getAttribute('data-pride') || '99', 10);
        return prideA - prideB;
      } else if (value === 'date') {
        const dateA = new Date(a.getAttribute('data-date') || '1970-01-01');
        const dateB = new Date(b.getAttribute('data-date') || '1970-01-01');
        return dateB - dateA;
      }
      return 0;
    });

    cards.forEach(card => projectsContainer.appendChild(card));
  }

  sortSelect.addEventListener('change', sortProjects);
  sortProjects();
});