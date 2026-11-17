// Mark function calls (a name followed by "("). Pygments tokenizes
// them as plain names.
document.querySelectorAll(".highlight .p").forEach((p) => {
    if (!p.textContent.startsWith("(")) {
        return;
    }
    const prev = p.previousElementSibling;
    if (prev && prev.matches(".n, .nb")) {
        prev.classList.add("fn-call");
    }
});
