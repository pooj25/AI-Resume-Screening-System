/* ── main.js — AI Resume Screener ── */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss alerts ───────────────
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // ── Score bar animation on page load ──
  document.querySelectorAll('.score-bar-fill').forEach(bar => {
    const targetWidth = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.transition = 'width 1s cubic-bezier(0.4,0,0.2,1)';
      bar.style.width = targetWidth;
    }, 200);
  });

  // ── Stat counter animation ─────────────
  document.querySelectorAll('.stat-number').forEach(el => {
    const raw = el.textContent.trim();
    const num = parseInt(raw);
    if (!isNaN(num) && num > 0) {
      let current = 0;
      const duration = 1000;
      const step = Math.max(1, Math.floor(num / 40));
      const interval = setInterval(() => {
        current = Math.min(current + step, num);
        el.textContent = current;
        if (current >= num) clearInterval(interval);
      }, duration / 40);
    }
  });

  // ── Close modal on Escape key ──────────
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(m => m.classList.remove('active'));
    }
  });

  // ── Sidebar active link highlight ──────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });

  // ── Table row click → navigate ─────────
  document.querySelectorAll('tbody tr[data-href]').forEach(row => {
    row.style.cursor = 'pointer';
    row.addEventListener('click', () => {
      window.location.href = row.dataset.href;
    });
  });

  // ── Smooth scroll for anchor links ──────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

});
