from excel_loader import db


class MapManager:

    def __init__(self):
        self.reload()

    def reload(self):

        db.reload()

        self.map = db.map

    ####################################################

    def get_map(self, department):

        self.reload()

        data = self.map[

            self.map["Department"]
            .astype(str)
            .str.strip()
            .str.lower()

            ==

            department.strip().lower()

        ]

        if data.empty:

            return {}

        return data.iloc[0].to_dict()