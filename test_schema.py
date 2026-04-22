import sys
sys.path.insert(0, 'backend')

from app.models import Appointment
from app.schemas import AppointmentResponse
from uuid import uuid4, UUID
from datetime import datetime

# 模拟一个 Appointment 对象
class MockAppointment:
    def __init__(self):
        self.id = uuid4()
        self.user_id = uuid4()
        self.bicycle_id = uuid4()
        self.type = "pick-up"
        self.status = "PENDING"
        self.time_slot_id = None  # NULL 值
        self.appointment_time = datetime.now()
        self.notes = "Test notes"
        self.created_at = datetime.now()

mock_apt = MockAppointment()
print(f"Mock Appointment: id={mock_apt.id}, time_slot_id={mock_apt.time_slot_id}")

try:
    # 尝试序列化
    response = AppointmentResponse.model_validate(mock_apt)
    print(f"✓ 序列化成功！")
    print(f"  id: {response.id}")
    print(f"  user_id: {response.user_id}")
    print(f"  time_slot_id: {response.time_slot_id}")
    print(f"  status: {response.status}")
except Exception as e:
    print(f"✗ 序列化失败：{e}")
    import traceback
    traceback.print_exc()
