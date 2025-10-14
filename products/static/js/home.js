const track = document.querySelector('.carousel-track');
const prevBtn = document.querySelector('.carousel-btn.prev');
const nextBtn = document.querySelector('.carousel-btn.next');
const cards = document.querySelectorAll('.produto-card');

let currentIndex = 0;

// Função para calcular largura do card + gap dinamicamente
function getCardWidth() {
  const cardStyle = getComputedStyle(cards[0]);
  const cardWidth = cards[0].offsetWidth;
  const gap = parseFloat(cardStyle.marginRight) || 0; // pega a margin-right real
  return cardWidth + gap;
}

// Função para calcular o máximo índice do carrossel
function getMaxIndex() {
  const trackParentWidth = track.parentElement.offsetWidth;
  return cards.length - Math.floor(trackParentWidth / getCardWidth());
}

nextBtn.addEventListener('click', () => {
  const maxIndex = getMaxIndex();
  if (currentIndex < maxIndex) {
    currentIndex++;
    track.style.transform = `translateX(-${currentIndex * getCardWidth()}px)`;
  }
});

prevBtn.addEventListener('click', () => {
  if (currentIndex > 0) {
    currentIndex--;
    track.style.transform = `translateX(-${currentIndex * getCardWidth()}px)`;
  }
});

// Ajusta o carrossel ao redimensionar a tela
window.addEventListener('resize', () => {
  track.style.transform = `translateX(-${currentIndex * getCardWidth() + 3000}px)`;
});