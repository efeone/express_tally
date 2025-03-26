frappe.listview_settings["Failed Tally Migration Record"] = {
    onload: function (listview) {
        listview.page.add_action_item(__("Retry"), function () {
            listview.call_for_selected_items("express_tally.express_tally_integration.doctype.failed_tally_migration_record.failed_tally_migration_record.retry_failed_vouchers");
        });
    },
};