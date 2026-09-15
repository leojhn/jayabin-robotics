import html as html_lib
import re
from html.parser import HTMLParser
from escpos.printer import Usb

# ==========================================================
# HTML -> RECEIPT DATA (FALLBACK PARSER)
# ==========================================================

class ReceiptHTMLParser(HTMLParser):
    """Extracts receipt values from HTML tags with target IDs."""

    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr",
        "img", "input", "link", "meta", "param",
        "source", "track", "wbr"
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.values = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        element_id = attrs.get("id")
        if tag.lower() not in self.VOID_TAGS:
            self.stack.append((tag.lower(), element_id))

    def handle_endtag(self, tag):
        tag = tag.lower()
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        for tag, element_id in reversed(self.stack):
            if element_id:
                self.values.setdefault(element_id, []).append(data)
                break

    def get_values(self):
        result = {}
        for key, pieces in self.values.items():
            value = html_lib.unescape("".join(pieces))
            value = re.sub(r"\s+", " ", value).strip()
            result[key] = value
        return result


# ==========================================================
# THERMAL PRINTER
# ==========================================================

class ThermalPrinter:
    VENDOR_ID = 0x4B43
    PRODUCT_ID = 0x3830
    IN_EP = 0x81
    OUT_EP = 0x02
    WIDTH = 48  # Caysn CN811-U, 80-mm paper, Font A

    def __init__(self):
        self.printer_name = "Caysn CN811-U"

    def connect(self):
        return Usb(
            idVendor=self.VENDOR_ID,
            idProduct=self.PRODUCT_ID,
            in_ep=self.IN_EP,
            out_ep=self.OUT_EP
        )

    def clean(self, value, default="-"):
        val_str = str(value if value is not None else "").strip()
        return val_str if val_str else default

    def separator(self):
        return "-" * self.WIDTH

    def center(self, text):
        text = str(text)
        if len(text) > self.WIDTH:
            text = text[:self.WIDTH]
        return text.center(self.WIDTH)

    def pair(self, label, value):
        label = str(label).strip()
        value = self.clean(value)

        if len(label) + 2 + len(value) <= self.WIDTH:
            spaces = self.WIDTH - len(label) - len(value)
            return label + (" " * max(2, spaces)) + value

        words = value.split()
        wrapped = []
        current = ""
        for word in words:
            if not current:
                current = word
            elif len(current) + 1 + len(word) <= self.WIDTH - 2:
                current += " " + word
            else:
                wrapped.append("  " + current)
                current = word

        if current:
            wrapped.append("  " + current)

        return label + "\n" + "\n".join(wrapped)

    def html_to_receipt(self, content):
        parser = ReceiptHTMLParser()
        parser.feed(str(content))
        values = parser.get_values()

        return {
            "receiptNo": values.get("receiptNo", ""),
            "date": values.get("date", ""),
            "time": values.get("time", ""),
            "patientId": values.get("patientId", ""),
            "patientName": values.get("patientName", ""),
            "appointmentId": values.get("appointmentId", ""),
            "token": values.get("tokenNo", "A-001"),
            "consultant": values.get("consultant", ""),
            "amount": values.get("amount", ""),
            "paymentMethod": values.get("paymentMethod", ""),
            "status": values.get("status", "PAID")
        }

    def print_receipt(self, receipt):
        printer = None

        try:
            printer = self.connect()

            token = self.clean(receipt.get("token"), "A-001")
            receipt_no = self.clean(receipt.get("receiptNo"))
            date = self.clean(receipt.get("date"))
            time = self.clean(receipt.get("time"))
            patient_id = self.clean(receipt.get("patientId"))
            patient_name = self.clean(receipt.get("patientName"))
            appointment_id = self.clean(receipt.get("appointmentId"))
            consultant = self.clean(receipt.get("consultant"))
            payment_method = self.clean(receipt.get("paymentMethod")).upper()
            status = self.clean(receipt.get("status"), "PAID").upper()
            amount = self.clean(receipt.get("amount"), "0")

            # Reset printer & Print Header
            printer.hw("reset")
            printer.set(align="center", bold=False, font="a", width=1, height=1)
            printer.text(self.separator() + "\n")
            printer.text("CITY HOSPITAL\n")
            printer.text("CONSULTANT PAYMENT RECEIPT\n")
            printer.text(self.separator() + "\n")

            # Token (2x size)
            printer.set(align="center", bold=True, font="a", width=1, height=1)
            printer.text("TOKEN NUMBER\n")
            printer.set(align="center", bold=True, font="a", width=2, height=2)
            printer.text(token + "\n")

            # Reset scaling for body details
            printer.set(align="left", bold=False, font="a", width=1, height=1)
            printer.text(self.separator() + "\n")

            # Receipt Details
            printer.text(self.pair("Receipt No", receipt_no) + "\n")
            printer.text(self.pair("Date", date) + "\n")
            printer.text(self.pair("Time", time) + "\n")
            printer.text(self.separator() + "\n")

            printer.text(self.pair("Patient ID", patient_id) + "\n")
            printer.text(self.pair("Patient Name", patient_name) + "\n")
            printer.text(self.pair("Appointment ID", appointment_id) + "\n")
            printer.text(self.separator() + "\n")

            printer.text(self.pair("Consultant", consultant) + "\n")
            printer.text(self.pair("Payment Method", payment_method) + "\n")
            printer.text(self.pair("Status", status) + "\n")
            printer.text(self.separator() + "\n")

            # Total
            printer.set(align="left", bold=True, font="a", width=1, height=1)
            printer.text(self.pair("TOTAL AMOUNT", "Rs. " + amount) + "\n")
            printer.text(self.separator() + "\n")

            # Paid Status & Footer
            printer.set(align="center", bold=True, font="a", width=1, height=1)
            printer.text("PAID\n")
            printer.text(self.separator() + "\n")
            printer.text("THANK YOU\n")
            printer.text("CITY HOSPITAL\n\n\n")

            printer.cut()

            return {
                "success": True,
                "printer": self.printer_name,
                "job": "USB-ESC-POS"
            }

        except Exception as e:
            raise RuntimeError(f"ESC/POS printer error: {str(e)}")

        finally:
            if printer is not None:
                try:
                    printer.close()
                except Exception:
                    pass

    def print_html(self, content):
        if isinstance(content, dict):
            # Direct JSON payload handling
            payload = content.get("html", content) if isinstance(content, dict) and "html" in content and isinstance(content["html"], dict) else content
            receipt = payload
        else:
            # HTML string fallback handling
            receipt = self.html_to_receipt(content)

        return self.print_receipt(receipt)


# Global instance
printer = ThermalPrinter()
