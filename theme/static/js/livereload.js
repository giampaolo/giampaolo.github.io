// Dev only: reload the page when "make autoreload" rebuilds it.

let lastModified = null;

setInterval(async () => {
    let resp;
    try {
        resp = await fetch(location.href, { cache: "no-store" });
    }
    catch (e) {
        return; // server restarting
    }
    const lm = resp.headers.get("Last-Modified");
    if (!resp.ok || !lm) {
        return; // page being rebuilt
    }
    if (lastModified !== null && lm !== lastModified) {
        location.reload();
    }
    lastModified = lm;
}, 1000);
