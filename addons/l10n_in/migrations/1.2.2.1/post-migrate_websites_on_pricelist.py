# -*- coding: utf-8 -*-


def migrate(cr, version):
    mapping = [
        ('SGST Payable', '1_p11232'),
        ('TDS Receivable', '1_p10054'),
    ]
    for item in mapping:
        cr.execute("update account_account set name='%s' where id in ("
                   "select res_id from ir_model_data where "
                   "model='account.account' and module='l10n_in' and "
                   "name='%s')" % item)
