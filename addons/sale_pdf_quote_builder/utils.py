# Part of Flectra. See LICENSE file for full copyright and licensing details.

import io

from flectra import _
from flectra.exceptions import ValidationError
from flectra.tools import pdf


def _ensure_document_not_encrypted(document):
    if pdf.PdfFileReader(io.BytesIO(document), strict=False).isEncrypted:
        raise ValidationError(_(
            "It seems that we're not able to process this pdf inside a quotation. It is either "
            "encrypted, or encoded in a format we do not support."
        ))
