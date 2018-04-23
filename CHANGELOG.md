# CHANGELOG

Inception of [Flectra](https://flectrahq.com/) from [Odoo](https://www.odoo.com/).

Flectra is Forked from Odoo v11's commit reference [odoo/odoo@6135e82](https://github.com/odoo/odoo/commit/6135e82d735d5eb3af914f4a838468f6dc33e51d)

As Flectra Team is working on Odoo's fork. It is team's responsibilities to maintaining the updates from Odoo.

This changelog contains things those are improved version by version and also things those are not identical with Odoo.
So, users can consider this **CHANGELOG** to find the differences between **Flectra** and **Odoo(Community Edition)**.


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
