/** @flectra-module **/
import { App, whenReady } from "@flectra/owl";
import { PublicReadonlySpreadsheet } from "./public_readonly";
import { templates } from "@web/core/assets";
import { makeEnv, startServices } from "@web/env";
import { session } from "@web/session";
import { _t } from "@web/core/l10n/translation";

(async function boot() {
    flectra.info = {
        db: session.db,
        server_version: session.server_version,
        server_version_info: session.server_version_info,
        isEnterprise: session.server_version_info.slice(-1)[0] === "e",
    };
    flectra.isReady = false;
    const env = makeEnv();
    await startServices(env);
    await whenReady();
    const app = new App(PublicReadonlySpreadsheet, {
        env,
        props: session.spreadsheet_public_props,
        templates,
        translateFn: _t,
        dev: env.debug,
        warnIfNoStaticProps: env.debug,
        translatableAttributes: ["data-tooltip"],
    });
    const root = await app.mount(document.getElementById("spreadsheet-mount-anchor"));
    flectra.__WOWL_DEBUG__ = { root };
    flectra.isReady = true;
})();
