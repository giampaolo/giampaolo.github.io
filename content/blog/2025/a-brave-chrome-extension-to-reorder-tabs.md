Title: A Brave / Chrome extension to reorder tabs
Date: 2025-04-02
Tags: js, brave, dotfiles
Authors: Giampaolo Rodola

While browsing, I almost always keep three tabs open: Gmail, Slack, and
Microsoft Teams (for work). I find it convenient to have them always in the
same position (1, 2, and 3), so I can quickly switch to them using keyboard
shortcuts (`alt+1`, `alt+2`, `alt+3`). While the Gmail tab remains in place,
Slack and Teams frequently move because I use them for work, closing them in
the evening and reopening them the next morning. And each time I have to
manually reposition them. To automate this process, I started looking for a
Brave (Chrome) extension but couldn't find one that fully met my needs. So, I
decided to spend a little time writing my own. It turns out it's incredibly
easy. Here's how you can create a simple Brave extension. The same process
should also work for Chrome.

* Put these 2 files in a folder:

`manifest.json`:

```json
{
    "manifest_version": 3,
    "name": "Tab repositioner",
    "version": "1.0",
    "description": "Set position of new tabs",
    "permissions": ["tabs"],
    "background": {
        "service_worker": "background.js"
    }
}
```

`background.js`:

```js
function move_tab(tab, index) {
    if (tab.index != index) {
        console.log(`moving tab '${tab.url}' to position ${index}`);
        chrome.tabs.move(tab.id, { index: index });
    }
}

function move_new_tabs(changeInfo, tab) {
    if ((changeInfo.status === "loading" || changeInfo.status === "complete") && tab.url) {
        if (tab.url.includes("mail.google.com")) { move_tab(tab, 0); }
        if (tab.url.includes("app.slack.com")) { move_tab(tab, 1); }
        if (tab.url.includes("teams.microsoft.com")) { move_tab(tab, 2); }
    }
}

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    move_new_tabs(changeInfo, tab);
});
```

* Go to `brave://extensions/` (`chrome://extensions/` for Chrome).
* Enable `Developer Mode` (top right).
* Click `Load unpacked` and select your folder.
* To observe debug messages printed in the console, click on `Service Worker`.
* After editing `background.js`, click the refresh icon to apply the changes.
