"""麦门极致省钱精算引擎 (Smart Saver Solver)

实现三大省钱策略：
1. 极致穷鬼模式 (Budget-Friendly): 在给定的超低预算下，以 1+1 随心配为基石，最大化饱腹感与蛋白质。
2. 最优满减凑单 (Coupon-Maximizer): 针对满减券门槛，计算溢出极小的最佳凑单组合，榨干折扣率。
3. 临期救火模式 (Expiring-Rescue): 优先核销 12~24 小时内失效的优质抵扣券，杜绝权益浪费。
"""
from typing import List, Dict, Any, Optional
from client.mcp_client import McDonaldMCPClient
from client.mock_data import COMBO_1PLUS1_PRICE, MOCK_MEALS, MOCK_COUPONS
from core.coupon_manager import CouponManager


class SmartSaverSolver:
    """省钱精算求解器"""

    def __init__(self, mcp_client: McDonaldMCPClient, store_id: str = "DEFAULT"):
        self.client = mcp_client
        self.store_id = store_id

        # 初始化数据
        self.meals = self.client.query_meals(store_id) or MOCK_MEALS
        raw_coupons = self.client.query_coupons() or MOCK_COUPONS
        self.coupon_mgr = CouponManager(raw_coupons)

    def solve(self, mode: str = "budget_friendly", target_budget: float = 25.0) -> Dict[str, Any]:
        """统一定理求解入口"""
        if mode == "budget_friendly":
            result = self._solve_budget_friendly(target_budget)
        elif mode == "coupon_maximizer":
            result = self._solve_coupon_maximizer()
        elif mode == "expiring_rescue":
            result = self._solve_expiring_rescue()
        else:
            result = self._solve_budget_friendly(target_budget)

        # 官方服务端精准验价闭环
        official_val = self.client.calculate_price(result["items"], result["applied_coupons"])
        result["official_verification"] = official_val
        result["payable_price"] = official_val.get("payable_amount", result["estimated_price"])
        result["saved_amount"] = round(result["original_total"] - result["payable_price"], 2)
        result["discount_rate"] = round((result["saved_amount"] / max(0.01, result["original_total"])) * 100, 1)

        return result

    def _solve_budget_friendly(self, budget: float) -> Dict[str, Any]:
        """策略 1：极致穷鬼套餐模式"""
        selected_items = []
        applied_coupons = []
        explanation = []

        # 1+1 随心配是麦门核心基石
        # 寻找红区 (主食/肉类) 与 白区 (饮品/甜品)
        red_items = [m for m in self.meals if "1+1红区" in m.get("tags", [])]
        white_items = [m for m in self.meals if "1+1白区" in m.get("tags", [])]

        if red_items and white_items and budget >= COMBO_1PLUS1_PRICE:
            # 优选双层吉士堡或麦辣鸡腿堡 + 鲜萃咖啡/柠檬红茶
            best_red = next((r for r in red_items if "高蛋白" in r.get("tags", [])), red_items[0])
            best_white = next((w for w in white_items if "0糖" in w.get("tags", [])), white_items[0])

            selected_items.append({
                "id": f"combo_1plus1_{best_red['id']}_{best_white['id']}",
                "name": f"1+1随心配：{best_red['name']} + {best_white['name']}",
                "price": COMBO_1PLUS1_PRICE,
                "original_price": best_red["price"] + best_white["price"],
                "quantity": 1,
                "type": "combo_1plus1",
                "calories": best_red["calories"] + best_white["calories"],
                "protein": best_red["protein"] + best_white["protein"]
            })
            explanation.append(f"采用经典『1+1随心配』基石组合（{best_red['name']} + {best_white['name']}），仅售 ¥{COMBO_1PLUS1_PRICE}（原价 ¥{best_red['price'] + best_white['price']}）。")

            remaining_budget = budget - COMBO_1PLUS1_PRICE

            # 如果剩余预算还够，再叠加单品特惠券或第二个1+1随心配/小食
            if remaining_budget >= COMBO_1PLUS1_PRICE and budget >= 30:
                sec_red = next((r for r in red_items if r != best_red), red_items[0])
                sec_white = next((w for w in white_items if w != best_white), white_items[0])
                selected_items.append({
                    "id": f"combo_1plus1_{sec_red['id']}_{sec_white['id']}",
                    "name": f"第二套随心配：{sec_red['name']} + {sec_white['name']}",
                    "price": COMBO_1PLUS1_PRICE,
                    "original_price": sec_red["price"] + sec_white["price"],
                    "quantity": 1,
                    "type": "combo_1plus1",
                    "calories": sec_red["calories"] + sec_white["calories"],
                    "protein": sec_red["protein"] + sec_white["protein"]
                })
                explanation.append(f"预算充裕，追加第二套随心配，饱腹感翻倍！")
            elif remaining_budget >= 5:
                # 检查是否有单品特惠小食，如 9.9 元麦乐鸡
                snack_cpn = next((c for c in self.coupon_mgr.get_single_item_coupons() if c.get("coupon_id") == "CPN_SAVER_03"), None)
                if snack_cpn and remaining_budget >= 9.9:
                    target_snack = next((m for m in self.meals if m["id"] == snack_cpn["target_item_id"]), None)
                    if target_snack:
                        selected_items.append({
                            "id": target_snack["id"],
                            "name": target_snack["name"],
                            "price": round(target_snack["price"] - snack_cpn["discount_value"], 2),
                            "original_price": target_snack["price"],
                            "quantity": 1,
                            "type": "discounted_item",
                            "calories": target_snack["calories"],
                            "protein": target_snack["protein"]
                        })
                        applied_coupons.append(snack_cpn["coupon_id"])
                        explanation.append(f"使用券【{snack_cpn['title']}】加购一份 {target_snack['name']}。")
        else:
            # 预算极低时推荐单份高性价比主食
            cheap_main = min(self.meals, key=lambda x: x["price"])
            selected_items.append({
                "id": cheap_main["id"],
                "name": cheap_main["name"],
                "price": cheap_main["price"],
                "original_price": cheap_main["price"],
                "quantity": 1,
                "type": "single_item",
                "calories": cheap_main["calories"],
                "protein": cheap_main["protein"]
            })
            explanation.append(f"超低预算兜底，选择性价比单品 {cheap_main['name']}。")

        orig_total = sum(i["original_price"] * i["quantity"] for i in selected_items)
        est_price = sum(i["price"] * i["quantity"] for i in selected_items)

        return {
            "mode": "极致穷鬼方案",
            "target_budget": budget,
            "items": selected_items,
            "applied_coupons": applied_coupons,
            "original_total": round(orig_total, 2),
            "estimated_price": round(est_price, 2),
            "explanation": explanation
        }

    def _solve_coupon_maximizer(self) -> Dict[str, Any]:
        """策略 2：最优满减门槛凑单模式"""
        threshold_cpns = self.coupon_mgr.get_threshold_coupons()
        if not threshold_cpns:
            return self._solve_budget_friendly(35.0)

        best_cpn = threshold_cpns[0]  # 优先拿门槛最划算的，例如满40减10
        threshold = best_cpn["threshold"]

        # 先选一个核心优质主食（如巨无霸或双层吉士堡套餐）
        main_dish = next((m for m in self.meals if m["id"] == "item_001"), self.meals[0])
        current_items = [{
            "id": main_dish["id"],
            "name": main_dish["name"],
            "price": main_dish["price"],
            "original_price": main_dish["price"],
            "quantity": 1,
            "calories": main_dish["calories"],
            "protein": main_dish["protein"]
        }]
        current_sum = main_dish["price"]

        # 贪心寻找最佳小食与饮品补足门槛
        remaining_gap = threshold - current_sum
        sorted_sides = sorted([m for m in self.meals if m["category"] in ("小食", "饮品")], key=lambda x: x["price"])

        for side in sorted_sides:
            if current_sum >= threshold:
                break
            current_items.append({
                "id": side["id"],
                "name": side["name"],
                "price": side["price"],
                "original_price": side["price"],
                "quantity": 1,
                "calories": side["calories"],
                "protein": side["protein"]
            })
            current_sum += side["price"]

        orig_total = current_sum
        est_price = max(0.01, round(orig_total - best_cpn["discount_value"], 2))
        explanation = [
            f"目标满减券【{best_cpn['title']}】（门槛 ¥{threshold}，立减 ¥{best_cpn['discount_value']}）。",
            f"主菜选定经典 {main_dish['name']}，搭配小食精准凑至 ¥{orig_total}，刚好突破 ¥{threshold} 门槛。",
            f"满减后实付仅 ¥{est_price}，每分钱都不浪费！"
        ]

        return {
            "mode": "最优满减凑单",
            "target_coupon": best_cpn["title"],
            "items": current_items,
            "applied_coupons": [best_cpn["coupon_id"]],
            "original_total": round(orig_total, 2),
            "estimated_price": est_price,
            "explanation": explanation
        }

    def _solve_expiring_rescue(self) -> Dict[str, Any]:
        """策略 3：临期卡券救火模式"""
        expiring = self.coupon_mgr.get_expiring_coupons(24)
        if not expiring:
            return self._solve_coupon_maximizer()

        # 优先使用最紧急且减免最大的券
        urgent_cpn = expiring[0]
        selected_items = []
        applied_coupons = [urgent_cpn["coupon_id"]]
        explanation = [f"【紧急救火】券【{urgent_cpn['title']}】仅剩 {urgent_cpn.get('expires_in_hours')} 小时即将失效，优先锁定！"]

        if urgent_cpn.get("discount_type") in ("single_discount", "special_price", "bogo"):
            target_item = next((m for m in self.meals if m["id"] == urgent_cpn.get("target_item_id")), self.meals[0])
            discount_val = urgent_cpn["discount_value"]
            discounted_price = max(0.01, round(target_item["price"] - discount_val, 2))
            
            if urgent_cpn.get("discount_type") == "bogo":
                selected_items.append({
                    "id": target_item["id"],
                    "name": f"{target_item['name']} × 2份 [买一送一券核销]",
                    "price": target_item["price"],
                    "original_price": target_item["price"] * 2,
                    "quantity": 1,
                    "calories": target_item["calories"] * 2,
                    "protein": target_item["protein"] * 2
                })
                explanation.append(f"核销买一送一券【{urgent_cpn['title']}】，仅付一份价格 ¥{target_item['price']} 获得双份 {target_item['name']}！")
            else:
                selected_items.append({
                    "id": target_item["id"],
                    "name": target_item["name"],
                    "price": discounted_price,
                    "original_price": target_item["price"],
                    "quantity": 1,
                    "calories": target_item["calories"],
                    "protein": target_item["protein"]
                })
                explanation.append(f"以折后价 ¥{discounted_price} 成功兑换 {target_item['name']}（原价 ¥{target_item['price']}）。")

            # 搭配一份高性价比主食
            main_food = next((m for m in self.meals if m["category"] == "主食"), None)
            if main_food and main_food["id"] != target_item["id"]:
                selected_items.append({
                    "id": main_food["id"],
                    "name": main_food["name"],
                    "price": main_food["price"],
                    "original_price": main_food["price"],
                    "quantity": 1,
                    "calories": main_food["calories"],
                    "protein": main_food["protein"]
                })
                explanation.append(f"搭配主食 {main_food['name']}，构成完整一餐。")
        else:
            return self._solve_coupon_maximizer()

        orig_total = sum(i["original_price"] * i["quantity"] for i in selected_items)
        est_price = sum(i["price"] * i["quantity"] for i in selected_items)

        return {
            "mode": "临期卡券救火方案",
            "items": selected_items,
            "applied_coupons": applied_coupons,
            "original_total": round(orig_total, 2),
            "estimated_price": round(est_price, 2),
            "explanation": explanation
        }
