// home.js - Versão otimizada para cards mobile
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
    const container = secao.querySelector('.produtos-container');

    const emptyMessage = track.querySelector('.empty');
    if (emptyMessage || cards.length === 0) {
        prevBtn.style.display = 'none';
        nextBtn.style.display = 'none';
        return;
    }

    let currentIndex = 0;
    
    function getCardsVisiveis() {
        const containerWidth = container.getBoundingClientRect().width;
        const card = cards[0];
        
        if (!card) return 1;
        
        const cardRect = card.getBoundingClientRect();
        const gap = window.innerWidth < 768 ? 10 : 30; // Gap menor no mobile
        const cardWidth = cardRect.width + gap;
        
        let cardsQueCabem = Math.floor(containerWidth / cardWidth);
        
        // CORREÇÃO: Garante pelo menos 1 card e no máximo 2 no mobile
        if (window.innerWidth < 768) {
            cardsQueCabem = Math.max(1, Math.min(cardsQueCabem, 2));
        } else if (window.innerWidth < 1200) {
            cardsQueCabem = Math.max(2, Math.min(cardsQueCabem, 3));
        } else {
            cardsQueCabem = Math.max(3, Math.min(cardsQueCabem, 4));
        }
        
        return cardsQueCabem;
    }

    function getCardWidth() {
        const card = cards[0];
        if (!card) return 0;
        
        const cardRect = card.getBoundingClientRect();
        const gap = window.innerWidth < 768 ? 10 : 30;
        return cardRect.width + gap;
    }

    function getMaxIndex() {
        const cardsVisiveis = getCardsVisiveis();
        return Math.max(0, Math.ceil(cards.length / cardsVisiveis) - 1);
    }

    function updateCarrossel() {
        const cardsVisiveis = getCardsVisiveis();
        const cardWidth = getCardWidth();
        const deslocamento = currentIndex * cardsVisiveis * cardWidth;
        
        track.style.transform = `translateX(-${deslocamento}px)`;
        track.style.transition = 'transform 0.4s ease'; // Transição mais suave
    }

    function checkButtons() {
        const maxIndex = getMaxIndex();
        const temMultiplasPaginas = maxIndex > 0;
        
        prevBtn.style.display = (currentIndex > 0 && temMultiplasPaginas) ? 'flex' : 'none';
        nextBtn.style.display = (currentIndex < maxIndex && temMultiplasPaginas) ? 'flex' : 'none';
        
        if (maxIndex === 0) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        }
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

    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const novoMaxIndex = getMaxIndex();
            if (currentIndex > novoMaxIndex) {
                currentIndex = 0;
            }
            updateCarrossel();
            checkButtons();
        }, 150);
    });

    // Inicialização
    setTimeout(() => {
        updateCarrossel();
        checkButtons();
    }, 200);
}