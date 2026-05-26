/* Cursor wave + bubble trail (Aqua-Terra theme)
   - Renders on a fixed full-screen canvas (z-index above page, pointer-events: none).
   - Spawns particles on mouse move (drops + ripples) and decays them.
   - Auto-disables if user prefers-reduced-motion or device is coarse-pointer (touch).
*/
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const canvas = document.getElementById('cursorCanvas');
  if (!canvas || reduce || coarse) {
    if (canvas) canvas.remove();
    return;
  }

  const ctx = canvas.getContext('2d', { alpha: true });
  let W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2);

  function resize() {
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  const ripples = [];   // expanding rings
  const bubbles = [];   // small floating dots
  const trail = [];     // recent cursor positions for fluid trail
  const MAX_TRAIL = 14;

  let lastX = -1, lastY = -1, lastSpawn = 0;
  const COLOR_PRIMARY = 'rgba(61, 217, 214, 1)';   // cyan
  const COLOR_SECONDARY = 'rgba(46, 117, 182, 1)'; // blue
  const COLOR_ACCENT = 'rgba(112, 173, 71, 1)';    // green
  const palette = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ACCENT];

  window.addEventListener('mousemove', (e) => {
    const x = e.clientX, y = e.clientY;
    const now = performance.now();
    trail.push({ x, y, t: now });
    if (trail.length > MAX_TRAIL) trail.shift();

    // distance gate to avoid spawning every pixel
    const dx = lastX < 0 ? 999 : x - lastX;
    const dy = lastY < 0 ? 999 : y - lastY;
    const dist = Math.hypot(dx, dy);

    if (dist > 6 && now - lastSpawn > 18) {
      // ripple
      ripples.push({
        x, y,
        r: 4 + Math.random() * 3,
        rmax: 38 + Math.random() * 22,
        alpha: 0.65,
        color: palette[(Math.random() * palette.length) | 0],
        born: now,
      });
      // 1-2 bubbles drifting upward
      const burst = 1 + ((Math.random() * 2) | 0);
      for (let i = 0; i < burst; i++) {
        bubbles.push({
          x: x + (Math.random() - 0.5) * 14,
          y: y + (Math.random() - 0.5) * 10,
          vx: (Math.random() - 0.5) * 0.4,
          vy: -0.4 - Math.random() * 0.7,
          r: 1.6 + Math.random() * 2.4,
          alpha: 0.7,
          color: palette[(Math.random() * palette.length) | 0],
        });
      }
      lastSpawn = now;
    }

    lastX = x; lastY = y;
  }, { passive: true });

  window.addEventListener('click', (e) => {
    // bigger splash on click
    for (let i = 0; i < 3; i++) {
      ripples.push({
        x: e.clientX, y: e.clientY,
        r: 6 + i * 4, rmax: 70 + i * 25, alpha: 0.7 - i * 0.18,
        color: palette[i % palette.length], born: performance.now(),
      });
    }
    for (let i = 0; i < 10; i++) {
      const angle = (Math.PI * 2 * i) / 10;
      bubbles.push({
        x: e.clientX, y: e.clientY,
        vx: Math.cos(angle) * (1 + Math.random()),
        vy: Math.sin(angle) * (1 + Math.random()),
        r: 2 + Math.random() * 3,
        alpha: 0.85,
        color: palette[i % palette.length],
      });
    }
  });

  function drawTrail() {
    if (trail.length < 2) return;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    for (let i = 1; i < trail.length; i++) {
      const p0 = trail[i - 1];
      const p1 = trail[i];
      const t = i / trail.length;
      ctx.strokeStyle = `rgba(61, 217, 214, ${0.06 + t * 0.18})`;
      ctx.lineWidth = 1 + t * 4;
      ctx.beginPath();
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);
      ctx.stroke();
    }
  }

  function tick() {
    ctx.clearRect(0, 0, W, H);

    // fluid trail
    drawTrail();

    // ripples
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      r.r += (r.rmax - r.r) * 0.06;
      r.alpha *= 0.95;
      ctx.beginPath();
      ctx.lineWidth = 1.6;
      ctx.strokeStyle = r.color.replace('1)', r.alpha.toFixed(3) + ')');
      ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
      ctx.stroke();
      if (r.alpha < 0.03) ripples.splice(i, 1);
    }

    // bubbles
    for (let i = bubbles.length - 1; i >= 0; i--) {
      const b = bubbles[i];
      b.x += b.vx;
      b.y += b.vy;
      b.vy *= 0.985;
      b.alpha *= 0.97;
      ctx.beginPath();
      ctx.fillStyle = b.color.replace('1)', (b.alpha * 0.85).toFixed(3) + ')');
      ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
      ctx.fill();
      // shine highlight
      ctx.beginPath();
      ctx.fillStyle = `rgba(255,255,255,${b.alpha * 0.5})`;
      ctx.arc(b.x - b.r * 0.35, b.y - b.r * 0.35, Math.max(0.4, b.r * 0.35), 0, Math.PI * 2);
      ctx.fill();
      if (b.alpha < 0.03) bubbles.splice(i, 1);
    }

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);

  // hide trail when cursor leaves
  document.addEventListener('mouseleave', () => { trail.length = 0; });
})();
