/* =====================================================================
   Aqua-Terra cursor effect (Antigravity-style fluid wave)
   - A soft glowing focal point follows the cursor with lerp.
   - A larger, slower "halo" trails behind for a fluid feeling.
   - A subtle concentric wave ring expands continuously around the cursor.
   - On movement spikes, an extra ripple is spawned.
   - Pointer-events: none, so it NEVER blocks clicks or scroll.
   - Uses mix-blend-mode: screen so the effect blends with any background
     without obscuring text or interactive elements.
   - Disabled on touch devices and prefers-reduced-motion.
   ===================================================================== */
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = window.matchMedia('(pointer: coarse)').matches;
  const canvas = document.getElementById('cursorCanvas');
  if (!canvas) return;
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

  // --- State ---
  let mx = W / 2, my = H / 2;        // raw mouse
  let fx = mx, fy = my;              // focal (fast lerp)
  let hx = mx, hy = my;              // halo (slow lerp)
  let visible = false;
  let lastMove = 0;
  let speed = 0;                     // moving average of cursor speed
  const ripples = [];                // expanding rings (continuous + on-burst)
  let lastSpawn = 0;
  let waveSpawn = 0;                 // continuous wave timer

  // --- Colors (water palette) ---
  const C_CYAN = [61, 217, 214];
  const C_BLUE = [46, 117, 182];
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

  // --- Mouse tracking ---
  window.addEventListener('mousemove', (e) => {
    const dx = e.clientX - mx, dy = e.clientY - my;
    const v = Math.hypot(dx, dy);
    speed = speed * 0.85 + v * 0.15;
    mx = e.clientX; my = e.clientY;
    visible = true;
    lastMove = performance.now();

    // movement burst -> extra ripple
    const now = performance.now();
    if (v > 6 && now - lastSpawn > 70) {
      ripples.push({
        x: mx, y: my,
        r: 6,
        rmax: 60 + Math.min(80, v * 1.5),
        born: now,
        life: 950,
        color: C_CYAN,
        width: 1.2,
      });
      lastSpawn = now;
    }
  }, { passive: true });

  window.addEventListener('mouseleave', () => { visible = false; });
  window.addEventListener('mouseenter', () => { visible = true; });

  // bigger pulse on click
  window.addEventListener('click', (e) => {
    const now = performance.now();
    for (let i = 0; i < 2; i++) {
      ripples.push({
        x: e.clientX, y: e.clientY,
        r: 8 + i * 6,
        rmax: 120 + i * 40,
        born: now + i * 80,
        life: 1100,
        color: i ? C_BLUE : C_CYAN,
        width: 1.6,
      });
    }
  });

  // --- Animation loop ---
  function lerp(a, b, t) { return a + (b - a) * t; }

  function tick(now) {
    // smooth follow
    fx = lerp(fx, mx, 0.22);
    fy = lerp(fy, my, 0.22);
    hx = lerp(hx, mx, 0.08);
    hy = lerp(hy, my, 0.08);

    // soft clear (no trail buildup, but smooth)
    ctx.clearRect(0, 0, W, H);

    if (!visible) {
      requestAnimationFrame(tick);
      return;
    }

    // continuous gentle wave around the cursor
    if (now - waveSpawn > 420) {
      ripples.push({
        x: hx, y: hy,
        r: 14,
        rmax: 70,
        born: now,
        life: 1600,
        color: C_CYAN,
        width: 1,
        gentle: true,
      });
      waveSpawn = now;
    }

    // --- Halo (big soft glow, slow follow) ---
    const haloR = 60 + Math.min(20, speed * 0.5);
    const haloAlpha = 0.10 + Math.min(0.08, speed * 0.004);
    const g1 = ctx.createRadialGradient(hx, hy, 0, hx, hy, haloR);
    g1.addColorStop(0, rgba(C_CYAN, haloAlpha));
    g1.addColorStop(0.55, rgba(C_BLUE, haloAlpha * 0.55));
    g1.addColorStop(1, rgba(C_BLUE, 0));
    ctx.fillStyle = g1;
    ctx.beginPath();
    ctx.arc(hx, hy, haloR, 0, Math.PI * 2);
    ctx.fill();

    // --- Focal soft dot (close follow) ---
    const focalR = 18;
    const g2 = ctx.createRadialGradient(fx, fy, 0, fx, fy, focalR);
    g2.addColorStop(0, rgba(C_CYAN, 0.55));
    g2.addColorStop(0.5, rgba(C_CYAN, 0.18));
    g2.addColorStop(1, rgba(C_CYAN, 0));
    ctx.fillStyle = g2;
    ctx.beginPath();
    ctx.arc(fx, fy, focalR, 0, Math.PI * 2);
    ctx.fill();

    // tiny bright core
    ctx.beginPath();
    ctx.fillStyle = rgba(C_CYAN, 0.7);
    ctx.arc(fx, fy, 2.2, 0, Math.PI * 2);
    ctx.fill();

    // --- Wave ripples (concentric rings) ---
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      const age = now - r.born;
      if (age < 0) continue;
      const t = age / r.life;
      if (t >= 1) { ripples.splice(i, 1); continue; }
      // easeOutCubic for radius
      const eased = 1 - Math.pow(1 - t, 3);
      const radius = r.r + (r.rmax - r.r) * eased;
      // fade alpha
      const baseA = r.gentle ? 0.28 : 0.55;
      const alpha = baseA * (1 - t);
      ctx.beginPath();
      ctx.lineWidth = r.width;
      ctx.strokeStyle = rgba(r.color, alpha);
      ctx.arc(r.x, r.y, radius, 0, Math.PI * 2);
      ctx.stroke();
    }

    // decay speed when idle
    speed *= 0.93;

    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
