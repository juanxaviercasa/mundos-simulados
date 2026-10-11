/* Cloudflare Worker + Turnstile, with explicit delivery confirmation. */
(() => {
  const form = document.querySelector('#npp-contact-form');
  if (!form) return;
  if (form.dataset.contactInitialized) return;
  form.dataset.contactInitialized = 'true';
  const en = form.dataset.language === 'en';
  const contactEmail = form.dataset.contactEmail || 'contacto@nubeparapymes.online';
  const words = en ? {
    send: 'Send inquiry', sending: 'Sending…', unavailable: 'The form is temporarily unavailable. Please email contacto@nubeparapymes.online.',
    verify: 'Complete the verification to send your inquiry.', success: 'Your inquiry was sent. We will reply to the email address you provided.',
    failure: 'We could not confirm delivery. Your message is still here; you can email contacto@nubeparapymes.online.',
    limit: 'Too many attempts. Wait a minute before trying again, or email us directly.'
  } : {
    send: 'Enviar consulta', sending: 'Enviando…', unavailable: 'El formulario no está disponible en este momento. Escríbenos a contacto@nubeparapymes.online.',
    verify: 'Completa la verificación para enviar tu consulta.', success: 'Tu consulta fue enviada. Te responderemos al correo que indicaste.',
    failure: 'No pudimos confirmar el envío. Tu mensaje sigue aquí; puedes escribir a contacto@nubeparapymes.online.',
    limit: 'Hay demasiados intentos. Espera un minuto antes de volver a enviar o escríbenos directamente.'
  };
  for (const key of Object.keys(words)) words[key] = words[key].replaceAll('contacto@nubeparapymes.online', contactEmail);
  const button = form.querySelector('[type=submit]');
  const status = document.querySelector('#npp-form-msg');
  const help = document.querySelector('#contact-message-help');
  const originalHelp = help.textContent;
  let token = '', widget, sending = false, ready = false;
  function message(text, state = '') { status.textContent = text; status.dataset.state = state; }
  function refresh() { button.disabled = sending || !ready || !token; }
  function selectTopic() { help.textContent = form.querySelector('[name=category]:checked, select[name=category] option:checked')?.dataset.help || originalHelp; }
  form.addEventListener('change', selectTopic);
  const type = new URL(location.href).searchParams.get('tipo');
  for (const input of form.querySelectorAll('[name=category]')) if (input.value === type) input.checked = true;
  const categorySelect = form.querySelector('select[name=category]');
  if (categorySelect && [...categorySelect.options].some(option => option.value === type)) categorySelect.value = type;
  selectTopic();
  async function initialize() {
    try {
      const response = await fetch('/api/contact', {headers: {Accept: 'application/json'}, cache: 'no-store', signal: AbortSignal.timeout(8000)});
      if (!response.ok) throw new Error('Unavailable');
      const settings = await response.json();
      if (settings.ready !== true || !settings.siteKey) throw new Error('Not configured');
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      script.async = true;
      script.onerror = () => message(words.unavailable, 'error');
      script.onload = () => {
        widget = window.turnstile.render('#npp-turnstile', {
          sitekey: settings.siteKey, action: 'contact', language: en ? 'en' : 'es',
          callback(value) { token = value; ready = true; refresh(); if (!status.dataset.state) message(''); },
          'expired-callback'() { token = ''; refresh(); message(words.verify); },
          'error-callback'() { token = ''; refresh(); message(words.unavailable, 'error'); }
        });
        message(words.verify);
      };
      document.head.append(script);
    } catch { message(words.unavailable, 'error'); }
  }
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (sending || !form.reportValidity()) return;
    if (!ready || !token || form.elements.website.value) { message(words.verify, 'error'); return; }
    sending = true; refresh(); button.textContent = words.sending; message(words.sending);
    const data = Object.fromEntries(new FormData(form));
    data.consent = form.elements.consent.checked;
    data.language = en ? 'en' : 'es';
    data.turnstile = token;
    try {
      const response = await fetch('/api/contact', {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(data), signal: AbortSignal.timeout(25000)});
      const result = await response.json();
      if (!response.ok || result.success !== true) {
        message(response.status === 429 ? words.limit : words.failure, 'error');
      } else {
        form.reset(); selectTopic(); message(words.success, 'success');
      }
    } catch { message(words.failure, 'error'); }
    finally {
      sending = false; token = ''; button.textContent = words.send; refresh();
      if (widget !== undefined) window.turnstile.reset(widget);
      status.focus();
    }
  });
  initialize();
})();
