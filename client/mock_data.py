"""麦当劳 MCP 服务离线高保真仿真数据模块 (Mock Data)

提供在无 Token 或离线演示场景下的真实业务数据回退，涵盖常见餐品、1+1随心配、卡券及营销日历。
"""

MOCK_MEALS = [
    {
        "id": "item_001",
        "name": "巨无霸汉堡",
        "category": "主食",
        "price": 25.0,
        "calories": 520,
        "protein": 26,
        "tags": ["经典", "双层牛肉", "饱腹"]
    },
    {
        "id": "item_002",
        "name": "双层吉士堡",
        "category": "主食",
        "price": 22.0,
        "calories": 440,
        "protein": 24,
        "tags": ["高蛋白", "1+1红区"]
    },
    {
        "id": "item_003",
        "name": "麦辣鸡腿堡",
        "category": "主食",
        "price": 23.0,
        "calories": 510,
        "protein": 22,
        "tags": ["人气", "微辣", "1+1红区"]
    },
    {
        "id": "item_004",
        "name": "麦香鸡汉堡",
        "category": "主食",
        "price": 14.5,
        "calories": 380,
        "protein": 15,
        "tags": ["实惠", "1+1红区"]
    },
    {
        "id": "item_005",
        "name": "板烧鸡腿堡",
        "category": "主食",
        "price": 24.0,
        "calories": 405,
        "protein": 25,
        "tags": ["非油炸", "健身首选"]
    },
    {
        "id": "item_006",
        "name": "麦辣鸡翅(2块)",
        "category": "小食",
        "price": 14.0,
        "calories": 210,
        "protein": 14,
        "tags": ["小食", "1+1红区"]
    },
    {
        "id": "item_007",
        "name": "麦乐鸡(5块)+甜酸酱",
        "category": "小食",
        "price": 13.5,
        "calories": 230,
        "protein": 13,
        "tags": ["小食", "1+1红区"]
    },
    {
        "id": "item_008",
        "name": "大脆鸡排",
        "category": "小食",
        "price": 14.0,
        "calories": 280,
        "protein": 16,
        "tags": ["小食", "周一特惠"]
    },
    {
        "id": "item_009",
        "name": "薯条(中)",
        "category": "小食",
        "price": 13.0,
        "calories": 320,
        "protein": 4,
        "tags": ["经典薯条"]
    },
    {
        "id": "item_010",
        "name": "鲜萃美式咖啡(中)",
        "category": "饮品",
        "price": 10.0,
        "calories": 15,
        "protein": 1,
        "tags": ["0糖", "1+1白区"]
    },
    {
        "id": "item_011",
        "name": "可口可乐(中)",
        "category": "饮品",
        "price": 9.5,
        "calories": 140,
        "protein": 0,
        "tags": ["冷饮", "1+1白区"]
    },
    {
        "id": "item_012",
        "name": "阳光柠檬红茶(中)",
        "category": "饮品",
        "price": 10.0,
        "calories": 95,
        "protein": 0,
        "tags": ["果味茶", "1+1白区"]
    },
    {
        "id": "item_013",
        "name": "迷你草莓新地",
        "category": "甜品",
        "price": 10.5,
        "calories": 180,
        "protein": 3,
        "tags": ["甜品", "1+1白区"]
    },
    {
        "id": "item_014",
        "name": "菠萝派",
        "category": "甜品",
        "price": 9.0,
        "calories": 230,
        "protein": 2,
        "tags": ["甜品", "1+1白区"]
    }
]

# 1+1 随心配固定价格
COMBO_1PLUS1_PRICE = 13.9

# 模拟优惠券资产池
MOCK_COUPONS = [
    {
        "coupon_id": "CPN_SAVER_01",
        "title": "满40减10元全场通用券",
        "discount_type": "threshold",
        "threshold": 40.0,
        "discount_value": 10.0,
        "expires_in_hours": 36,
        "scope": "ALL",
        "description": "麦麦省独家满减券"
    },
    {
        "coupon_id": "CPN_SAVER_02",
        "title": "巨无霸单品半价券",
        "discount_type": "single_discount",
        "target_item_id": "item_001",
        "threshold": 0.0,
        "discount_value": 12.5,
        "expires_in_hours": 12,
        "scope": "item_001",
        "description": "临期爆款！仅剩12小时失效"
    },
    {
        "coupon_id": "CPN_SAVER_03",
        "title": "麦乐鸡5块特惠9.9元券",
        "discount_type": "special_price",
        "target_item_id": "item_007",
        "threshold": 0.0,
        "discount_value": 3.6,
        "expires_in_hours": 72,
        "scope": "item_007",
        "description": "小食特惠尝鲜券"
    },
    {
        "coupon_id": "CPN_SAVER_04",
        "title": "满59减18元工作日午餐专属券",
        "discount_type": "threshold",
        "threshold": 59.0,
        "discount_value": 18.0,
        "expires_in_hours": 48,
        "scope": "ALL",
        "description": "多人/大额拼单神器"
    },
    {
        "coupon_id": "CPN_SAVER_05",
        "title": "鲜萃咖啡买一送一券",
        "discount_type": "bogo",
        "target_item_id": "item_010",
        "threshold": 0.0,
        "discount_value": 10.0,
        "expires_in_hours": 8,
        "scope": "item_010",
        "description": "极度临期！办公室续命首选"
    }
]

# 模拟活动日历
MOCK_CAMPAIGN_CALENDAR = {
    "month": "2026-10",
    "today_date": "2026-10-10",
    "events": [
        {
            "date": "2026-10-10",
            "name": "麦麦周六亲子会员日",
            "tag": "周末特惠",
            "highlight": "开心乐园餐赠送限定积木玩具，甜品站第2份半价"
        },
        {
            "date": "2026-10-12",
            "name": "麦麦会员周一狂欢日",
            "tag": "会员半价",
            "highlight": "大脆鸡排买一送一，板烧鸡腿堡单品半价"
        },
        {
            "date": "2026-10-14",
            "name": "疯狂周三麦乐鸡节",
            "tag": "小食狂欢",
            "highlight": "20块麦乐鸡仅售22元，附赠4款限定沾酱"
        },
        {
            "date": "2026-10-24",
            "name": "1024 程序员节专属特惠",
            "tag": "极客派对",
            "highlight": "双层吉士堡+鲜萃咖啡极客提神套餐特惠10.24元"
        }
    ]
}
