// ==UserScript==
// @include       https://plus.google.com/*
// @require       utils.js
// @require       google-common.js
// ==/UserScript==

window.Unity = external.getUnityObject(1);

function isCorrectPage() {
    var i, ids = ['contentPane'];

    for (i = 0; i < ids.length; i++) {
        if (!document.getElementById(ids[i])) {
            return false;
        }
    }

    return true;
}

function getPosts() {
    var container = document.getElementById('contentPane');
    var unreadItems = document.evaluate('//div[@guidedhelpid="streamcontent"]/div/div[contains(@id,"update-")]',
                                        container, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);

    var i, node, icon, author, body, res = [];
    for (i = 0; i < unreadItems.snapshotLength; i++) {
        node = unreadItems.snapshotItem(i);
        icon = document.evaluate('div/div/a/img', node,
                                 null, XPathResult.ANY_UNORDERED_NODE_TYPE, null).singleNodeValue.src;
        author = document.evaluate('div/div/div/header/h3/a', node,
                                   null, XPathResult.ANY_UNORDERED_NODE_TYPE, null).singleNodeValue.textContent;
        body = document.evaluate('div/div/div[3]/div/div', node,
                                 null, XPathResult.ANY_UNORDERED_NODE_TYPE, null).singleNodeValue.textContent;

        res.push({ icon: icon,
                   author: author,
                   body: body });
    }
    return res;
}

function selfTest() {
    var i, readItems = getPosts();

    if (!readItems.length) {
        return;
    }

    for (i = 0; i < readItems.length; i++) {
        if (!readItems[i].icon || !readItems[i].author) {
            return;
        }
    }

    reportTestState('PASS SELF TEST');
}

function markAsRead(items) {
    var i;
    for (i = 0; i < items.length; i++) {
        if (items[i].body) {
            localStorage.setItem(items[i].body, true);
        }
    }
}

function filterReaded(items) {
    return items.filter(function (item) {
        return item.body && !localStorage.getItem(item.body);
    });
}

function showItems(items) {
    var i;
    for (i = 0; i < items.length; i++) {
        localStorage.setItem(items[i].body, true);
        Unity.Notification.showNotification(items[i].author, items[i].body, items[i].icon);
    }
}

function messagingIndicatorSetup() {
    var tabActive = true;

    window.onblur = function () {
        tabActive = false;
    };
    window.onfocus = function () {
        tabActive = true;
    };

    var checkMessangesCount = wrapCallback(function () {
        var i, unreadItems = filterReaded(getPosts());
        var unread = String(unreadItems.length);

        Unity.MessagingIndicator.showIndicator(_("Unread"), { count: unread });
        if (tabActive) {
            markAsRead(unreadItems);
        } else {
            showItems(unreadItems);
        }
    });

    checkMessangesCount();
    setInterval(checkMessangesCount, 1000);

    doMainMenuIntegration(document);

    selfTest();
}

if (isCorrectPage()) {
    Unity.init({ name: "Google+",
		 domain: 'plus.google.com',
		 homepage: 'https://plus.google.com/',
                 iconUrl: "icon://google-plus",
                 onInit: wrapCallback(messagingIndicatorSetup) });
}
