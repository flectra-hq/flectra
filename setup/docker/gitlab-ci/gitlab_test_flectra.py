#!/usr/bin/env python3

# Part of code taken from github.com/OCA/maintainer-quality-tools

import re
import os
import shutil
import subprocess
import sys
import uuid
import argparse
from coverage.cmdline import main as coverage_main
import locale

try:
    basestring
except NameError:
    basestring = str

RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
YELLOW_LIGHT = "\033[33m"
CLEAR = "\033[0;m"

# modules that are either added as dependencies for other modules, so better to ignore them for the moment
modules_to_ignore = ["account_analytic_default", "account_bank_statement_import", "account_budget",
                     "account_cancel", "account_check_printing", "account_payment", "account_tax_python",
                     "account_test", "account_voucher", "analytic", "anonymization", "association",
                     "auth_crypt", "auth_ldap", "auth_oauth", "auth_signup", "barcodes", "base_address_city",
                     "base_address_extended", "base_automation", "base_gengo", "base_geolocalize", "base_iban",
                     "base_import", "base_import_module", "base_setup", "base_sparse_field", "base_vat",
                     "base_vat_autocomplete", "bus", "calendar_sms", "crm_livechat",
                     "crm_phone_validation", "crm_project", "decimal_precision", "delivery", "document", "event",
                     "event_sale", "fetchmail", "gamification", "gamification_sale_crm", "google_account",
                     "google_calendar", "google_drive", "google_spreadsheet",
                     "hr_contract", "hr_expense_check", "hr_gamification", "hr_maintenance",
                     "hr_org_chart", "hr_payroll", "hr_payroll_account", "hr_recruitment_survey",
                     "hr_timesheet_attendance", "http_routing", "hw_blackbox_be", "hw_escpos", "hw_posbox_homepage",
                     "hw_posbox_upgrade", "hw_proxy", "hw_scale", "hw_scanner", "hw_screen", "link_tracker",
                     "live_currency_rate", "mass_mailing_event", "mass_mailing_event_track", "membership",
                     "mrp_byproduct", "note_pad", "pad", "pad_project", "password_security",
                     "payment", "payment_adyen", "payment_authorize", "payment_buckaroo", "payment_ogone",
                     "payment_paypal", "payment_payumoney", "payment_sips", "payment_stripe", "payment_transfer",
                     "phone_validation", "portal", "pos_cache", "pos_data_drinks", "pos_discount", "pos_mercury",
                     "pos_reprint", "pos_restaurant", "pos_sale", "procurement_jit", "product", "product_email_template",
                     "product_expiry", "product_extended", "product_margin", "project_timesheet_holidays", "rating",
                     "rating_project", "report_intrastat", "resource", "sale_mrp", "sale_order_dates",
                     "sale_payment", "sale_service_rating", "sale_timesheet", "sales_team", "sms", "stock_dropshipping",
                     "stock_landed_costs", "stock_picking_batch", "survey_crm", "theme_bootswatch", "theme_default",
                     "transifex", "utm", "web", "web_diagram", "web_editor", "web_kanban_gauge", "web_planner",
                     "web_settings_dashboard", "web_tour", "website_crm", "website_crm_partner_assign",
                     "website_crm_phone_validation", "website_customer", "website_event_questions",
                     "website_event_sale", "website_event_track", "website_form", "website_form_project",
                     "website_forum_doc", "website_gengo" , "website_google_map", "website_hr", "website_hr_recruitment",
                     "website_links", "website_livechat", "website_mail", "website_mail_channel", "website_mass_mailing",
                     "website_membership", "website_partner", "website_payment", "website_quote", "website_rating",
                     "website_rating_project", "website_sale_comparison", "website_sale_delivery", "website_sale_digital",
                     "website_sale_management", "website_sale_options", "website_sale_stock", "website_sale_stock_options",
                     "website_sale_wishlist", "website_theme_install", "website_twitter", "theme_art", "theme_hermit",
                     "theme_leith", "theme_techreceptives"]


def colorized(text, color):
    return '\n'.join(
        map(lambda line: color + line + CLEAR, text.split('\n')))


def green(text):
    return colorized(text, GREEN)


def yellow(text):
    return colorized(text, YELLOW)


def red(text):
    return colorized(text, RED)


def yellow_light(text):
    return colorized(text, YELLOW_LIGHT)


fail_msg = red("FAIL")
success_msg = green("Success")


