// home.js - Versão corrigida para múltiplos carrosséis

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar todos os carrosséis
    document.querySelectorAll('.produtos-secao').forEach((secao) => {
        initCarrossel(secao);
    });
});

function initCarrossel(secao) {
    const track = secao.querySelector('.produtos-track');
    const prevBtn = secao.querySelector('.produtos-btn.prev');
    const nextBtn = secao.querySelector('.produtos-btn.next');
    const cards = track.querySelectorAll('.produto-card');

    if (cards.length === 0) return;

    let currentIndex = 0;

    function getCardWidth() {
        const cardStyle = getComputedStyle(cards[0]);
        const cardWidth = cards[0].offsetWidth;
        const gap = parseFloat(cardStyle.marginRight) || 0;
        return cardWidth + gap;
    }

    function getMaxIndex() {
        const trackParentWidth = track.parentElement.offsetWidth;
        const cardsToShow = Math.floor(trackParentWidth / getCardWidth());
        return Math.max(0, cards.length - cardsToShow);
    }

    function updateCarrossel() {
        track.style.transform = `translateX(-${currentIndex * getCardWidth()}px)`;
    }

    function checkButtons() {
        const maxIndex = getMaxIndex();
        prevBtn.style.display = currentIndex > 0 ? 'flex' : 'none';
        nextBtn.style.display = currentIndex < maxIndex ? 'flex' : 'none';
    }

    nextBtn.addEventListener('click', () => {
        const maxIndex = getMaxIndex();
        if (currentIndex < maxIndex) {
            currentIndex++;
            updateCarrossel();
            checkButtons();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarrossel();
            checkButtons();
        }
    });

    // Esconder botões inicialmente se não forem necessários
    checkButtons();

    // Recalcular ao redimensionar
    window.addEventListener('resize', () => {
        const maxIndex = getMaxIndex();
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
            updateCarrossel();
        }
        checkButtons();
    });
}