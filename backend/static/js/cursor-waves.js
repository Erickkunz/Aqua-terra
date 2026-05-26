/* =====================================================================
   Aqua-Terra cursor wave (HIGHLY VISIBLE Antigravity-style)
   Big focal dot + solid ring + bright halo + continuous waves.
   Visible on light AND dark backgrounds.
   Disabled on touch and prefers-reduced-motion.
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

  let mx = -200, my = -200;
  let fx = mx, fy = my;
  let hx = mx, hy = my;
  let visible = false;
  let speed = 0;
  const ripples = [];
  let lastSpawn = 0;
  let waveSpawn = 0;

  const C_CYAN = [61, 217, 214];
  const C_BLUE = [46, 117, 182];
  const C_DEEP = [31, 78, 121];
  const C_WHITE = [255, 255, 255];
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;

  window.addEventListener('mousemove', (e) => {
    const dx = e.clientX - mx, dy = e.clientY - my;
    const v = Math.hypot(dx, dy);
    speed = speed * 0.85 + v * 0.15;
    mx = e.clientX; my = e.clientY;
    if (!visible) { fx = mx; fy = my; hx = mx; hy = my; }
    visible = true;

    const now = performance.now();
    if (v > 4 && now - lastSpawn > 60) {
      ripples.push({
        x: mx, y: my,
        r: 8,
        rmax: 70 + Math.min(80, v * 1.3),
        born: now,
        life: 900,
        color: C_CYAN,
        width: 2.2,
      });
      lastSpawn = now;
    }
  }, { passive: true });

  window.addEventListener('mouseleave', () => { visible = false; });
  window.addEventListener('mouseenter', () => { visible = true; });

  window.addEventListener('click', (e) => {
    const now = performance.now();
    for (let i = 0; i < 3; i++) {
      ripples.push({
        x: e.clientX, y: e.clientY,
        r: 10 + i * 8,
        rmax: 130 + i * 50,
        born: now + i * 70,
        life: 1100,
        color: i === 1 ? C_BLUE : C_CYAN,
        width: 2.5,
      });
    }
  });

  function lerp(a, b, t) { return a + (b - a) * t; }

  function tick(now) {
    fx = lerp(fx, mx, 0.25);
    fy = lerp(fy, my, 0.25);
    hx = lerp(hx, mx, 0.09);
    hy = lerp(hy, my, 0.09);

    ctx.clearRect(0, 0, W, H);

    if (!visible) { requestAnimationFrame(tick); return; }

    // continuous gentle wave
    if (now - waveSpawn > 380) {
      ripples.push({
        x: hx, y: hy,
        r: 20, rmax: 95, born: now, life: 1700,
        color: C_CYAN, width: 1.5, gentle: true,
      });
      waveSpawn = now;
    }

    // ===== OUTER HALO (big diffuse glow) =====
    const haloR = 80 + Math.min(30, speed * 0.6);
    const haloA = 0.35 + Math.min(0.15, speed * 0.005);
    const g1 = ctx.createRadialGradient(hx, hy, 0, hx, hy, haloR);
    g1.addColorStop(0, rgba(C_CYAN, haloA));
    g1.addColorStop(0.4, rgba(C_BLUE, haloA * 0.7));
    g1.addColorStop(1, rgba(C_DEEP, 0));
    ctx.fillStyle = g1;
    ctx.beginPath();
    ctx.arc(hx, hy, haloR, 0, Math.PI * 2);
    ctx.fill();

    // ===== INNER FOCAL GLOW =====
    const focalR = 32;
    const g2 = ctx.createRadialGradient(fx, fy, 0, fx, fy, focalR);
    g2.addColorStop(0, rgba(C_WHITE, 0.85));
    g2.addColorStop(0.25, rgba(C_CYAN, 0.75));
    g2.addColorStop(0.6, rgba(C_CYAN, 0.35));
    g2.addColorStop(1, rgba(C_CYAN, 0));
    ctx.fillStyle = g2;
    ctx.beginPath();
    ctx.arc(fx, fy, focalR, 0, Math.PI * 2);
    ctx.fill();

    // ===== SOLID RING (always visible, like Antigravity) =====
    ctx.beginPath();
    ctx.lineWidth = 2;
    ctx.strokeStyle = rgba(C_CYAN, 0.95);
    ctx.arc(fx, fy, 18, 0, Math.PI * 2);
    ctx.stroke();

    // inner soft ring
    ctx.beginPath();
    ctx.lineWidth = 1.2;
    ctx.strokeStyle = rgba(C_WHITE, 0.6);
    ctx.arc(fx, fy, 11, 0, Math.PI * 2);
    ctx.stroke();

    // ===== BRIGHT CORE DOT =====
    ctx.beginPath();
    ctx.fillStyle = rgba(C_WHITE, 1);
    ctx.arc(fx, fy, 3.5, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = rgba(C_CYAN, 1);
    ctx.arc(fx, fy, 2, 0, Math.PI * 2);
    ctx.fill();

    // ===== WAVE RIPPLES =====
    for (let i = ripples.length - 1; i >= 0; i--) {
      const r = ripples[i];
      const age = now - r.born;
      if (age < 0) continue;
      const t = age / r.life;
      if (t >= 1) { ripples.splice(i, 1); continue; }
      const eased = 1 - Math.pow(1 - t, 3);
      const radius = r.r + (r.rmax - r.r) * eased;
      const baseA = r.gentle ? 0.45 : 0.75;
      const alpha = baseA * (1 - t);
      // outer ring
      ctx.beginPath();
      ctx.lineWidth = r.width;
      ctx.strokeStyle = rgba(r.color, alpha);
      ctx.arc(r.x, r.y, radius, 0, Math.PI * 2);
      ctx.stroke();
      // inner glow ring
      if (!r.gentle && t < 0.65) {
        ctx.beginPath();
        ctx.lineWidth = r.width * 0.7;
        ctx.strokeStyle = rgba(C_WHITE, alpha * 0.45);
        ctx.arc(r.x, r.y, radius * 0.85, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    speed *= 0.93;
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();