def has_test_errors(fname, dbname, check_loaded=True):
    """
    Check a list of log lines for test errors.
    Extension point to detect false positives.
    """
    # Rules defining checks to perform
    # this can be
    # - a string which will be checked in a simple substring match
    # - a regex object that will be matched against the whole message
    # - a callable that receives a dictionary of the form
    #     {
    #         'loglevel': ...,
    #         'message': ....,
    #     }
    errors_ignore = [
        'Mail delivery failed',
        'failed sending mail',
    ]
    errors_report = [
        lambda x: 'loglevel' in x and x['loglevel'] == 'CRITICAL',
        'At least one test failed',
        'no access rules, consider adding one',
        'invalid module names, ignored',
    ]

    def make_pattern_list_callable(pattern_list):
        for i in range(len(pattern_list)):
            if isinstance(pattern_list[i], basestring):
                regex = re.compile(pattern_list[i])
                pattern_list[i] = lambda x, regex=regex: \
                    regex.search(x['message'])
            elif hasattr(pattern_list[i], 'match'):
                regex = pattern_list[i]
                pattern_list[i] = lambda x, regex=regex: \
                    regex.search(x['message'])

    make_pattern_list_callable(errors_ignore)
    make_pattern_list_callable(errors_report)

    print("-" * 10)
    # Read log file removing ASCII color escapes:
    # http://serverfault.com/questions/71285
    color_regex = re.compile(r'\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')
    log_start_regex = re.compile(r'^.*(?P<loglevel>(INFO|WARNING|DEBUG|ERROR|CRITICAL)).*?: (?P<message>.*\S)\s*$')
    log_records = []
    last_log_record = dict.fromkeys(log_start_regex.groupindex.keys())
    with open(fname, encoding='utf-8') as log:
        for line in log:
            line = color_regex.sub('', line)
            if sys.stdout.encoding != 'UTF-8':
                line = line.encode('ascii', 'ignore').decode('ascii')
            match = log_start_regex.match(line)
            if match:
                last_log_record = match.groupdict()
                log_records.append(last_log_record)
            else:
                last_log_record['message'] = '%s\n%s' % (
                    last_log_record['message'], line.rstrip('\n')
                )
    errors = []
    for log_record in log_records:
        ignore = False
        for ignore_pattern in errors_ignore:
            if ignore_pattern(log_record):
                ignore = True
                break
        if ignore:
            break
        print('{0}: {1}'.format(log_record['loglevel'], log_record['message']))
        for report_pattern in errors_report:
            if report_pattern(log_record):
                errors.append(log_record)
                break

    if check_loaded:
        if not [r for r in log_records if 'Modules loaded.' in r['message']]:
            errors.append({'message': "Message not found: 'Modules loaded.'"})

    if errors:
        for e in errors:
            print(e['message'])
        print("-"*10)
    return len(errors)


def run_flectra(type_of_db, server_path, host, port, user, password):
    print("\n creating database for : ", type_of_db)
    try:
        db = str(uuid.uuid1()) + "-" + type_of_db
        
        # Setting locale is needed because of gitlab runner server have
        # other locales
        os.environ["LANG"] = "en_US.UTF-8"
        os.environ["LANGUAGE"] = "en_US:en"
        os.environ["LC_ALL"] = "en_US.UTF-8"
        
        os.environ["PGPASSWORD"] = password
        subprocess.check_call(
                ["createdb", "-U", user, "-h", host, "-p", port, "-T",
                 "template1", db])
    except subprocess.CalledProcessError:
        print("Problem in creating database.")
    else:
        log_file = os.path.join(os.getcwd(), "flectra.log")

        # ugly hack as -i all is broken and does not take all modules into consideration
        # need to remove l10n_* modules from the list as installing them all together
        # creates trouble and build always fails
        addons_path = os.path.join(server_path, "addons")
        if not os.path.isdir(addons_path):
            # Assume we are at integration test level where we can not test performance and client modules
            addons_path = os.path.join(server_path, "flectra", "addons")
            modules_to_ignore.append('test_performance')
            modules_to_ignore.append('website')

        addons = list(
            set([addon.name for addon in os.scandir(addons_path) if addon.is_dir() and "10n" not in addon.name]) - set(
                modules_to_ignore))

        if type_of_db == "all":
            modules_to_init = str(",".join(addons))
        else:
            modules_to_init = "base"

        cmd_flectra = ["unbuffer", "coverage", "run", "--source", server_path]
        cmd_flectra += ["%s/flectra-bin" % (server_path),
                        "--db_host",
                        host,
                        "--db_port",
                        port,
                        "--db_user",
                        user,
                        "--db_password",
                        password,
                        "-d",
                        db,
                        '--db-filter',
                        db,
                        "--addons-path",
                        addons_path,
                        "--log-level=info",
                        "--stop-after-init",
                        "--test-enable",
                        "--init", modules_to_init]
        print("CMD EXECUTED --->>> ", " ".join(cmd_flectra))

        with open(log_file, 'w') as outfile:
            with subprocess.Popen(
                    cmd_flectra,
                    stdout=outfile,
                    bufsize=1,
                    universal_newlines=True) as p:
                returncode = p.wait()
        outfile.close()
        errors = has_test_errors(os.path.join(server_path, log_file), db)
    return {'errors': errors, 'returncode': returncode}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Create Docker Instances....')
    parser.add_argument('--build', dest='build', help='Port For Instance', required=True, default="base")
    parser.add_argument('--server-path', dest='path', help='Flectra Path')
    parser.add_argument('--host', dest='host',
                        help='PostgreSQL Host',
                        default="postgres")
    parser.add_argument('--port', dest='port',
                        help='PostgreSQL Port',
                        default="5432")
    parser.add_argument('--user', dest='user',
                        help='PostgreSQL user',
                        default="flectra")
    parser.add_argument('--password', dest='password',
                        help='PostgreSQL password',
                        default="flectra")
    args = parser.parse_args()
    build = args.build

    if argv is None:
        argv = sys.argv
    res = {}
    server_path = args.path or os.getcwd()
    
    if build == "all":
        res['all'] = run_flectra(
                type_of_db="all",
                server_path=server_path,
                host=args.host,
                port=args.port,
                user=args.user,
                password=args.password,
        )
        errors = 'all' in res and res['all'] and 'errors' in res['all'] and \
                 res['all']['errors']
    
    if build == "base":
        res['base'] = run_flectra(
                type_of_db="base",
                server_path=server_path,
                host=args.host,
                port=args.port,
                user=args.user,
                password=args.password,
        )
        errors = 'base' in res and res['base'] and 'errors' in res['base'] and \
                 res['base']['errors']
    
    print("************ ERRORS ************  : ", errors)
    return errors


if __name__ == '__main__':
    rc = main()
    
    if rc:
        exit(rc)
    
    coverage_main(["report"])
    
    exit(rc)
