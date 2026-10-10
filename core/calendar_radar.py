"""麦麦营销活动雷达 (Calendar Radar)

解析 campaign-calendar 返回的当月/当日营销活动，智能提示优惠活动与会员日。
"""
from typing import Dict, Any, List


class CalendarRadar:
    """营销活动雷达"""

    def __init__(self, calendar_data: Dict[str, Any]):
        self.data = calendar_data
        self.today_date = calendar_data.get("today_date", "")
        self.events = calendar_data.get("events", [])

    def get_today_event(self) -> List[Dict[str, Any]]:
        """获取今天生效的活动"""
        matched = [e for e in self.events if e.get("date") == self.today_date]
        return matched

    def get_upcoming_highlights(self) -> List[Dict[str, Any]]:
        """获取即将到来的重磅活动（如会员日、1024程序员节）"""
        return [e for e in self.events if e.get("date") >= self.today_date]

    def get_tips(self) -> List[str]:
        """输出智能消费避坑与加惠提示"""
        tips = []
        today_evts = self.get_today_event()
        if today_evts:
            for evt in today_evts:
                tips.append(f"【今日特惠】{evt.get('name')}：{evt.get('highlight')}")
        else:
            tips.append("【今日提醒】今日暂无大型会员狂欢，推荐使用 1+1 随心配或满减券组合最划算。")

        # 检查是否有临近的程序员节或会员日
        for evt in self.events:
            if "1024" in evt.get("name", ""):
                tips.append(f"【节日预告】{evt.get('name')} 即将到来：{evt.get('highlight')}！")
        return tips
