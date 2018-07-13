# -*- coding: utf-8 -*-
# Part of Odoo, Flectra. See LICENSE file for full copyright and licensing details.
from flectra import api, fields, models, tools, _
from flectra.addons import decimal_precision as dp

from flectra.tools import pycompat
from flectra.tools.translate import html_translate
from flectra.tools import float_is_zero


class ProductTags(models.Model):
    _name = 'product.tags'
    _description = 'Product Tags'
    _order = 'sequence'

    sequence = fields.Integer(help="Gives the sequence order when "
                                   "displaying a list of tags.")
    name = fields.Char(string='Name', required=True, translate=True)

    _sql_constraints = [('name_uniq', 'unique (name)',
                         "Tag name already exists !")]


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brands'
    _order = 'sequence'

    sequence = fields.Integer(help="Gives the sequence order when displaying "
                                   "a list of brands.")
    name = fields.Char(string='Name', required=True, translate=True)
    brand_image = fields.Binary(string='Brand Image')

    _sql_constraints = [('name_uniq', 'unique (name)',
                         'Brand name already exists !')]


class ProductRibbon(models.Model):
    _name = 'product.ribbon'
    _description = 'Product Ribbon'
    _order = 'name'

    name = fields.Char(string='Name', size=20, required=True, translate=True)
    ribbon_color_back = fields.Char(string='Background Color', required=True)
    ribbon_color_text = fields.Char(string='Font Color', required=True)


class ProductViewLimit(models.Model):
    _name = 'product.view.limit'
    _order = 'sequence'

    sequence = fields.Integer(help="Gives the sequence order when "
                                   "displaying a list of rules.")
    name = fields.Integer(string='Limit', required=True)

    _sql_constraints = [('name', 'unique(name)', 'This must be unique!')]


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _default_website(self):
        default_website_id = self.env.ref('website.default_website')
        return [default_website_id.id] if default_website_id else None

    website_ids = fields.Many2many('website', 'website_pricelist_rule_rel',
                                   'pricelist_id', 'website_id',
                                   string="website", default=_default_website,
                                   help='List of websites in which price-list '
                                        'will published.')
    code = fields.Char(string='E-commerce Promotional Code', groups="base.group_user")
    selectable = fields.Boolean(help="Allow the end user to choose this price list")

    def clear_cache(self):
        # website._get_pl() is cached to avoid to recompute at each request the
        # list of available pricelists. So, we need to invalidate the cache when
        # we change the config of website price list to force to recompute.
        website = self.env['website']
        website._get_pl_partner_order.clear_cache(website)

    @api.model
    def create(self, data):
        res = super(ProductPricelist, self).create(data)
        self.clear_cache()
        return res

    @api.multi
    def write(self, data):
        res = super(ProductPricelist, self).write(data)
        self.clear_cache()
        return res

    @api.multi
    def unlink(self):
        res = super(ProductPricelist, self).unlink()
        self.clear_cache()
        return res


