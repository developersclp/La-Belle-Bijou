// home.js - Versão com 4 cards fixos
document.addEventListener('DOMContentLoaded', function() {
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
    const cardsPorPagina = 4;

    function getCardWidth() {
        // Método preciso: usa o bounding box real
        const cardRect = cards[0].getBoundingClientRect();
        return cardRect.width + 30; // width + gap de 30px definido no track
    }

    function getMaxIndex() {
        // Máximo de páginas baseado em 4 cards por página
        return Math.ceil(cards.length / cardsPorPagina) - 1;
    }

    function updateCarrossel() {
        const deslocamento = currentIndex * cardsPorPagina * getCardWidth();
        track.style.transform = `translateX(-${deslocamento}px)`;
        
        console.log(`Index: ${currentIndex}, Deslocamento: ${deslocamento}px, Card width: ${getCardWidth()}px`);
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

    checkButtons();

    window.addEventListener('resize', () => {
        // Ao redimensionar, mantém a posição atual se possível
        const maxIndex = getMaxIndex();
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
            updateCarrossel();
        }
        checkButtons();
    });
}