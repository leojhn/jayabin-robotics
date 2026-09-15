from excel_loader import db


class FAQManager:

    def __init__(self):
        self.reload()

    def reload(self):

        db.reload()

        self.faq = db.faq

    def get_all_faqs(self):

        self.reload()

        return self.faq.to_dict(orient="records")