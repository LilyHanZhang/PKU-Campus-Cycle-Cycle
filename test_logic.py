# 测试逻辑验证

# 卖家流程
# 预约类型：drop-off（卖家送车到指定地点）
# 时间段类型：pick-up（管理员从指定地点取车）

appointment_type_appointment = "drop-off"  # 预约的 type
appointment_type_timeslot = "pick-up"  # 时间段的 appointment_type

# 验证逻辑（有预约的情况）
# if user_appointment.type == "pick-up" and time_slot.appointment_type != "drop-off":
#     raise HTTPException(...)
# elif user_appointment.type == "drop-off" and time_slot.appointment_type != "pick-up":
#     raise HTTPException(...)

# 卖家流程验证
if appointment_type_appointment == "pick-up" and appointment_type_timeslot != "drop-off":
    print("❌ 验证失败 1")
elif appointment_type_appointment == "drop-off" and appointment_type_timeslot != "pick-up":
    print("❌ 验证失败 2")
else:
    print("✅ 卖家流程验证通过")
    print(f"   预约类型：{appointment_type_appointment}")
    print(f"   时间段类型：{appointment_type_timeslot}")

# 买家流程
# 预约类型：pick-up（买家来取车）
# 时间段类型：drop-off（管理员送车/买家取车）

appointment_type_appointment_buyer = "pick-up"
appointment_type_timeslot_buyer = "drop-off"

if appointment_type_appointment_buyer == "pick-up" and appointment_type_timeslot_buyer != "drop-off":
    print("❌ 验证失败 3")
elif appointment_type_appointment_buyer == "drop-off" and appointment_type_timeslot_buyer != "pick-up":
    print("❌ 验证失败 4")
else:
    print("✅ 买家流程验证通过")
    print(f"   预约类型：{appointment_type_appointment_buyer}")
    print(f"   时间段类型：{appointment_type_timeslot_buyer}")
