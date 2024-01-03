/** @flectra-module **/

import { Component } from "@flectra/owl";

export class FileUploadProgressContainer extends Component {}
FileUploadProgressContainer.template = "web.FileUploadProgressContainer";
FileUploadProgressContainer.props = {
    Component: { optional: false },
    shouldDisplay: { type: Function, optional: true },
    fileUploads: { type: Object },
};
