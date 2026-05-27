/* =====================================================================
   Aqua-Terra cursor + floating spheres (SOLID, fully visible)
   - Solid colored spheres that follow the cursor (trail of 7 orbs).
   - 14 ambient spheres drift across the page in the background.
   - No transparency tricks: opaque fills, bright cores, hard edges.
   - Disabled on touch and prefers-reduced-motion.
   ===================================================================== */
(function () {
  if (window.__aquaCursor) return; window.__aquaCursor = true;
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  let canvas = document.getElementById('cursorCanvas');
  if (!canvas) {
    canvas = document.createElement('canvas');
    canvas.id = 'cursorCanvas';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
  }
  if (reduce || coarse) { canvas.remove(); return; }

  const ctx = canvas.getContext('2d', { alpha: true });
  let W = 0, H = 0;
  const DPR = Math.min(window.devicePixelRatio || 1, 2);

  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();
  window.addEventListener('resize', resize);

  // ===== Color palette (cores blancos -> bordes vivos) =====
  const COLORS = [
    { core: '#FFFFFF', mid: '#7FF1EE', edge: '#3DD9D6' }, // cyan
    { core: '#FFFFFF', mid: '#6BBDFF', edge: '#2E75B6' }, // blue
    { core: '#FFFFFF', mid: '#B5F088', edge: '#70AD47' }, // green
    { core: '#FFFFFF', mid: '#FFD580', edge: '#E8A33D' }, // amber
  ];

  // ===== Cursor state =====
  let mx = window.innerWidth / 2, my = window.innerHeight / 2;
  let visible = true;
  const TRAIL_LEN = 7;
  const trail = Array.from({ length: TRAIL_LEN }, (_, i) => ({
    x: mx, y: my,
    radius: 22 - i * 2.2,
    color: COLORS[i % COLORS.length],
    smoothing: 0.18 + i * 0.04,
  }));

  window.addEventListener('mousemove', (e) => {
    mx = e.clientX; my = e.clientY;
    visible = true;
  }, { passive: true });
  window.addEventListener('mouseleave', () => { visible = false; });
  window.addEventListener('mouseenter', () => { visible = true; });

  // ===== Click bursts =====
  const bursts = [];
  window.addEventListener('click', (e) => {
    const now = performance.now();
    for (let i = 0; i < 10; i++) {
      const angle = (Math.PI * 2 * i) / 10;
      const speed = 4 + Math.random() * 3;
      bursts.push({
        x: e.clientX, y: e.clientY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        r: 8 + Math.random() * 6,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        born: now,
        life: 800 + Math.random() * 400,
      });
    }
  });

  // ===== Ambient floating spheres =====
  function spawnAmbient() {
    const radius = 14 + Math.random() * 28;
    return {
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.7,
      vy: (Math.random() - 0.5) * 0.7,
      r: radius,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.01 + Math.random() * 0.02,
    };
  }
  const AMBIENT_COUNT = 14;
  const ambient = Array.from({ length: AMBIENT_COUNT }, spawnAmbient);

  // ===== Drawing helpers =====
  function hexA(hex, a) {
    const h = hex.replace('#', '');
    const r = parseInt(h.substring(0, 2), 16);
    const g = parseInt(h.substring(2, 4), 16);
    const b = parseInt(h.substring(4, 6), 16);
    return `rgba(${r},${g},${b},${a})`;
  }

  function drawSphere(x, y, r, color, alpha = 1) {
    // Outer halo
    const haloR = r * 2.3;
    const halo = ctx.createRadialGradient(x, y, r * 0.5, x, y, haloR);
    halo.addColorStop(0, hexA(color.edge, 0.45 * alpha));
    halo.addColorStop(1, hexA(color.edge, 0));
    ctx.fillStyle = halo;
    ctx.beginPath();
    ctx.arc(x, y, haloR, 0, Math.PI * 2);
    ctx.fill();

    // Main solid sphere body (opaque radial gradient)
    const sphere = ctx.createRadialGradient(
      x - r * 0.35, y - r * 0.35, r * 0.1,
      x, y, r
    );
    sphere.addColorStop(0, hexA(color.core, alpha));
    sphere.addColorStop(0.45, hexA(color.mid, alpha));
    sphere.addColorStop(1, hexA(color.edge, alpha));
    ctx.fillStyle = sphere;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();

    // Hard rim (gives "solid" perception)
    ctx.lineWidth = 1.5;
    ctx.strokeStyle = hexA(color.edge, 0.9 * alpha);
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();

    // Specular highlight (white dot top-left)
    const spec = ctx.createRadialGradient(
      x - r * 0.4, y - r * 0.45, 0,
      x - r * 0.4, y - r * 0.45, r * 0.6
    );
    spec.addColorStop(0, hexA('#FFFFFF', 0.9 * alpha));
    spec.addColorStop(1, hexA('#FFFFFF', 0));
    ctx.fillStyle = spec;
    ctx.beginPath();
    ctx.arc(x - r * 0.4, y - r * 0.45, r * 0.6, 0, Math.PI * 2);
    ctx.fill();
  }

  function lerp(a, b, t) { return a + (b - a) * t; }

  // ===== Animation loop =====
  function tick(now) {
    ctx.clearRect(0, 0, W, H);

    // Ambient floating spheres
    for (const a of ambient) {
      a.x += a.vx;
      a.y += a.vy;
      a.pulse += a.pulseSpeed;
      if (a.x < -60) a.x = W + 60;
      if (a.x > W + 60) a.x = -60;
      if (a.y < -60) a.y = H + 60;
      if (a.y > H + 60) a.y = -60;
      const pulse = 1 + Math.sin(a.pulse) * 0.15;
      drawSphere(a.x, a.y, a.r * pulse, a.color, 0.9);
    }

    // Click bursts
    for (let i = bursts.length - 1; i >= 0; i--) {
      const b = bursts[i];
      const age = now - b.born;
      const t = age / b.life;
      if (t >= 1) { bursts.splice(i, 1); continue; }
      b.x += b.vx;
      b.y += b.vy;
      b.vx *= 0.96;
      b.vy *= 0.96;
      const r = b.r * (1 - t * 0.4);
      drawSphere(b.x, b.y, r, b.color, 1 - t);
    }

    if (visible) {
      // Cursor trail (solid spheres of decreasing size following the mouse)
      let prevX = mx, prevY = my;
      for (let i = 0; i < trail.length; i++) {
        const t = trail[i];
        t.x = lerp(t.x, prevX, t.smoothing);
        t.y = lerp(t.y, prevY, t.smoothing);
        prevX = t.x;
        prevY = t.y;
        const alpha = 1 - (i / trail.length) * 0.55;
        drawSphere(t.x, t.y, t.radius, t.color, alpha);
      }
    }

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