class ProductPublicCategory(models.Model):
    _name = "product.public.category"
    _inherit = ["website.seo.metadata"]
    _description = "Website Product Category"
    _order = "sequence, name"

    def _default_website(self):
        default_website_id = self.env.ref('website.default_website')
        return [default_website_id.id] if default_website_id else None

    name = fields.Char(required=True, translate=True)
    parent_id = fields.Many2one('product.public.category', string='Parent Category', index=True)
    child_id = fields.One2many('product.public.category', 'parent_id', string='Children Categories')
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of product categories.")
    # NOTE: there is no 'default image', because by default we don't show
    # thumbnails for categories. However if we have a thumbnail for at least one
    # category, then we display a default image on the other, so that the
    # buttons have consistent styling.
    # In this case, the default image is set by the js code.
    image = fields.Binary(attachment=True, help="This field holds the image used as image for the category, limited to 1024x1024px.")
    image_medium = fields.Binary(string='Medium-sized image', attachment=True,
                                 help="Medium-sized image of the category. It is automatically "
                                 "resized as a 128x128px image, with aspect ratio preserved. "
                                 "Use this field in form views or some kanban views.")
    image_small = fields.Binary(string='Small-sized image', attachment=True,
                                help="Small-sized image of the category. It is automatically "
                                "resized as a 64x64px image, with aspect ratio preserved. "
                                "Use this field anywhere a small image is required.")
    website_ids = fields.Many2many('website', 'website_prod_public_categ_rel',
                                   'website_id', 'category_id',
                                   default=_default_website,
                                   string='Websites', copy=False,
                                   help='List of websites in which '
                                        'category will published.')
    partner_tag_ids = fields.Many2many('res.partner.category',
                                       'partner_public_categ_tags_rel',
                                       'tag_id', 'category_id',
                                       string='Partner Tags',
                                       help='If logged in customers/partners '
                                            'have this tag then this product '
                                            'category will appear to them in '
                                            'E-commerce website.\n\n'
                                            'If empty then it becomes general '
                                            'category which display to any '
                                            'customers/partners.')

    @api.model
    def create(self, vals):
        tools.image_resize_images(vals)
        res = super(ProductPublicCategory, self).create(vals)
        # @todo Flectra:
        # Multi-Website: Check different test-cases for child & parent category
        if res.parent_id:
            res.parent_id.write({
                'website_ids': [(4, website_id.id) for website_id in res.website_ids]
            })
        return res

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(ProductPublicCategory, self).write(vals)
        # @todo Flectra:
        # Multi-Website: Check different test-cases for child & parent category
        if self.parent_id and self.website_ids.ids:
            self.parent_id.write({
                'website_ids': [(4, website_id.id) for website_id in self.website_ids]
            })
        if self.child_id:
            for child_id in self.child_id:
                for website_id in child_id.website_ids:
                    if website_id not in self.website_ids:
                        child_id.write({
                            'website_ids': [(3, website_id.id)]
                        })
        return res

    @api.constrains('parent_id')
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValueError(_('Error ! You cannot create recursive categories.'))

    @api.multi
    def name_get(self):
        res = []
        for category in self:
            names = [category.name]
            parent_category = category.parent_id
            while parent_category:
                names.append(parent_category.name)
                parent_category = parent_category.parent_id
            res.append((category.id, ' / '.join(reversed(names))))
        return res


