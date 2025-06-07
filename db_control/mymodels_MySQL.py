from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    pass


class Customers(Base):
    __tablename__ = 'customers'
    customer_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(100))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(10))


class Items(Base):
    __tablename__ = 'items'
    item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    item_name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)


class Purchases(Base):
    __tablename__ = 'purchases'
    purchase_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(10), ForeignKey("customers.customer_id"))
    purchase_date: Mapped[str] = mapped_column(String(10))


class PurchaseDetails(Base):
    __tablename__ = 'purchase_details'
    detail_id: Mapped[str] = mapped_column(String(10), primary_key=True, autoincrement=True)
    purchase_id: Mapped[str] = mapped_column(String(10), ForeignKey("purchases.purchase_id"))
    item_id: Mapped[str] = mapped_column(String(10), ForeignKey("items.item_id"))
    quantity: Mapped[int] = mapped_column(Integer)


#baby_careのテーブルを追加
class MilkLog(Base):
    __tablename__ = 'milk_log'
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    milktype: Mapped[str] = mapped_column(String(10))
    volume: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime)

#activity_logsのテーブルを追加
class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    activity_type: Mapped[str] = mapped_column(
        String(10), nullable=False
    )
    milktype: Mapped[str] = mapped_column(
        String(10), nullable=False, default=''
    )
    volume: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    diaper_type: Mapped[str] = mapped_column(
        String(10), nullable=False, default=''
    )
    hardness: Mapped[str] = mapped_column(
        String(10), nullable=False, default=''
    )
    diaper_amount: Mapped[str] = mapped_column(
        String(10), nullable=False, default=''
    )
    sleep_state: Mapped[str] = mapped_column(
        String(10), nullable=False, default=''
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime)