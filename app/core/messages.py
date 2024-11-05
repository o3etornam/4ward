MESSAGES = {
    1: {
        "Type": "response",
        "Message": "Welcome to NUMA!\n\n Enter your meter number",
        "Label": "Welcome page",
        "DataType": "input",
        "FieldType": "number",
    },
    2: {
        "Type": "response",
        "Message": "",
        "Label": "amount",
        "DataType": "input",
        "FieldType": "decimal",
    },
    3: {
        "Type": "AddToCart",
        "Message": "The request has been submitted. Please wait for a payment prompt soon",
        "Item": {"ItemName": "Send Money", "Qty": 1, "Price": 0.0},
        "Label": "The request has been submitted. Please wait for a payment prompt soon",
        "DataType": "display",
        "FieldType": "text",
    },
}


TOKEN_ERROR_MESSAGES = {
    "0": "Success",
    "3": "Failed to calculate the fee",
    "4": "Failed to connect to LAPIS server",
    "5": "Failed to save bill record into the database",
    "10": "Invalid meter number",
    "11": "Customer does not exist",
    "12": "Customer account status is abnormal",
    "13": "Invalid platform ID",
    "20": "Invalid payment",
    "22": "Payment is too much, exceeds maximum purchase limitation",
    "23": "Payment is too little, less than the additional fee",
    "40": "Invalid transaction ID",
    "41": "Transaction ID has already been used",
    "42": "Decryption failed, root key may be invalid",
}

PURCHASE_ERROR_MESSAGES = {
    "0": "Success",
    "4": "Failed to connect to LAPIS server",
    "10": "Invalid meter number",
    "11": "Customer does not exist",
    "12": "Customer account status is abnormal",
    "13": "Invalid platform ID",
}
