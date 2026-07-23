document.addEventListener('DOMContentLoaded', () => {
  const sortSelect = document.getElementById('sort-select');
  const container = document.getElementById('projects-container');

  if (!sortSelect || !container) return;

  sortSelect.addEventListener('change', () => {
    const sortBy = sortSelect.value;
    const cards = Array.from(container.querySelectorAll('.project-card'));

    cards.sort((a, b) => {
      if (sortBy === 'date') {
        // Sort by Date (newest to oldest)
        return new Date(b.dataset.date) - new Date(a.dataset.date);
      } else if (sortBy === 'pride') {
        // Sort by Pride rating (highest to lowest)
        return Number(b.dataset.pride) - Number(a.dataset.pride);
      }
    });

    // Re-append sorted cards back into container
    cards.forEach(card => container.appendChild(card));
  });

  // Run initial sort on page load
  sortSelect.dispatchEvent(new Event('change'));
});