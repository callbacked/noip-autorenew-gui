document.addEventListener("DOMContentLoaded", function() {
    const events = document.getElementById("events");
    const renewButton = document.getElementById("renew-button");
    const checkLogButton = document.getElementById("check-log-button");
    const popup = document.getElementById("popup");
    const themeToggle = document.getElementById("theme-toggle");
    const body = document.body;
    const lightIcon = document.querySelector(".light-icon");
    const darkIcon = document.querySelector(".dark-icon");

    function applyTheme(theme) {
        body.dataset.theme = theme;
        if (theme === "light") {
            lightIcon.style.display = "block";
            darkIcon.style.display = "none";
        } else {
            lightIcon.style.display = "none";
            darkIcon.style.display = "block";
        }
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

    function checkRenewalStatus() {
        return fetch("/is_renewal_running")
            .then(response => response.json())
            .then(data => data.running);
    }

    if (renewButton) {
        renewButton.addEventListener("click", function() {
            fetch("/renew", { method: "POST" })
                .then(response => response.json())
                .then(() => {
                    popup.style.display = "block";
                    const checkStatusInterval = setInterval(() => {
                        checkRenewalStatus()
                            .then(isRunning => {
                                if (!isRunning) {
                                    clearInterval(checkStatusInterval);
                                    popup.style.display = "none";
                                    return fetch("/manual_renew_log");
                                }
                            })
                            .then(response => response.json())
                            .then(data => {
                                const logOutput = document.getElementById("log-output");
                                if (data.log) {
                                    logOutput.textContent = data.log;
                                    showTab('manual-log');
                                } else if (data.error) {
                                    logOutput.textContent = "Error: " + data.error;
                                    showTab('manual-log');
                                }
                            })
                            .catch(error => console.error("Error fetching log:", error));
                    }, 1000);
                })
                .catch(error => console.error("Error starting renewal:", error));
        });
    }

    if (checkLogButton) {
        checkLogButton.addEventListener("click", function() {
            fetch("/manual_renew_log")
                .then(response => response.json())
                .then(data => {
                    const logOutput = document.getElementById("log-output");
                    if (data.log) {
                        logOutput.textContent = data.log;
                        showTab('manual-log');
                    } else if (data.error) {
                        logOutput.textContent = "Error: " + data.error;
                        showTab('manual-log');
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }

    function showTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = content.id === tabId ? 'block' : 'none';
        });
        document.querySelectorAll('.tab-button').forEach(button => {
            button.classList.toggle('active', button.getAttribute('data-tab') === tabId);
        });
    }

    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            showTab(button.getAttribute('data-tab'));
        });
    });

    document.getElementById('export-button').addEventListener('click', function() {
        fetch('/export_accounts')
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'accounts.json'; 
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            })
            .catch(error => console.error('Error exporting accounts:', error));
    });
    
    document.getElementById('import-button').addEventListener('click', function() {
        const form = document.getElementById('import-form');
        const fileInput = form.querySelector('input[type="file"]');
        
        if (fileInput.files.length > 0) {
            form.submit();
        } else {
            fileInput.click();
        }
    });

    const importButton = document.getElementById('import-button');
    const fileInput = document.querySelector('#import-form input[type="file"]');

    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            importButton.textContent = 'Submit';
            importButton.classList.add('btn-success');
        } else {
            importButton.textContent = 'Import Accounts';
            importButton.classList.remove('btn-success');
        }
    });
    

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
