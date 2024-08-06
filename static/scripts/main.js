document.addEventListener("DOMContentLoaded", function() {
    const events = document.getElementById("events");
    const renewButton = document.getElementById("renew-button");
    const popup = document.getElementById("popup");
    const themeToggle = document.getElementById("theme-toggle");
    const body = document.body;
    const lightIcon = document.querySelector(".light-icon");
    const darkIcon = document.querySelector(".dark-icon");

    function applyTheme(theme) {
        body.dataset.theme = theme;
    }
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);


    if (themeToggle) {
        themeToggle.addEventListener("click", function() {
            const currentTheme = body.dataset.theme;
            const newTheme = currentTheme === "light" ? "dark" : "light";
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme); 
        });
    }
    if (renewButton) {
        renewButton.addEventListener("click", function() {
            fetch("/renew", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    popup.style.display = "block";
                    setTimeout(() => {
                        popup.style.display = "none";
                    }, 2000);
                })
                .catch(error => console.error("Error:", error));
        });
    }
    
    if (events) {
        const eventSource = new EventSource("/events");
        eventSource.onmessage = function(event) {
            const newElement = document.createElement("div");
            newElement.textContent = event.data;
            events.appendChild(newElement);
            events.scrollTop = events.scrollHeight;
        };

        eventSource.onerror = function(event) {
            const newElement = document.createElement("div");
            newElement.textContent = "Error: Unable to connect to event source.";
            events.appendChild(newElement);
            events.scrollTop = events.scrollHeight;
        };
    }
});
