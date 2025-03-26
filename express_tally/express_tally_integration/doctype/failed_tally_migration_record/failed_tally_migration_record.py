# Copyright (c) 2025, Laxman Tandon and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class FailedTallyMigrationRecord(Document):
	def validate(self):
		self.calculate_amount()

	def calculate_amount(self):
		total_amount = 0
		if self.payload:
			payload = json.loads(self.payload)
			if self.voucher_type in ['Sales Invoice', 'Purchase Invoice']:
				for item in payload.get('items', []):
					item_amount = item.get('amount', 0)
					total_amount += float(item_amount)
				for item in payload.get('taxes', []):
					tax_amount = item.get('tax_amount', 0)
					total_amount += float(tax_amount)
			if self.voucher_type == 'Journal Entry':
				for item in payload.get('accounts', []):
					item_amount = item.get('credit', 0)
					total_amount += float(item_amount)
		self.amount = total_amount

@frappe.whitelist()
def retry_failed_voucher(failed_record_id):
	'''
		Method to create missing Voucher
	'''
	docname = None
	if frappe.db.exists('Failed Tally Migration Record', failed_record_id):
		doc = frappe.get_doc('Failed Tally Migration Record', failed_record_id)
		payload = json.loads(doc.payload)
		voucher = frappe.get_doc(payload)
		voucher.save()
		submit_vouchers = frappe.db.get_single_value('Express Tally Settings', 'submit_vouchers')
		if submit_vouchers:
			try:
				voucher.submit()
			except Exception as e:
				frappe.log_error(
                    title="{0} submisison".format(voucher.doctype),
                    message=str(e),
                    reference_doctype=voucher.doctype,
                    reference_name=voucher.name,
                )
		docname = voucher.name
		frappe.db.set_value('Failed Tally Migration Record', failed_record_id, 'reference_document', docname)
		return docname

@frappe.whitelist()
def retry_failed_vouchers(names):
	"""
	    method to bulk create missing Vouchers
	"""
	names = json.loads(names)
	for name in names:
		try:
			retry_failed_voucher(name)
		except:
			pass