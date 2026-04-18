(function () {
    function normalize(pathname) {
        return pathname.replace(/\/+$/, "").toLowerCase();
    }

    const current = normalize(window.location.pathname);
    const links = document.querySelectorAll(".sidebar .nav-link");

    links.forEach((link) => {
        const target = normalize(new URL(link.href, window.location.origin).pathname);
        if (target && current === target) {
            link.classList.add("active");
        }
    });
})();
