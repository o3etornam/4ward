from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime


class DataTypes(str, Enum):
    INPUT = "input"
    DISPLAY = "display"


class FieldTypes(str, Enum):
    TEXT = "text"
    DECIMAL = "decimal"
    NUMBER = "number"


class Items(BaseModel):
    ItemName: str
    Qty: int
    Price: float


class Types(BaseModel):
    ItemName: str
    Qty: int
    Price: float


class HubtelResponse(BaseModel):
    SessionId: str = ""
    Type: str
    Message: str
    Item: Items | None = None
    Label: str
    DataType: DataTypes
    FieldType: FieldTypes


class HubtelRequest(BaseModel):
    Type: str
    Message: str
    ServiceCode: str
    Operator: str
    ClientState: str | None = None
    Mobile: str
    SessionId: str
    Sequence: int = 1
    Platform: str


class Item(BaseModel):
    ItemId: str
    Name: str
    Quantity: int
    UnitPrice: float


class Payment(BaseModel):
    PaymentType: str
    AmountPaid: float
    AmountAfterCharges: float
    PaymentDate: datetime
    PaymentDescription: str
    IsSuccessful: bool


class OrderInfo(BaseModel):
    CustomerMobileNumber: str
    CustomerEmail: EmailStr | None = None
    CustomerName: str
    Status: str
    OrderDate: datetime
    Currency: str
    BranchName: str
    IsRecurring: bool
    RecurringInvoiceId: str | None = None
    Subtotal: float
    Items: list[Item]
    Payment: Payment


class PayementRequest(BaseModel):
    SessionId: str
    OrderId: str
    ExtraData: dict
    OrderInfo: OrderInfo

class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"


class HubtelCallBackRequest(BaseModel):
    SessionId: str
    OrderId: str
    ServiceStatus: Status
    MetaData: None = None
