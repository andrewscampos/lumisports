(function () {
    function getCookie(name) {
        var eq = name + '=';
        var parts = document.cookie.split(';');
        for (var i = 0; i < parts.length; i++) {
            var c = parts[i].trim();
            if (c.indexOf(eq) === 0) return c.substring(eq.length);
        }
        return null;
    }

    function setCookie(name, value, days) {
        var d = new Date();
        d.setTime(d.getTime() + (days || 365) * 86400000);
        document.cookie = name + '=' + value + ';expires=' + d.toUTCString() + ';path=/';
    }

    function loadTheme() {
        var saved = getCookie('lumisports-theme');
        if (saved) document.documentElement.setAttribute('data-theme', saved);
    }

    function toggleTheme() {
        var root = document.documentElement;
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next);
        setCookie('lumisports-theme', next);
        var btn = document.getElementById('theme-toggle');
        if (btn) {
            btn.innerHTML = next === 'dark'
                ? '<i class="fas fa-sun"></i>'
                : '<i class="fas fa-moon"></i>';
        }
    }

    function setCurrentDate() {
        var el = document.getElementById('current-date');
        if (el) {
            el.textContent = new Date().toLocaleDateString('pt-BR', {
                weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
            });
        }
    }

    function initAdSense() {
        try {
            (window.adsbygoogle = window.adsbygoogle || []).push({});
        } catch (e) { /* AdSense ainda carregando */ }
    }

    loadTheme();
    setCurrentDate();

    var themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAdSense);
    } else {
        initAdSense();
    }
})();
