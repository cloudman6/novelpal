class HybridQueryRouter:
    def route_query(query: str) -> QueryPlan:
        """查询路由决策树"""
        # 结合规则和大模型判断查询类型