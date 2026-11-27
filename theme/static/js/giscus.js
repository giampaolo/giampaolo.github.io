/*
 * Blog comments, backed by giscus + GitHub Discussions. Injects the
 * widget into the .giscus div of comments.html and keeps its theme
 * in sync with the dark mode toggle.
 */

const GISCUS_ORIGIN = "https://giscus.app";

function initGiscus(container) {
    const section = container.closest(".comments");
    const url = new URL(container.dataset.themeUrl, location.href).href;
    let sheet = null;
    let ready = false;
    let pushed = null;

    function isDark() {
        return document.documentElement.dataset.theme === "dark";
    }

    // giscus.css branches on prefers-color-scheme, which inside the
    // iframe follows the OS, not our toggle. Swap the conditions for
    // ones that are always / never true.
    function themeFor(dark) {
        const yes = "(min-width: 0px)";
        const no = "(min-width: 99999px)";
        const css = sheet
            .replace(/\(prefers-color-scheme:\s*dark\)/g, dark ? yes : no)
            .replace(/\(prefers-color-scheme:\s*light\)/g, dark ? no : yes);
        return "data:text/css;base64," + btoa(css);
    }

    function inject() {
        const attrs = {
            "data-repo": container.dataset.repo,
            "data-repo-id": container.dataset.repoId,
            "data-category": container.dataset.category,
            "data-category-id": container.dataset.categoryId,
            "data-mapping": "specific",
            "data-term": container.dataset.term,
            // without it giscus matches by a fuzzy title search
            "data-strict": "1",
            "data-reactions-enabled": "1",
            "data-emit-metadata": "0",
            "data-input-position": "top",
            "data-theme": sheet ? themeFor(isDark()) : url,
            "data-lang": "en",
            "data-loading": "lazy",
        };
        pushed = isDark();

        const script = document.createElement("script");
        script.src = GISCUS_ORIGIN + "/client.js";
        script.crossOrigin = "anonymous";
        script.async = true;
        for (const [name, value] of Object.entries(attrs)) {
            script.setAttribute(name, value);
        }
        // a blocked script fires "error", so the section stays hidden
        script.addEventListener("load", () => {
            section.removeAttribute("hidden");
        });
        container.appendChild(script);
    }

    function push() {
        if (!ready || !sheet || isDark() === pushed) {
            return;
        }
        const frame = document.querySelector("iframe.giscus-frame");
        if (!frame || !frame.contentWindow) {
            return;
        }
        const dark = isDark();
        const msg = { giscus: { setConfig: { theme: themeFor(dark) } } };
        frame.contentWindow.postMessage(msg, GISCUS_ORIGIN);
        pushed = dark;
    }

    new MutationObserver(push).observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-theme"],
    });

    // contentWindow exists well before giscus can receive messages
    window.addEventListener("message", (event) => {
        if (
            event.origin !== GISCUS_ORIGIN || !event.data ||
            !event.data.giscus
        ) {
            return;
        }
        ready = true;
        push();
    });

    // giscus fetches the theme with crossorigin="anonymous", which
    // needs CORS and is blocked from localhost. Inlining it as a
    // data: URL avoids both.
    fetch(url)
        .then((resp) => {
            if (!resp.ok) {
                throw new Error(resp.status);
            }
            return resp.text();
        })
        .then((css) => {
            sheet = css;
        })
        .catch((err) => {
            console.warn("giscus: can't inline theme, using its URL", err);
        })
        .finally(inject);
}

const giscusContainer = document.querySelector(".giscus");
if (giscusContainer) {
    initGiscus(giscusContainer);
}
