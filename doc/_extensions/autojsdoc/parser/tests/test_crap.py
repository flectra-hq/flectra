# -*- coding: utf-8 -*-
"""
Test various crap patterns found in Flectra code to ensure they don't blow up
the parser thingie
"""
from autojsdoc.parser import jsdoc
from support import parse

def test_export_external():
    [mod] = parse("""
    flectra.define('module', function () {
        return $.Deferred().reject();
    });
    """)
    assert isinstance(mod.exports, jsdoc.CommentDoc)
    assert mod.exports.doc == ''

def test_extend_jq():
    parse("""
    flectra.define('a', function (r) {
        $.extend($.expr[':'], { a: function () {} });
        $.fn.extend({ a: function () {} });
    });
    """)

def test_extend_dynamic():
    parse("""
    flectra.define('a', function () {
        foo.bar.baz[qux + '_external'] = function () {};
    });
    """)

def test_extend_deep():
    parse("""
    flectra.define('a', function () {
        var eventHandler = $.summernote.eventHandler;
        var dom = $.summernote.core.dom;
        dom.thing = function () {};

        var fn_editor_currentstyle = eventHandler.modules.editor.currentStyle;
        eventHandler.modules.editor.currentStyle = function () {}
    });
    """)

def test_arbitrary():
    parse("""
    flectra.define('bob', function () {
        var page = window.location.href.replace(/^.*\/\/[^\/]+/, '');
        var mailWidgets = ['mail_followers', 'mail_thread', 'mail_activity', 'kanban_activity'];
        var bob;
        var fldj = foo.getTemplate().baz;
    });
    """)

def test_prototype():
    [A, B] = parse("""
    flectra.define('mod1', function () {
        var exports = {};
        exports.Foo = Backbone.Model.extend({});
        exports.Bar = Backbone.Model.extend({});
        var BarCollection = Backbone.Collection.extend({
            model: exports.Bar,
        });
        exports.Baz = Backbone.Model.extend({});
        return exports;
    });
    flectra.define('mod2', function (require) {
        var models = require('mod1');
        var _super_orderline = models.Bar.prototype;
        models.Foo = models.Bar.extend({});
        var _super_order = models.Baz.prototype;
        models.Bar = models.Baz.extend({});
    });
    """)

