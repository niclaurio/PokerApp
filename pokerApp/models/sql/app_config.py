from . import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


class AppConfig(Base):
    __tablename__ = "app_configs"
    key: Mapped[str] = mapped_column(String(30), primary_key=True)
    value: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(100), unique=True)

    @classmethod
    def update_rows_to_insert_initially(cls):
        data = [
            {"key": "vat", "value": "0.2", "description": "Value-added tax rate"},
            {
                "key": "app_commission_match",
                "value": "0.05",
                "description": "Percentage commission the app earns from each match",
            },
            {
                "key": "app_commission_cashgame",
                "value": "0.075",
                "description": "Percentage commission the app earns from each cash game",
            },
            {
                "key": "basic_match_fee",
                "value": "2.50",
                "description": "Basic fee for a match",
            },
            {
                "key": "basic_cashgame_fee",
                "value": "20",
                "description": "Basic fee for a cash game",
            },
            {
                "key": "basic_big_blind_increasing",
                "value": "12",
                "description": "Amount by which the big blind increases in the game",
            },
            {
                "key": "basic_starting_big_blind",
                "value": "12",
                "description": "Starting big blind amount in the game",
            },
            {
                "key": "minimum_point_earned",
                "value": "40",
                "description": "Minimum points winners can earn",
            },
        ]

        Base.models_to_insert_initially[cls] = data
