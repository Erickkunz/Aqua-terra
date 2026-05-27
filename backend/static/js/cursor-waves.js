/* =====================================================================
   Aqua-Terra cursor water waves v15
   - 5 big auto-waves at center on load (visual showcase)
   - 3 small translucent rings persistently around the cursor
     (move WITH the cursor, no trail/wake behind)
   - JS-driven animation (bypasses Windows "reduce animations" setting)
   ===================================================================== */
(function () {
  if (window.__aquaCursorDOM) return; window.__aquaCursorDOM = true;

  function boot() {
    const coarse = window.matchMedia('(pointer: coarse)').matches;
    if (coarse) {
      console.warn('[Aqua waves] disabled (touch device)');
      return;
    }

    // Clean leftover
    document.querySelectorAll('#cursorCanvas, #aquaCursorRoot, #aquaCursorStyles, #aquaDebugMarker').forEach(el => el.remove());

    // Minimal CSS (no animations - everything driven by JS)
    const css = document.createElement('style');
    css.id = 'aquaCursorStyles';
    css.textContent = `
      #aquaCursorRoot {
        position: fixed !important;
        top: 0 !important; left: 0 !important;
        width: 100vw !important; height: 100vh !important;
        pointer-events: none !important;
        z-index: 2147483646 !important;
        overflow: hidden !important;
      }
      /* Big showcase wave (auto + future use) */
      .aqua-wave {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        border: 5px solid #3DD9D6;
        background: radial-gradient(circle, rgba(127, 241, 238, 0.35) 0%, rgba(61, 217, 214, 0.1) 50%, rgba(61, 217, 214, 0) 100%);
        box-shadow:
          0 0 26px 5px rgba(61, 217, 214, 0.85),
          0 0 14px rgba(255, 255, 255, 0.6),
          inset 0 0 14px rgba(127, 241, 238, 0.5);
        transform: translate(-50%, -50%);
        will-change: transform, opacity, width, height;
      }
      /* Small persistent cursor rings - translucent, gentle */
      .aqua-cursor-ring {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
        border: 1.5px solid rgba(127, 241, 238, 0.55);
        background: transparent;
        box-shadow: 0 0 6px rgba(61, 217, 214, 0.25);
        transform: translate(-50%, -50%);
        opacity: 0;
        will-change: transform, opacity;
      }
    `;
    document.head.appendChild(css);

    const root = document.createElement('div');
    root.id = 'aquaCursorRoot';
    root.setAttribute('aria-hidden', 'true');
    document.body.appendChild(root);

    // ===== Big wave system (used for auto-spawn at load) =====
    const waves = [];
    const WAVE_LIFE = 1300;

    function spawnWave(x, y, sizeTo) {
      const sizeFrom = 18;
      const el = document.createElement('div');
      el.className = 'aqua-wave';
      el.style.left = x + 'px';
      el.style.top = y + 'px';
      el.style.width = sizeFrom + 'px';
      el.style.height = sizeFrom + 'px';
      el.style.opacity = '0';
      el.style.borderWidth = '5px';
      root.appendChild(el);
      waves.push({ el, born: performance.now(), life: WAVE_LIFE, sizeFrom, sizeTo });
    }

    // ===== Small cursor rings (persistent, follow cursor) =====
    // 3 concentric rings of different base sizes, each pulses gently,
    // each follows the cursor with slight smoothing for an organic feel.
    const RING_COUNT = 3;
    const rings = [];
    for (let i = 0; i < RING_COUNT; i++) {
      const el = document.createElement('div');
      el.className = 'aqua-cursor-ring';
      root.appendChild(el);
      rings.push({
        el,
        baseSize: 24 + i * 18,    // 24, 42, 60
        x: window.innerWidth / 2,
        y: window.innerHeight / 2,
        smooth: 0.35 - i * 0.08,   // outer rings lag slightly more
        phase: i * Math.PI * 0.6,  // out-of-phase pulses
      });
    }

    // Cursor tracking
    let mx = window.innerWidth / 2, my = window.innerHeight / 2;
    let lastMoveTime = 0;
    let cursorActive = false;

    window.addEventListener('mousemove', (e) => {
      mx = e.clientX; my = e.clientY;
      lastMoveTime = performance.now();
      cursorActive = true;
    }, { passive: true });

    window.addEventListener('mouseleave', () => { cursorActive = false; });
    window.addEventListener('mouseenter', () => { cursorActive = true; });

    function lerp(a, b, t) { return a + (b - a) * t; }

    function tick(now) {
      // ---- Big waves (auto-spawn animation) ----
      for (let i = waves.length - 1; i >= 0; i--) {
        const w = waves[i];
        const age = now - w.born;
        const t = age / w.life;
        if (t >= 1) {
          w.el.remove();
          waves.splice(i, 1);
          continue;
        }
        const easeT = 1 - Math.pow(1 - t, 3);
        const size = w.sizeFrom + (w.sizeTo - w.sizeFrom) * easeT;
        const opacity = t < 0.15 ? (t / 0.15) : (1 - (t - 0.15) / 0.85);
        const borderW = 5 - 3.5 * easeT;
        w.el.style.width = size + 'px';
        w.el.style.height = size + 'px';
        w.el.style.opacity = opacity.toFixed(3);
        w.el.style.borderWidth = borderW.toFixed(2) + 'px';
      }

      // ---- Cursor rings (small, translucent, follow cursor) ----
      // Fade them out if cursor has been still for >600ms (no trail when idle)
      const idleTime = now - lastMoveTime;
      const targetVisibility = (cursorActive && idleTime < 800) ? 1 : 0;

      for (let i = 0; i < rings.length; i++) {
        const r = rings[i];
        // Smooth follow (all rings target same cursor point - no trail)
        r.x = lerp(r.x, mx, r.smooth);
        r.y = lerp(r.y, my, r.smooth);
        // Gentle breathing pulse
        const pulse = 1 + Math.sin(now * 0.005 + r.phase) * 0.12;
        const size = r.baseSize * pulse;
        // Current opacity smoothly approaches target
        const currentOp = parseFloat(r.el.style.opacity) || 0;
        const baseOp = 0.55 - i * 0.1; // outer rings more translucent
        const targetOp = baseOp * targetVisibility;
        const newOp = lerp(currentOp, targetOp, 0.12);
        r.el.style.left = r.x + 'px';
        r.el.style.top = r.y + 'px';
        r.el.style.width = size + 'px';
        r.el.style.height = size + 'px';
        r.el.style.opacity = newOp.toFixed(3);
      }

      requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);

    // Keep root last child of body (defensive)
    setInterval(() => {
      if (document.body.lastElementChild !== root) {
        document.body.appendChild(root);
      }
    }, 2000);

    // ===== Auto-spawn 5 big waves at center on load =====
    let testN = 0;
    const testTimer = setInterval(() => {
      const cx = window.innerWidth / 2 + (Math.random() - 0.5) * 200;
      const cy = window.innerHeight / 2 + (Math.random() - 0.5) * 200;
      spawnWave(cx, cy, 200);
      testN++;
      if (testN >= 5) clearInterval(testTimer);
    }, 400);

    console.log('[Aqua waves v15] 3 small cursor rings + 5 auto big waves on load');
  }

  if (document.body) boot();
  else document.addEventListener('DOMContentLoaded', boot, { once: true });
})();
