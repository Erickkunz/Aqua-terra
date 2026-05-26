/* =====================================================================
   Aqua-Terra cursor wave (Antigravity-style)
   - Visible on both light and dark backgrounds (no mix-blend-mode).
   - Soft glowing focal dot follows the cursor with lerp.
   - Larger blurred halo trails slowly behind.
   - Subtle concentric wave rings emanate continuously.
   - Bigger pulse on click.
   - Pointer-events: none -> never blocks clicks or scroll.
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

  // --- State ---
  let mx = -200, my = -200;          // raw mouse (off-screen initially)
  let fx = mx, fy = my;              // focal (fast lerp)
  let hx = mx, hy = my;              // halo (slow lerp)
  let visible = false;
  let speed = 0;
  const ripples = [];
  let lastSpawn = 0;
  let waveSpawn = 0;

  // --- Colors ---
  const C_CYAN = [61, 217, 214];
  const C_BLUE = [46, 117, 182];
  const C_DEEP = [31, 78, 121];
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

  window.addEventListener('mousemove', (e) => {
    const dx = e.clientX - mx, dy = e.clientY - my;
    const v = Math.hypot(dx, dy);
    speed = speed * 0.85 + v * 0.15;
    mx = e.clientX; my = e.clientY;
    if (!visible) {
      // first time -> snap focal/halo to current pos so it doesn't fly in
      fx = mx; fy = my; hx = mx; hy = my;
    }
    visible = true;

    const now = performance.now();
    if (v > 5 && now - lastSpawn > 90) {
      ripples.push({
        x: mx, y: my,
        r: 6,
        rmax: 55 + Math.min(70, v * 1.2),
        born: now,
        life: 900,
        color: C_CYAN,
        width: 1.4,
      });
      lastSpawn = now;
    }
  }, { passive: true });

  window.addEventListener('mouseleave', () => { visible = false; });
  window.addEventListener('mouseenter', () => { visible = true; });

  window.addEventListener('click', (e) => {
    const now = performance.now();
    for (let i = 0; i < 2; i++) {
      ripples.push({
        x: e.clientX, y: e.clientY,
        r: 8 + i * 6,
        rmax: 110 + i * 35,
        born: now + i * 70,
        life: 1100,
        color: i ? C_BLUE : C_CYAN,
        width: 1.8,
      });
    }
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  function tick(now) {
    fx = lerp(fx, mx, 0.22);
    fy = lerp(fy, my, 0.22);
    hx = lerp(hx, mx, 0.085);
    hy = lerp(hy, my, 0.085);

    ctx.clearRect(0, 0, W, H);

    if (!visible) { requestAnimationFrame(tick); return; }

    // continuous gentle wave
    if (now - waveSpawn > 480) {
      ripples.push({
        x: hx, y: hy,
        r: 16, rmax: 78, born: now, life: 1700,
        color: C_CYAN, width: 1, gentle: true,
      });
      waveSpawn = now;
    }

    // --- Outer halo (big diffuse glow) ---
    const haloR = 65 + Math.min(25, speed * 0.5);
    const haloA = 0.18 + Math.min(0.10, speed * 0.004);
    const g1 = ctx.createRadialGradient(hx, hy, 0, hx, hy, haloR);
    g1.addColorStop(0, rgba(C_CYAN, haloA));
    g1.addColorStop(0.45, rgba(C_BLUE, haloA * 0.6));
    g1.addColorStop(1, rgba(C_DEEP, 0));
    ctx.fillStyle = g1;
    ctx.beginPath();
    ctx.arc(hx, hy, haloR, 0, Math.PI * 2);
    ctx.fill();

    // --- Inner focal glow ---
    const focalR = 22;
    const g2 = ctx.createRadialGradient(fx, fy, 0, fx, fy, focalR);
    g2.addColorStop(0, rgba(C_CYAN, 0.65));
    g2.addColorStop(0.45, rgba(C_CYAN, 0.22));
    g2.addColorStop(1, rgba(C_CYAN, 0));
    ctx.fillStyle = g2;
    ctx.beginPath();
    ctx.arc(fx, fy, focalR, 0, Math.PI * 2);
    ctx.fill();

    // --- Bright core ---
    ctx.beginPath();
    ctx.fillStyle = rgba(C_CYAN, 0.9);
    ctx.arc(fx, fy, 2.4, 0, Math.PI * 2);
    ctx.fill();

    // --- Wave ripples ---
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      const age = now - r.born;
      if (age < 0) continue;
      const t = age / r.life;
      if (t >= 1) { ripples.splice(i, 1); continue; }
      const eased = 1 - Math.pow(1 - t, 3);
      const radius = r.r + (r.rmax - r.r) * eased;
      const baseA = r.gentle ? 0.32 : 0.55;
      const alpha = baseA * (1 - t);
      // outer thin ring
      ctx.beginPath();
      ctx.lineWidth = r.width;
      ctx.strokeStyle = rgba(r.color, alpha);
      ctx.arc(r.x, r.y, radius, 0, Math.PI * 2);
      ctx.stroke();
      // inner glow ring
      if (!r.gentle && t < 0.6) {
        ctx.beginPath();
        ctx.lineWidth = r.width * 0.6;
        ctx.strokeStyle = rgba(C_CYAN, alpha * 0.4);
        ctx.arc(r.x, r.y, radius * 0.85, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    speed *= 0.93;
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
