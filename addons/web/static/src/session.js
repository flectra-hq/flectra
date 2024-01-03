/** @flectra-module **/

export const session = flectra.__session_info__ || {};
delete flectra.__session_info__;
