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
            body.style.overflow = 'hidden';
            navbarToggler.setAttribute('aria-expanded', 'true');
        } else {
            closeMenu();
        }
    }

    function closeMenu() {
        navbarCollapse.classList.remove('show');
        overlay.classList.remove('show');
        body.classList.remove('menu-open');
        body.style.overflow = '';
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

icon_perfil = document.querySelector('icon-link')
menu_variavel = document.getElementById('menu-variavel')

function menu_usuario() {
    if (menu_variavel.style.display == 'flex') {

    }
}

icon_perfil.addEventListener('click', menu_usuario)