/*
 * Dark / light toggle. The initial theme is set by an inline script
 * in base.html, this handles the nav button and giscus.
 */

const GISCUS_ORIGIN = "https://giscus.app";

function setGiscusTheme(theme) {
    const iframe = document.querySelector("iframe.giscus-frame");
    if (!iframe) {
        return;
    }
    const msg = {giscus: {setConfig: {theme: theme}}};
    iframe.contentWindow.postMessage(msg, GISCUS_ORIGIN);
}

function toggleTheme() {
    const root = document.documentElement;
    const theme = root.dataset.theme === "dark" ? "light" : "dark";
    // cross-fade where supported, else switch at once
    if (document.startViewTransition) {
        document.startViewTransition(() => {
            root.dataset.theme = theme;
        });
    } else {
        root.dataset.theme = theme;
    }
    try {
        localStorage.setItem("theme", theme);
    } catch (e) {
        console.warn("can't save theme", e);
    }
    setGiscusTheme(theme);
}

document.getElementById("theme-toggle").addEventListener("click", toggleTheme);

document.addEventListener("keydown", (event) => {
    if (event.key !== "D" || !event.shiftKey) {
        return;
    }
    if (event.ctrlKey || event.altKey || event.metaKey) {
        return;
    }
    // don't hijack typing
    if (event.target.closest("input, textarea, select, [contenteditable]")) {
        return;
    }
    toggleTheme();
});

// giscus posts a message once its iframe is up
window.addEventListener("message", (event) => {
    if (event.origin === GISCUS_ORIGIN) {
        setGiscusTheme(document.documentElement.dataset.theme);
    }
});
