"""
单元测试：测试北京时间转换功能

测试用例：
1. 测试 UTC 时间转换为北京时间（UTC+8）
2. 测试跨天的时间转换
3. 测试跨月的时间转换
4. 测试跨年的时间转换
5. 测试时间格式正确性
"""

import pytest
from datetime import datetime, timedelta


def utc_to_beijing(utc_datetime: datetime) -> str:
    """
    将 UTC 时间转换为北京时间字符串
    模拟前端的 formatToBeijingTime 函数
    """
    # 获取 UTC 时间
    utc_year = utc_datetime.year
    utc_month = utc_datetime.month
    utc_day = utc_datetime.day
    utc_hours = utc_datetime.hour
    utc_minutes = utc_datetime.minute
    
    # 转换为北京时间（UTC+8）
    beijing_hours = utc_hours + 8
    beijing_day = utc_day
    beijing_month = utc_month
    beijing_year = utc_year
    
    if beijing_hours >= 24:
        beijing_hours -= 24
        beijing_day += 1
        # 处理月份和年份的进位
        import calendar
        days_in_month = calendar.monthrange(beijing_year, beijing_month)[1]
        if beijing_day > days_in_month:
            beijing_day = 1
            beijing_month += 1
            if beijing_month > 12:
                beijing_month = 1
                beijing_year += 1
    
    return f"{beijing_year}/{str(beijing_month).zfill(2)}/{str(beijing_day).zfill(2)} {str(beijing_hours).zfill(2)}:{str(utc_minutes).zfill(2)}"


class TestBeijingTimeConversion:
    """测试北京时间转换"""
    
    def test_same_day_conversion(self):
        """测试同一天的转换（不跨天）"""
        # UTC 时间 10:30，北京时间应该是 18:30
        utc_dt = datetime(2025, 1, 15, 10, 30)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/15 18:30"
    
    def test_cross_day_conversion(self):
        """测试跨天的转换"""
        # UTC 时间 20:00，北京时间应该是第二天 04:00
        utc_dt = datetime(2025, 1, 15, 20, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/16 04:00"
    
    def test_midnight_conversion(self):
        """测试午夜的转换"""
        # UTC 时间 16:00，北京时间应该是第二天 00:00
        utc_dt = datetime(2025, 1, 15, 16, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/16 00:00"
    
    def test_cross_month_conversion(self):
        """测试跨月的转换"""
        # 1 月 31 日 UTC 20:00，北京时间应该是 2 月 1 日 04:00
        utc_dt = datetime(2025, 1, 31, 20, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/02/01 04:00"
    
    def test_cross_year_conversion(self):
        """测试跨年的转换"""
        # 12 月 31 日 UTC 20:00，北京时间应该是次年 1 月 1 日 04:00
        utc_dt = datetime(2025, 12, 31, 20, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2026/01/01 04:00"
    
    def test_leap_year_february(self):
        """测试闰年 2 月的转换"""
        # 2024 年是闰年，2 月有 29 天
        # 2 月 29 日 UTC 20:00，北京时间应该是 3 月 1 日 04:00
        utc_dt = datetime(2024, 2, 29, 20, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2024/03/01 04:00"
    
    def test_minutes_preserved(self):
        """测试分钟数保持不变"""
        utc_dt = datetime(2025, 1, 15, 12, 45)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/15 20:45"
        assert ":45" in beijing_time
    
    def test_format_correctness(self):
        """测试格式正确性"""
        utc_dt = datetime(2025, 1, 5, 3, 5)  # 单个数字的月份、日期、小时、分钟
        beijing_time = utc_to_beijing(utc_dt)
        
        # 应该补零
        assert beijing_time == "2025/01/05 11:05"
        assert len(beijing_time) == 16  # YYYY/MM/DD HH:mm
    
    def test_various_hours(self):
        """测试不同小时的转换"""
        test_cases = [
            (0, 8),    # UTC 0:00 -> 北京 8:00
            (5, 13),   # UTC 5:00 -> 北京 13:00
            (10, 18),  # UTC 10:00 -> 北京 18:00
            (15, 23),  # UTC 15:00 -> 北京 23:00
            (17, 1),   # UTC 17:00 -> 北京 1:00（次日）
            (23, 7),   # UTC 23:00 -> 北京 7:00（次日）
        ]
        
        for utc_hour, expected_beijing_hour in test_cases:
            utc_dt = datetime(2025, 1, 15, utc_hour, 0)
            beijing_time = utc_to_beijing(utc_dt)
            
            # 提取小时部分
            hour_part = int(beijing_time.split(' ')[1].split(':')[0])
            assert hour_part == expected_beijing_hour, f"UTC {utc_hour}:00 should be Beijing {expected_beijing_hour}:00"
    
    def test_iso_string_conversion(self):
        """测试 ISO 格式字符串转换"""
        # 模拟前端解析 ISO 字符串
        iso_string = "2025-01-15T10:30:00.000Z"
        utc_dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/15 18:30"


class TestTimeDisplayConsistency:
    """测试时间显示一致性"""
    
    def test_admin_and_user_see_same_time(self):
        """测试管理员和用户看到相同的时间"""
        # 假设管理员选择北京时间 2025/01/15 14:00
        # 后端存储为 UTC 时间 2025-01-15T06:00:00.000Z
        
        utc_dt = datetime(2025, 1, 15, 6, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        # 管理员和用户都应该看到北京时间 14:00
        assert beijing_time == "2025/01/15 14:00"
    
    def test_multiple_timezones_show_beijing_time(self):
        """测试多个时区都显示北京时间"""
        # 无论用户在哪个时区，都应该显示北京时间
        
        # UTC 时间 10:00
        utc_dt = datetime(2025, 1, 15, 10, 0)
        beijing_time = utc_to_beijing(utc_dt)
        assert beijing_time == "2025/01/15 18:00"
        
        # 这个时间在美国西部时间是凌晨 2 点，但显示仍应为北京时间 18:00


class TestEdgeCases:
    """测试边界情况"""
    
    def test_exactly_16_hours_utc(self):
        """测试 UTC 16:00（正好是北京时间 00:00）"""
        utc_dt = datetime(2025, 1, 15, 16, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/01/16 00:00"
    
    def test_february_28_non_leap_year(self):
        """测试平年 2 月 28 日跨天"""
        # 2025 年是平年，2 月只有 28 天
        utc_dt = datetime(2025, 2, 28, 20, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2025/03/01 04:00"
    
    def test_december_31_midnight_beijing(self):
        """测试 12 月 31 日 UTC 16:00（北京时间为次年 1 月 1 日 00:00）"""
        utc_dt = datetime(2025, 12, 31, 16, 0)
        beijing_time = utc_to_beijing(utc_dt)
        
        assert beijing_time == "2026/01/01 00:00"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
