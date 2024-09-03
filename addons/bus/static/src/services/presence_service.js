/** @flectra-module **/

import { EventBus } from "@flectra/owl";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";

export const presenceService = {
    start(env) {
        const LOCAL_STORAGE_PREFIX = "presence";
        const bus = new EventBus();
        let isFlectraFocused = true;
        let lastPresenceTime =
            browser.localStorage.getItem(`${LOCAL_STORAGE_PREFIX}.lastPresence`) ||
            new Date().getTime();

        function onPresence() {
            lastPresenceTime = new Date().getTime();
            browser.localStorage.setItem(`${LOCAL_STORAGE_PREFIX}.lastPresence`, lastPresenceTime);
            bus.trigger("presence");
        }

        function onFocusChange(isFocused) {
            try {
                isFocused = parent.document.hasFocus();
            } catch {
                // noop
            }
            isFlectraFocused = isFocused;
            browser.localStorage.setItem(`${LOCAL_STORAGE_PREFIX}.focus`, isFlectraFocused);
            if (isFlectraFocused) {
                lastPresenceTime = new Date().getTime();
                env.bus.trigger("window_focus", isFlectraFocused);
            }
        }

        function onStorage({ key, newValue }) {
            if (key === `${LOCAL_STORAGE_PREFIX}.focus`) {
                isFlectraFocused = JSON.parse(newValue);
                env.bus.trigger("window_focus", newValue);
            }
            if (key === `${LOCAL_STORAGE_PREFIX}.lastPresence`) {
                lastPresenceTime = JSON.parse(newValue);
                bus.trigger("presence");
            }
        }
        browser.addEventListener("storage", onStorage);
        browser.addEventListener("focus", () => onFocusChange(true));
        browser.addEventListener("blur", () => onFocusChange(false));
        browser.addEventListener("pagehide", () => onFocusChange(false));
        browser.addEventListener("click", onPresence);
        browser.addEventListener("keydown", onPresence);

        return {
            bus,
            getLastPresence() {
                return lastPresenceTime;
            },
            isFlectraFocused() {
                return isFlectraFocused;
            },
            getInactivityPeriod() {
                return new Date().getTime() - this.getLastPresence();
            },
        };
    },
};

registry.category("services").add("presence", presenceService);
