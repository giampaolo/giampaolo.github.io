/*
 * Floating "back to top" button. Shows up when the user has scrolled
 * down and is moving back up, hides again on downward scroll.
 */

const SHOW_AFTER_PX = 400;
const UP_ICON =
    '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 15l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';

function scrollToTop() {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
        window.scrollTo(0, 0);
        return;
    }
    // the browser's smooth scroll can take ~1s on long pages
    const start = window.scrollY;
    const t0 = performance.now();
    function step(now) {
        const t = Math.min((now - t0) / 300, 1);
        const eased = 1 - Math.pow(1 - t, 3);
        window.scrollTo(0, start * (1 - eased));
        if (t < 1) {
            requestAnimationFrame(step);
        }
    }
    requestAnimationFrame(step);
}

const backToTop = document.createElement("button");
backToTop.type = "button";
backToTop.className = "jump-up";
backToTop.title = "Scroll to top";
backToTop.setAttribute("aria-label", "Scroll to top");
// hidden via opacity, so keep it out of the tab order
backToTop.tabIndex = -1;
backToTop.innerHTML = UP_ICON;
backToTop.addEventListener("click", scrollToTop);
document.body.appendChild(backToTop);

let lastY = window.scrollY;
window.addEventListener("scroll", () => {
    const y = window.scrollY;
    const visible = y < lastY && y > SHOW_AFTER_PX;
    backToTop.classList.toggle("is-visible", visible);
    backToTop.tabIndex = visible ? 0 : -1;
    lastY = y;
}, { passive: true });