class ProductTemplate(models.Model):
    _inherit = ["product.template", "website.seo.metadata", 'website.published.mixin', 'rating.mixin']
    _order = 'website_published desc, website_sequence desc, name'
    _name = 'product.template'
    _mail_post_access = 'read'

    def _default_website(self):
        default_website_id = self.env.ref('website.default_website')
        return [default_website_id.id] if default_website_id else None

    website_description = fields.Html('Description for the website', sanitize_attributes=False, translate=html_translate)
    alternative_product_ids = fields.Many2many('product.template', 'product_alternative_rel', 'src_id', 'dest_id',
                                               string='Alternative Products', help='Suggest more expensive alternatives to '
                                               'your customers (upsell strategy). Those products show up on the product page.')
    accessory_product_ids = fields.Many2many('product.product', 'product_accessory_rel', 'src_id', 'dest_id',
                                             string='Accessory Products', help='Accessories show up when the customer reviews the '
                                             'cart before paying (cross-sell strategy, e.g. for computers: mouse, keyboard, etc.). '
                                             'An algorithm figures out a list of accessories based on all the products added to cart.')
    website_size_x = fields.Integer('Size X', default=1)
    website_size_y = fields.Integer('Size Y', default=1)
    website_sequence = fields.Integer('Website Sequence', help="Determine the display order in the Website E-commerce",
                                      default=lambda self: self._default_website_sequence())
    public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category',
                                        help="Categories can be published on the Shop page (online catalog grid) to help "
                                        "customers find all the items within a category. To publish them, go to the Shop page, "
                                        "hit Customize and turn *Product Categories* on. A product can belong to several categories.")
    product_image_ids = fields.One2many('product.image', 'product_tmpl_id', string='Images')

    website_price = fields.Float('Website price', compute='_website_price', digits=dp.get_precision('Product Price'))
    website_public_price = fields.Float('Website public price', compute='_website_price', digits=dp.get_precision('Product Price'))
    website_price_difference = fields.Boolean('Website price difference', compute='_website_price')
    website_ids = fields.Many2many('website', 'website_prod_pub_rel',
                                   'website_id', 'product_id',
                                   string='Websites', copy=False,
                                   default=_default_website,
                                   help='List of websites in which '
                                        'Product will published.')
    ribbon_id = fields.Many2one('product.ribbon', string="Product Ribbon")
    brand_id = fields.Many2one('product.brand', string="Product Brand")
    tag_ids = fields.Many2many('product.tags', string="Product Tags")

    def _website_price(self):
        # First filter out the ones that have no variant:
        # This makes sure that every template below has a corresponding product in the zipped result.
        self = self.filtered('product_variant_id')
        # use mapped who returns a recordset with only itself to prefetch (and don't prefetch every product_variant_ids)
        for template, product in pycompat.izip(self, self.mapped('product_variant_id')):
            template.website_price = product.website_price
            template.website_public_price = product.website_public_price
            template.website_price_difference = product.website_price_difference

    def _default_website_sequence(self):
        self._cr.execute("SELECT MIN(website_sequence) FROM %s" % self._table)
        min_sequence = self._cr.fetchone()[0]
        return min_sequence and min_sequence - 1 or 10

    def set_sequence_top(self):
        self.website_sequence = self.sudo().search([], order='website_sequence desc', limit=1).website_sequence + 1

    def set_sequence_bottom(self):
        self.website_sequence = self.sudo().search([], order='website_sequence', limit=1).website_sequence - 1

    def set_sequence_up(self):
        previous_product_tmpl = self.sudo().search(
            [('website_sequence', '>', self.website_sequence), ('website_published', '=', self.website_published)],
            order='website_sequence', limit=1)
        if previous_product_tmpl:
            previous_product_tmpl.website_sequence, self.website_sequence = self.website_sequence, previous_product_tmpl.website_sequence
        else:
            self.set_sequence_top()

    def set_sequence_down(self):
        next_prodcut_tmpl = self.search([('website_sequence', '<', self.website_sequence), ('website_published', '=', self.website_published)], order='website_sequence desc', limit=1)
        if next_prodcut_tmpl:
            next_prodcut_tmpl.website_sequence, self.website_sequence = self.website_sequence, next_prodcut_tmpl.website_sequence
        else:
            return self.set_sequence_bottom()

    @api.multi
    def _compute_website_url(self):
        super(ProductTemplate, self)._compute_website_url()
        for product in self:
            product.website_url = "/shop/product/%s" % (product.id,)


class Product(models.Model):
    _inherit = "product.product"

    website_price = fields.Float('Website price', compute='_website_price', digits=dp.get_precision('Product Price'))
    website_public_price = fields.Float('Website public price', compute='_website_price', digits=dp.get_precision('Product Price'))
    website_price_difference = fields.Boolean('Website price difference', compute='_website_price')

    def _website_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            price_without_pricelist = taxes.compute_all(p.list_price, pricelist.currency_id)[ret]
            p.website_price_difference = False if float_is_zero(price_without_pricelist - p.website_price, precision_rounding=pricelist.currency_id.rounding) else True
            p.website_public_price = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]

    @api.multi
    def website_publish_button(self):
        self.ensure_one()
        return self.product_tmpl_id.website_publish_button()


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    type = fields.Selection([('radio', 'Radio'), ('select', 'Select'), ('color', 'Color')], default='radio')


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    html_color = fields.Char(string='HTML Color Index', oldname='color', help="Here you can set a "
                             "specific HTML color index (e.g. #ff0000) to display the color on the website if the "
                             "attibute type is 'Color'.")


class ProductImage(models.Model):
    _name = 'product.image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    product_tmpl_id = fields.Many2one('product.template', 'Related Product', copy=True)
