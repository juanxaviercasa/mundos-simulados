/* Theme preference is local to this browser; no tracking or network requests. */
(() => {
  const key = 'ms-theme';
  const root = document.documentElement;
  root.dataset.msClient = 'true';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(key); } catch { /* Storage may be disabled. */ }
  if (!['light', 'dark'].includes(preference)) preference = null;
  const apply = theme => {
    root.dataset.msTheme = theme;
    root.style.colorScheme = theme;
    document.querySelectorAll('.ms-theme-toggle').forEach(button => {
      const dark = theme === 'dark';
      button.setAttribute('aria-label', dark ? 'Activar modo claro' : 'Activar modo oscuro');
      button.setAttribute('aria-pressed', String(dark));
      button.title = dark ? 'Activar modo claro' : 'Activar modo oscuro';
      button.textContent = dark ? '☀ Claro' : '☾ Oscuro';
    });
  };
  apply(preference || (system.matches ? 'dark' : 'light'));
  const mount = () => {
    const hosts = [...document.querySelectorAll('#masthead .site-header-primary-section-right')];
    if (!hosts.length && document.querySelector('#masthead')) hosts.push(document.querySelector('#masthead'));
    hosts.forEach(host => {
      if (host.querySelector('.ms-theme-toggle')) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'ms-theme-toggle';
      button.addEventListener('click', () => {
        preference = root.dataset.msTheme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem(key, preference); } catch { /* The control still works. */ }
        apply(preference);
      });
      host.append(button);
    });
    apply(root.dataset.msTheme);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once: true});
  else mount();
  system.addEventListener('change', event => { if (!preference) apply(event.matches ? 'dark' : 'light'); });
  window.addEventListener('storage', event => {
    if (event.key !== key) return;
    preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : null;
    apply(preference || (system.matches ? 'dark' : 'light'));
  });
})();
