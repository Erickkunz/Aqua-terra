/* Aqua-Terra chat widget
   - Opens a panel anchored to .chat-fab with preset Q&A.
   - Clicking a question reveals the answer with a small typing effect.
   - Has an "Ask something else" -> opens /contact in a new tab.
*/
(function () {
  const fab = document.querySelector('.chat-fab');
  if (!fab) return;
  fab.setAttribute('aria-label', 'Chat de ayuda');
  fab.setAttribute('aria-haspopup', 'dialog');
  fab.setAttribute('aria-expanded', 'false');

  const QA = [
    { q: 'Que servicios ofrecen?',
      a: 'Tenemos 4 pilares: <strong>Tecnologia</strong> (IoT + sensorica), <strong>Consultoria</strong> (diagnosticos y ROI), <strong>Materiales</strong> (equipos certificados) y <strong>Consultoria internacional</strong> con BID, FAO, GIZ.' },
    { q: 'Como solicito una cotizacion?',
      a: 'Agrega productos al carrito y llena el formulario en <a href="/shop/cart">tu carrito</a>, o ve directo a <a href="/contact">Contacto</a> y elige "Cotizacion".' },
    { q: 'En que paises trabajan?',
      a: 'Tenemos proyectos en Peru, Mexico, Colombia, Chile, Argentina, Brasil y Ecuador, con oficinas en 4 ciudades de LATAM.' },
    { q: 'Tienen garantia?',
      a: 'Si. Garantia extendida 3-5 anos en equipos premium y servicio postventa regional en todas nuestras geografias.' },
    { q: 'Como calculo mi ROI?',
      a: 'Usa nuestra <a href="/pillars/consultoria">calculadora de ROI</a> interactiva o pidenos un diagnostico gratuito desde <a href="/contact">contacto</a>.' },
    { q: 'Cuanto demora un proyecto?',
      a: 'Depende del alcance: kits de riego <strong>2-4 semanas</strong>, sistemas medianos <strong>3-6 meses</strong>, plantas de tratamiento <strong>12-24 meses</strong>.' },
  ];

  // Build panel
  const panel = document.createElement('div');
  panel.className = 'chat-panel';
  panel.setAttribute('role', 'dialog');
  panel.setAttribute('aria-label', 'Chat de ayuda');
  panel.hidden = true;
  panel.innerHTML = `
    <div class="chat-head">
      <div class="chat-head-info">
        <span class="chat-avatar"><i class="fa-solid fa-droplet"></i></span>
        <div>
          <strong>Aqua-Terra</strong>
          <small><span class="chat-status-dot"></span> En linea</small>
        </div>
      </div>
      <button class="chat-close" aria-label="Cerrar chat"><i class="fa-solid fa-xmark"></i></button>
    </div>
    <div class="chat-body" id="chatBody">
      <div class="chat-msg chat-msg-bot">
        <span class="chat-bubble">Hola! Soy el asistente virtual de Aqua-Terra. En que te puedo ayudar?</span>
      </div>
      <div class="chat-questions" id="chatQuestions"></div>
    </div>
    <div class="chat-foot">
      <a href="/contact" class="btn btn-primary btn-sm btn-block">
        <i class="fa-solid fa-paper-plane"></i> Hablar con un humano
      </a>
    </div>
  `;
  document.body.appendChild(panel);

  const body = panel.querySelector('#chatBody');
  const qBox = panel.querySelector('#chatQuestions');
  const closeBtn = panel.querySelector('.chat-close');

  function renderQuestions() {
    qBox.innerHTML = '';
    QA.forEach((item, i) => {
      const btn = document.createElement('button');
      btn.className = 'chat-q-btn';
      btn.type = 'button';
      btn.innerHTML = `<i class="fa-solid fa-circle-question"></i> ${item.q}`;
      btn.addEventListener('click', () => answerQuestion(i, btn));
      qBox.appendChild(btn);
    });
  }

  function answerQuestion(idx, btn) {
    const item = QA[idx];
    btn.disabled = true;
    btn.classList.add('used');

    // user echo
    const userMsg = document.createElement('div');
    userMsg.className = 'chat-msg chat-msg-user';
    userMsg.innerHTML = `<span class="chat-bubble">${item.q}</span>`;
    qBox.before(userMsg);
    body.scrollTop = body.scrollHeight;

    // typing indicator
    const typing = document.createElement('div');
    typing.className = 'chat-msg chat-msg-bot';
    typing.innerHTML = `<span class="chat-bubble chat-typing"><span></span><span></span><span></span></span>`;
    qBox.before(typing);
    body.scrollTop = body.scrollHeight;

    setTimeout(() => {
      typing.remove();
      const bot = document.createElement('div');
      bot.className = 'chat-msg chat-msg-bot chat-anim';
      bot.innerHTML = `<span class="chat-bubble">${item.a}</span>`;
      qBox.before(bot);
      body.scrollTop = body.scrollHeight;
    }, 650);
  }

  function open() {
    panel.hidden = false;
    requestAnimationFrame(() => panel.classList.add('open'));
    fab.setAttribute('aria-expanded', 'true');
    fab.classList.add('active');
  }
  function close() {
    panel.classList.remove('open');
    fab.setAttribute('aria-expanded', 'false');
    fab.classList.remove('active');
    setTimeout(() => { panel.hidden = true; }, 280);
  }

  fab.addEventListener('click', () => {
    if (panel.classList.contains('open')) close();
    else open();
  });
  closeBtn.addEventListener('click', close);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

  renderQuestions();
})();
