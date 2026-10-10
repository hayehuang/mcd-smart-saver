"""卡券资产管理与分类模块

负责优惠券去重、临期判定、门槛排序与类型标签提取。
"""
from typing import List, Dict, Any


class CouponManager:
    """优惠券管家"""

    def __init__(self, raw_coupons: List[Dict[str, Any]]):
        self.coupons = raw_coupons

    def get_expiring_coupons(self, threshold_hours: int = 24) -> List[Dict[str, Any]]:
        """获取即将过期的救火卡券"""
        expiring = [
            c for c in self.coupons
            if c.get("expires_in_hours", 999) <= threshold_hours
        ]
        return sorted(expiring, key=lambda x: x.get("expires_in_hours", 999))

    def get_threshold_coupons(self) -> List[Dict[str, Any]]:
        """获取满减类优惠券，按减免金额降序排列"""
        threshold_cpns = [
            c for c in self.coupons
            if c.get("discount_type") == "threshold"
        ]
        return sorted(threshold_cpns, key=lambda x: x.get("discount_value", 0), reverse=True)

    def get_single_item_coupons(self) -> List[Dict[str, Any]]:
        """获取单品特惠/半价/买一送一卡券"""
        return [
            c for c in self.coupons
            if c.get("discount_type") in ("single_discount", "special_price", "bogo")
        ]

    def summary(self) -> Dict[str, Any]:
        """返回卡券资产全景摘要"""
        total = len(self.coupons)
        expiring = len(self.get_expiring_coupons(24))
        max_discount = max((c.get("discount_value", 0) for c in self.coupons), default=0)
        return {
            "total_count": total,
            "expiring_soon_count": expiring,
            "max_possible_discount": max_discount
        }
