/* Defers the Three.js viewer until the panel is near the viewport or touched. */
const panels = document.querySelectorAll('[data-molecule-viewer]');
if (panels.length) {
  let started = false;
  function loadViewer() {
    if (started) return;
    started = true;
    import('./molecular-viewer.js');
  }
  function scheduleLoad() {
    if ('requestIdleCallback' in window) window.requestIdleCallback(loadViewer, { timeout: 2500 });
    else setTimeout(loadViewer, 1);
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        observer.disconnect();
        scheduleLoad();
      }
    }, { rootMargin: '160px 0px', threshold: 0 });
    panels.forEach((panel) => observer.observe(panel));
  } else scheduleLoad();
  panels.forEach((panel) => {
    panel.addEventListener('pointerdown', loadViewer, { once: true, passive: true });
    panel.addEventListener('focusin', loadViewer, { once: true });
  });
}
