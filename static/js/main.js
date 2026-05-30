(function () {
    const html = document.documentElement;
    const toggle = document.getElementById('themeToggle');
    const saved = localStorage.getItem('ishiki-theme') || 'dark';
    html.setAttribute('data-bs-theme', saved);
    if (toggle) {
        toggle.addEventListener('click', () => {
            const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('ishiki-theme', next);
        });
    }
})();
