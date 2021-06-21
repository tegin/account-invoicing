# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    alternate_payer_id = fields.Many2one(
        "res.partner",
        string="Alternate Payer",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="If set, this partner will be the that we expect to pay or to "
        "be paid by. If not set, the payor is by default the "
        "commercial",
    )

    @api.depends("commercial_partner_id", "alternate_payer_id")
    def _compute_bank_partner_id(self):
        super(
            AccountMove,
            self.filtered(lambda r: not r.alternate_payer_id or not r.is_outbound()),
        )._compute_bank_partner_id()
        for move in self:
            if move.is_outbound() and move.alternate_payer_id:
                move.bank_partner_id = move.alternate_payer_id

    @api.onchange("partner_id", "alternate_payer_id")
    def _onchange_partner_id(self):
        return super()._onchange_partner_id()

    def _recompute_payment_terms_lines(self):
        super()._recompute_payment_terms_lines()
        for invoice in self:
            if invoice.alternate_payer_id:
                invoice.line_ids.filtered(
                    lambda r: r.account_id.user_type_id.type
                    in ("receivable", "payable")
                ).write({"partner_id": invoice.alternate_payer_id.id})
