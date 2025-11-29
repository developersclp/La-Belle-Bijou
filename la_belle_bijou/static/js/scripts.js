// Modificiar o estado do header mobile conforme cliques
document.addEventListener('DOMContentLoaded', function() {
    const navbarToggler = document.querySelector('.custom-toggler');
    const navbarCollapse = document.getElementById('navbarMobile');
    const overlay = document.querySelector('.navbar-overlay');
    const body = document.body;

    function toggleMenu() {
        const isOpening = !navbarCollapse.classList.contains('show');
        
        if (isOpening) {
            navbarCollapse.classList.add('show');
            overlay.classList.add('show');
            body.classList.add('menu-open');
            body.style.position = 'fixed';
            navbarToggler.setAttribute('aria-expanded', 'true');
            navbarToggler.classList.add('bac')
        } else {
            closeMenu();
        }
    }

    function closeMenu() {
        navbarCollapse.classList.remove('show');
        overlay.classList.remove('show');
        body.classList.remove('menu-open');
        body.style.position = '';
        navbarToggler.setAttribute('aria-expanded', 'false');
    }

    navbarToggler.addEventListener('click', toggleMenu);
    overlay.addEventListener('click', closeMenu);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navbarCollapse.classList.contains('show')) {
            closeMenu();
        }
    });

    document.querySelectorAll('#navbarMobile a').forEach(link => {
        link.addEventListener('click', closeMenu);
    });
});

// Ativar e dastivar o modal do perfil do usuário
icon_perfil = document.getElementById('icone-perfil')
menu_variavel = document.getElementById('menu_variavel')
overlay = document.getElementById('overlay')

function impedirScroll() {
    const largura_scroll_bar = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.overflow = 'hidden';
    document.body.style.paddingRight = largura_scroll_bar + 'px';
}

function liberarScroll() {
    document.documentElement.style.overflow = '';
    document.body.style.paddingRight = '';
}

icon_perfil.addEventListener('click', () => {
    menu_variavel.classList.toggle('visivel')
    overlay.classList.toggle('visivel')
    icon_perfil.classList.toggle('ativo')
    document.body.classList.toggle('no_scroll')
    impedirScroll()
})

overlay.addEventListener('click', () => {
    menu_variavel.classList.toggle('visivel')
    overlay.classList.toggle('visivel')
    icon_perfil.classList.toggle('ativo')
    document.body.classList.toggle('no_scroll')
    liberarScroll()
})