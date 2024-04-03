/** @flectra-module **/

import { BlockUI } from "@web/core/ui/block_ui";
import { patch } from "@web/core/utils/patch";
import { session } from '@web/session';
import { xml } from "@flectra/owl";

patch(BlockUI.prototype, {
    setup(...args) {
        super.setup(...args);
        this.preloader_option = session.preloader_option;
    }
});

BlockUI.template = xml`
    <div t-att-class="state.blockUI ? 'o_blockUI fixed-top d-flex justify-content-center align-items-center flex-column vh-100 bg-black-50' : ''">
      <t t-if="state.blockUI">
        <div t-if="preloader_option == 'style_one'" class="o_spinner mb-4">
            <img src="/web/static/img/spin.svg" alt="Loading..."/>
        </div>
        <div t-if="preloader_option == 'style_two'" class="mb-4 preloader2">
            <div class="loader loader-inner-1">
                <div class="loader loader-inner-2">
                    <div class="loader loader-inner-3">
                    </div>
                </div>
            </div>
        </div>
        <div t-if="preloader_option == 'style_three'" class="mb-4 preloader3">
            <div class="loader-inner">
                <div class="box-1"></div>
                <div class="box-2"></div>
                <div class="box-3"></div>
                <div class="box-4"></div>
            </div>
        </div>
        <div t-if="preloader_option == 'style_four'" class="mb-4 preloader4">
        </div>
        <div t-if="preloader_option == 'style_five'" class="mb-4 preloader5">
            <div class="inner-loader">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="inner-loader">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
            <div class="inner-loader">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
        <div t-if="preloader_option == 'style_six'" class="mb-4 preloader6">
            <div class="box"></div>
            <div class="box"></div>
            <div class="box"></div>
            <div class="box"></div>
            <div class="box"></div>
        </div>
        <div t-if="preloader_option == 'style_seven'" class="mb-4 preloader7">
        </div>
        <div t-if="preloader_option == 'style_eight'" class="mb-4 preloader8">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
        </div>
        <div t-if="preloader_option == 'style_nine'" class="mb-4 preloader9">
        </div>
        <div t-if="preloader_option == 'style_ten'" class="mb-4 preloader10">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
        </div>
        <div t-if="preloader_option == 'style_eleven'" class="mb-4 preloader11">
        </div>
        <div t-if="preloader_option == 'style_twelve'" class="mb-4 preloader12">
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
            <div class="loader-inner"></div>
        </div>
        <div class="o_message text-center px-4">
            <t t-esc="state.line1"/> <br/>
            <t t-esc="state.line2"/>
        </div>
      </t>
    </div>`;
