class Errors:
    error = "Error"
    int_ser_err = "Internal Server Error"
    not_found = "Not Found Error"
    invalid_token = "Invalid token or expired token."
    cntv_credentials = "Could not validate credentials"
    permission = "You do not have permissions."
    not_auth = "Not authenticated"
    alr_exists = "Already Exists"
    doesnt_exist = "Does not exist"

    taken = "Username already taken"
    invalid_cr = "Invalid Credentials Error"
    dsnt_exist = "The user does not exist."
    fld_inc = "Transaction filled incorrectly"
    not_found_doc = "No matching document found"
    trans_sign_inc = "Transaction signature is incorrect"
    wrn_dev_id = "Wrong device id"
    while_ch = "Error while checking"
    pr_nf = "Product not found"
    pr_narr = "Product has not arrived yet"
    qlty_checked = "Quality already checked for this product"
    qlty_ch_nperf = "Quality check not performed for this product"
    qlty_ch_failed = "Product quality check failed. Manager approval required."
    cnnt_be_retnd_to_splrs = (
        "Product quality check passed. Cannot be returned to suppliers."
    )
    invalid_id = "Id is not a valid ObjectId"
    large_file = "Request Entity Too Large"
    unsupported_media = "Unsupported Media Type"
    empty_file = "Empty File Upload"
    failed_upload = "File Upload Failed"

    token_invalid_order_create = "Token invalid"
    busy_employee = "Employee is already assigned"
    dont_started_work = "Employee doesn't started work in this orders"
    order_of_operations_was_broken = "Order processing is inconsistent"


class Messages:
    message = "Message"
    success = "Success"
    qlty_ch_compl = "Quality check was completed successfully"
    file_upload_success = "Files were uploaded successfully"
