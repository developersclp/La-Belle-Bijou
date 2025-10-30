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
    const emptyMessage = track.querySelector('.empty-message');
    
    if (emptyMessage || cards.length === 0) {
        prevBtn.style.display = 'none';
        nextBtn.style.display = 'none';
        return;
    }

    let currentIndex = 0;

    function getCardsVisiveis() {
        const containerWidth = container.getBoundingClientRect().width;
        const cardWidth = cards[0].getBoundingClientRect().width + 30;

        const cardsQueCabem = Math.floor(containerWidth / cardWidth);

        if (window.innerWidth < 768) {
            return Math.min(Math.max(cardsQueCabem, 1), 2);
        } else {
            return Math.min(Math.max(cardsQueCabem, 3), 4);
        }
    }

    function getCardWidth() {
        // Método preciso: usa o bounding box real
        const cardRect = cards[0].getBoundingClientRect();
        return cardRect.width + 30; // width + gap de 30px definido no track
    }

    function getMaxIndex() {
        // Máximo de páginas baseado em 4 cards por página
        const cardsVisiveis = getCardsVisiveis();
        return Math.max(0, Math.ceil(cards.length / cardsVisiveis) - 1);
    }

    function updateCarrossel() {
        const cardsVisiveis = cardsVisiveis();
        const deslocamento = currentIndex * cardsVisiveis * getCardWidth();
        track.style.transform = `translateX(-${deslocamento}px)`;
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
                currentIndex = novoMaxIndex;
            }

            updateCarrossel();
            checkButtons();
        }, 100);
    });

    checkButtons();

    setTimeout(() => {
        updateCarrossel();
        checkButtons();
    }, 100);
}