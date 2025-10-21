// add_entrada = document.getElementById('add-entrada')
// fecha_add_entrada = document.getElementById('fecha-add-entrada')

// add_saida = document.getElementById('add-saida')
// fecha_add_saida = document.getElementById('fecha-add-saida')

// function Abrir_Entrada() {

// }

// function Fechar_Entrada() {

// }

// function Abrir_Saida() {

// }

// function Fechar_Saida() {

// }

// add_entrada.addEventListener('click', Abrir_Entrada)
// fecha_add_entrada.addEventListener('click', Fechar_Entrada)

// add_saida.addEventListener('click', Abrir_Saida)
// fecha_add_saida.addEventListener('click', Fechar_Saida)

(function(){
  const openEntrada = document.getElementById('openEntrada');
  const openSaida = document.getElementById('openSaida')
  const overlay = document.getElementById('overlay');
  const modal = overlay.querySelector('.modal');
  const closeEntrada = document.getElementById('closeEntrada');
  const closeSaida = document.getElementById('closeSaida')
  const form = document.getElementById('modalForm');
  const input = document.getElementById('inputField');
  const errorMsg = document.getElementById('errorMsg');

  let lastFocusedElement = null;
  let focusListener = null;

  /* Abrir modais */
  function openAddEntrada() {
    lastFocusedElement = document.activeElement;
    overlay.classList.add('show');
    overlay.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    setTimeout(() => input.focus(), 60);
    trapFocus(modal);
  }

  function openAddSaida() {
    lastFocusedElement = document.activeElement;
    overlay.classList.add('show');
    overlay.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    setTimeout(() => input.focus(), 60);
    trapFocus(modal);
  }

  /* Fechar modais */
  function closeAddEntrada() {
    overlay.classList.remove('show');
    overlay.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
    removeTrap();
    if (lastFocusedElement) lastFocusedElement.focus();
  }

function closeAddSaida() {
    overlay.classList.remove('show');
    overlay.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
    removeTrap();
    if (lastFocusedElement) lastFocusedElement.focus();
}

  /* Validação simples */
  function validateInput(value) {
    return value && value.trim().length > 0;
  }

  form.addEventListener('submit', (e)=>{
    e.preventDefault();
    if(!validateInput(input.value)){
      errorMsg.classList.add('show');
      input.setAttribute('aria-invalid','true');
      input.focus();
      return;
    }
    errorMsg.classList.remove('show');
    input.removeAttribute('aria-invalid');
    console.log('Valor enviado:', input.value);
    closeAddEntrada();
  });

  /* Eventos */
  openEntrada.addEventListener('click', openAddEntrada);
  openSaida.addEventListener('click', openAddSaida);

  closeEntrada.addEventListener('click', closeAddEntrada);
  closeSaida.addEventListener('click', closeAddSaida);

  overlay.addEventListener('mousedown', (e)=>{
    if(!modal.contains(e.target)) closeAddEntrada();
  });

  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape' && overlay.classList.contains('show')) closeAddEntrada();
  });

  /* Trap focus simples */
  function trapFocus(container){
    const focusableSelectors = 'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, [tabindex]:not([tabindex="-1"])';
    const nodes = Array.from(container.querySelectorAll(focusableSelectors))
                .filter(n => n.offsetWidth || n.offsetHeight || n.getClientRects().length);
    if(nodes.length === 0) return;
    const first = nodes[0];
    const last = nodes[nodes.length-1];

    focusListener = function(e){
      if(e.key !== 'Tab') return;
      if(e.shiftKey){
        if(document.activeElement === first){ e.preventDefault(); last.focus(); }
      } else {
        if(document.activeElement === last){ e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener('keydown', focusListener);
  }

  function removeTrap(){
    if(focusListener){
      document.removeEventListener('keydown', focusListener);
      focusListener = null;
    }
  }

})();