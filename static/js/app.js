(function () {
    function normalize(pathname) {
        return pathname.replace(/\/+$/, "").toLowerCase();
    }

    function appendNotification(notification) {
        const list = document.getElementById("notification-list");
        if (!list) {
            return;
        }

        const item = document.createElement("div");
        item.className = "p-3 border rounded-3 notification-item";
        item.innerHTML = '<div class="fw-semibold"></div><div class="small text-secondary"></div>';
        item.querySelector(".fw-semibold").textContent = notification.title || "Notification";
        item.querySelector(".text-secondary").textContent = notification.message || "";

        if (list.firstChild) {
            list.insertBefore(item, list.firstChild);
        } else {
            list.appendChild(item);
        }
    }

    function connectNotifications() {
        if (!window.location.host || !window.WebSocket) {
            return;
        }

        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socket = new WebSocket(protocol + "://" + window.location.host + "/ws/notifications/");
        socket.onmessage = function (event) {
            try {
                appendNotification(JSON.parse(event.data));
            } catch (error) {
                console.error("Notification parse error", error);
            }
        };
    }

    function bindPreviewInputs() {
        document.querySelectorAll('input[type="file"][data-preview-target]').forEach((input) => {
            input.addEventListener("change", function () {
                const previewTarget = document.querySelector(this.getAttribute("data-preview-target"));
                if (!previewTarget) {
                    return;
                }

                const file = this.files && this.files[0];
                if (!file) {
                    previewTarget.innerHTML = "";
                    return;
                }

                if (file.type.startsWith("image/")) {
                    const reader = new FileReader();
                    reader.onload = function (event) {
                        previewTarget.innerHTML = '<img class="img-fluid rounded" alt="Preview">';
                        previewTarget.querySelector("img").src = event.target.result;
                    };
                    reader.readAsDataURL(file);
                } else {
                    previewTarget.innerHTML = '<div class="alert alert-info mb-0">Selected file: ' + file.name + '</div>';
                }
            });
        });
    }

    const current = normalize(window.location.pathname);
    const links = document.querySelectorAll(".sidebar .nav-link");

    links.forEach((link) => {
        const target = normalize(new URL(link.href, window.location.origin).pathname);
        if (target && current === target) {
            link.classList.add("active");
        }
    });

    connectNotifications();
    bindPreviewInputs();
})();
