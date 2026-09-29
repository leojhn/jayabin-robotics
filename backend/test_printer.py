import win32print


PRINTER_NAME = "KPOS_216"


def print_test_receipt():

    receipt = """

             CITY HOSPITAL
          CONSULTANT PAYMENT RECEIPT

----------------------------------------

              TOKEN NUMBER

                 A-001

----------------------------------------

Receipt No        TEST-001
Date              25/08/2026
Time              12:30 PM

----------------------------------------

Patient ID        PAT-001
Patient Name      TEST PATIENT

Consultant        Dr. Test Doctor

----------------------------------------

Consultation Fee              Rs. 290

----------------------------------------

TOTAL                         Rs. 290
PAID

----------------------------------------

Payment Method                CASH

Status                        PAID


              Thank You
             CITY HOSPITAL




"""


    try:

        # ESC/POS initialize printer
        ESC = b"\x1b"
        GS = b"\x1d"

        INIT = ESC + b"@"

        # Encode receipt
        receipt_data = receipt.encode(
            "cp437",
            errors="replace"
        )

        # Feed paper
        FEED = b"\n\n\n\n\n"

        # Cut paper
        CUT = GS + b"V\x00"


        final_data = (
            INIT
            + receipt_data
            + FEED
            + CUT
        )


        print(
            f"Opening printer: {PRINTER_NAME}"
        )


        printer_handle = win32print.OpenPrinter(
            PRINTER_NAME
        )


        try:

            job_id = win32print.StartDocPrinter(

                printer_handle,

                1,

                (
                    "HMS Printer Test",
                    None,
                    "RAW"
                )

            )


            win32print.StartPagePrinter(
                printer_handle
            )


            bytes_written = win32print.WritePrinter(

                printer_handle,

                final_data

            )


            win32print.EndPagePrinter(
                printer_handle
            )


            win32print.EndDocPrinter(
                printer_handle
            )


            print("\n==============================")

            print("PRINT TEST SUCCESSFUL")

            print(f"Printer: {PRINTER_NAME}")

            print(f"Job ID: {job_id}")

            print(
                f"Bytes sent: {bytes_written}"
            )

            print("==============================\n")


        finally:

            win32print.ClosePrinter(
                printer_handle
            )


    except Exception as e:

        print("\n==============================")

        print("PRINT TEST FAILED")

        print(str(e))

        print("==============================\n")


if __name__ == "__main__":

    print_test_receipt()