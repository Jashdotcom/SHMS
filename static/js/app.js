(function () {
    function normalize(pathname) {
        return pathname.replace(/\/+$/, "").toLowerCase();
    }

    function appendNotification(notification) {
        const list = document.getElementById("notification-list");
        if (!list) {
            return;
        }

        const emptyState = document.getElementById("notification-empty");
        if (emptyState) {
            emptyState.remove();
        }

        const item = document.createElement(notification.related_url ? "a" : "div");
        item.className = "notification-item dropdown-item";
        if (notification.related_url) {
            item.href = notification.related_url;
        }
        item.innerHTML = '<span class="fw-semibold d-block"></span><span class="small text-secondary d-block"></span><span class="small text-secondary"></span>';
        item.querySelector(".fw-semibold").textContent = notification.title || "Notification";
        item.querySelector(".text-secondary").textContent = notification.message || "";
        item.querySelectorAll(".text-secondary")[1].textContent = "Just now";

        if (list.firstChild) {
            list.insertBefore(item, list.firstChild);
        } else {
            list.appendChild(item);
        }

        updateNotificationCount();
    }

    function updateNotificationCount() {
        const count = document.getElementById("notification-count");
        if (!count) {
            return;
        }

        const current = Number.parseInt(count.textContent.trim(), 10) || 0;
        count.textContent = String(current + 1);
        count.classList.remove("d-none");
    }

    function connectNotifications() {
        if (!window.location.host || !window.WebSocket || !document.getElementById("notification-count")) {
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
        socket.onclose = function (event) {
            if (event.code !== 1000) {
                window.setTimeout(connectNotifications, 3000);
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
