/*
 * Adds a "copy" button to the top right of every code block.
 */

const COPY_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
const DONE_ICON = '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

async function copyCode(button, pre) {
    try {
        await navigator.clipboard.writeText(pre.innerText);
    } catch (e) {
        console.warn("can't copy to clipboard", e);
        return;
    }
    button.innerHTML = DONE_ICON;
    button.classList.add("copied");
    clearTimeout(button.resetTimer);
    button.resetTimer = setTimeout(() => {
        button.innerHTML = COPY_ICON;
        button.classList.remove("copied");
    }, 1500);
}

for (const pre of document.querySelectorAll(".highlight > pre")) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "copy-code";
    button.title = "Copy";
    button.setAttribute("aria-label", "Copy code");
    button.innerHTML = COPY_ICON;
    button.addEventListener("click", () => copyCode(button, pre));
    pre.parentElement.appendChild(button);
}
