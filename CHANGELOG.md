# CHANGELOG

Inception of [Flectra](https://www.flectrahq.com/) from [Odoo](https://www.odoo
.com/).

Flectra is Forked from Odoo v11's commit reference [odoo/odoo@6135e82](https://github.com/odoo/odoo/commit/6135e82d735d5eb3af914f4a838468f6dc33e51d)

As Flectra Team is working on Odoo's fork. It is team's responsibilities to maintaining the updates from Odoo.

This changelog contains things those are improved version by version and also things those are not identical with Odoo.
So, users can consider this **CHANGELOG** to find the differences between **Flectra** and **Odoo(Community Edition)**.

Introduction


## [1.7.0] - Firecrown - 2020-05-29
### Added

- Upstream patches and Security Fixes
- Allow admins to select chatter position (bottom or sidebar).
- Allow enabling debug mode from environment variable FLECTRA_DEBUG_MODE

### Fixes
- #184 Inconsistent access to res.config.settings in multiple modules made only for flectra
- #186 Error: ‘ir.mail_server’ object has no attribute ‘keep_days’ while selecting outgoing mail server in invoice template
- #196 Unable to archive project
- #217 Enhance and fix tests for default discount modules
- #218 Helpdesk Stage: wrong security rule
- #225 GitLab CI logic breaks building needed packages
- #228 Checksum file size/check sum error on deb package 1.6.20200201
- #230 Overlapping on multi line fields
- #234 Debian archive InRelease hash mismatch; no packages since 03-19
- #235 TypeError: required field "posonlyargs" missing from arguments
- #238 Account cash rounding must be company specific
- [FIX] website_sale wrong images displayed in products view
- [FIX] rest_api when single database
- [FIX] Use of negative qty in sale orders of stock products
- [FIX] allow BOM with same template but different variants
- [IMP] [Project.Task] Remove confusing priority field from the title.


## [1.6.0] - Firecrown - 2019-03-28
### Added

- Database backup and Restore via Shell
- Keyboard Shortcuts
- Upstream patches and Security Fixes

### Fixes
- #163 No access to certain terms for translation
- #155 german translation
- #172 Flectra 1.5 Bad Request - Session expired (invalid CSRF token) at Login


## [1.5.0] - Rufous - 2018-10-31
### Added

- One Click App Install
- Email Digest
- United Arab Emirates (UAE) Accounting Localization
- Automated Abandon Cart Recovery
- Inter-Company Transaction (Extra Addons)
- Email Validation (Extra Addons)

### Fixes
- #95 Installation issue with Linux Mint 19
- #98 Helpdesk module: Related Partner field changes user_id name and Related Partner
- #99 Hide Helpdesk Issue Form page for not logged in visitors
- #100 Portal User has no rights to access /my/ticket page
- #104 Incorrect layout for billing orders
- #105 Flectra Client Error: TypeError: Cannot read property 'id' of undefined
- #107 Documentation Link Fix
- #126, #131 Multi-Company Multi Accounting plan
- #132 multiple shipment issue with PO
- #134 oauth data error
- #164 Wrong order of taxes in quotation


## [1.4.0] - Lucifer - 2018-08-07
### Added
- Helpdesk
- Recurring Documents
- Capital Asset Management

### Fixes
- #77 Email Invitation Link - Missing Link / Error Traceback in Email invitation
- #79 Printing Current view
- #86 Broken Documentation - Fixed links with documentations
- #87 Invalid State Code with GST for India
- #88 Sale Advance Pricelist Installation Issue
- #91 Point of Sale Issue for Order Creation
- [ALL] upstream patching till 48803ecd0ed1d628261b10c57f32657e100038f7

## [1.3.0] - Sunbeam - 2018-06-21
### Added
- Blanket Sales Orders
- Blanket Purchase Orders
- Advance Pricelist Porting For Ecommerce
- Stock Ageing Report
- Stock Cycle Count

### Fixes
- #60 Thumbnail Error
- #67 OAUTHLIB ERROR in Flectra Rest API for Windows
- #69 Menu Edit error
- #70 access_token header not found REST API
- #71 ERROR IN REST API AUTHENTICATION
- #73 REST API BUGS
- #74 ValueError for module license opl-1
- #75 Print current view with CTRL+P will also print the main menu
- [Invoicing] Fiscal Period is now visible in Invoicing Configuration
- [Invoicing] HSN calculation issue on gstr-2 summary
- [Invoicing] indian chart of account issue, gst traceback on partner form
- [Invoicing] singapore account tax group
- [Ecommerce] Search criteria can be cleared from ecommerce search bar
- [Ecommerce] Translation Issue of Theme Selector Dropdown
- [Ecommerce] Website Menu write() call fixed with unknown fields: 'is_homepage' while changing menu sequence on website
- [Ecommerce] product page filter for radio button

## [1.2.0] - WoodStar - 2018-04-23
### Added
- Manage product category visibility on website by partners/customers tags
- Cash Flow Report
- GST Reporting for Indian Localization
- GST Reporting for Singapore Localization
- Advance Pricelist Module
- Themes for Website
    - Theme Leith

### Fixes
- #50, #51 website_hr module bug
- #48 Kanban image display issue
- #43 Menu bookmark issue
- #59 website_sale migration issue

## [1.1.0] - Hermit - 2018-03-19
### Added
- Favorite Menu Book Marking in Search
- ISO Country Code with Size of 3
- Shop Page Layout Variants
- Layered Navigation for Shop Page
- Website RMA (Return Merchandise Authorization)
- Set Cover Image for Project same as Tasks
- Pycharm Templates
- User Documentation
- Purchase Indent
- Themes for Website
    - Theme Hermit

### Fixes
- #5 Sale Report Branch Bug
- #30 , #37 Lead Allocation Bug
- #38 Issue with Current Adding  
- #39 "|" sign after manage databases

## [1.0.0] - Snowcap - 2018-01-25
### Added
- Multi Level Business Branch
- Password Security Policies
- Multi Website for eCommerce
- RMA (Return Merchandise Authorization)
- Gantt View
- eCommerce functionality
    - Product Page Layout
    - Product Quick Info
    - Product Share Options
    - Product Ribbon
    - Shop Page View Option (List / Grid)
    - Shop Page Product View Limit per Page 
- Account Discount Feature
- Sale Discount Feature
- Language Flag Image Support
- REST API
- Project Scrum
- Drag and Drop Multiple Attachment in Form View
- RTL/LTR Language Support
- Themes for Website
    - Theme Art
    - Theme Techreceptives

### Changed
- All namespace related stuff (odoo/openerp >> flectra)
- Backend Theme / New UI/UX
    - More user friendly
    - Less Branding
    - Fresh New Color Palette
    - Fresh New Fonts
- All Apps Icons
- _website_theme_install_ module set to _"installable"=Flase_
- Allow to install multiple themes for multiple website in single instance

### Removed
- Odoo's Enterprise Tags
- Product Options in Edit Mode of Shop Page
    - Size
    - Styles
