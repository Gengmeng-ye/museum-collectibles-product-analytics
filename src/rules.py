import re

MUSEUM_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Palace Museum", ("故宫", "宫廷")),
    ("Dunhuang", ("敦煌",)),
    ("Sanxingdui", ("三星堆", "川蜀小堆")),
    ("Henan Museum", ("河南博物", "河南洛阳", "洛阳")),
    ("Hunan Museum", ("湖南省博物", "湖南博物")),
    ("Gansu Museum", ("甘肃省博物", "甘肃博物")),
    ("Xinjiang Museum", ("新疆博物",)),
    ("Suzhou Museum", ("苏州博物",)),
    ("Terracotta Warriors", ("兵马俑",)),
    ("National Museum of China", ("中国国家博物馆", "国博")),
    ("Shaanxi History Museum", ("陕西历史博物馆", "陕历博")),
    ("Shandong Museum", ("山东博物馆",)),
    ("Chengdu Museum", ("成都博物馆",)),
    ("Liaoning Museum", ("辽宁省博物馆", "辽宁博物馆")),
    ("Qingdao Beer Museum", ("青岛啤酒博物馆",)),
    ("Van Gogh Museum", ("梵高博物馆",)),
    ("Du Fu Thatched Cottage", ("杜甫草堂",)),
)

CATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Excavation Kit", ("考古", "挖掘", "挖宝", "寻宝", "探宝", "挖土")),
    ("Figurine / Display", ("手办", "摆件", "公仔", "盲盒", "模型")),
    ("Craft / Assembly", ("DIY", "手工", "积木", "拼装", "修复")),
    ("Gift / Assortment", ("福袋", "心意盒", "礼盒", "伴手礼")),
)

FORMAT_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Excavation / DIY Kit", ("考古", "挖掘", "挖宝", "寻宝", "修复", "DIY", "diy")),
    ("Figurine", ("手办", "公仔", "摆件", "模型")),
    ("Plush / Bag Charm", ("毛绒", "挂件", "钥匙扣", "包挂")),
    ("Magnet", ("冰箱贴", "磁吸", "磁贴")),
    ("Badge / Accessory", ("徽章", "胸针", "吧唧", "首饰")),
    ("Gift Bag / Assortment", ("福袋", "礼盒", "礼包")),
)

ASPECT_RULES: dict[str, tuple[str, ...]] = {
    "Product Design": ("设计", "外观", "好看", "可爱", "造型", "颜色", "光泽"),
    "Quality": ("质量", "瑕疵", "破", "坏", "粗糙", "简陋", "材质", "做工"),
    "Packaging": ("包装", "盒子", "外包装", "手提袋", "封口", "胶带"),
    "Price & Value": ("价格", "定价", "贵", "便宜", "性价比", "不值", "物超所值"),
    "Service": ("客服", "掌柜", "态度", "服务"),
    "Logistics": ("物流", "快递", "发货", "驿站"),
    "Blind-box Outcome": ("隐藏", "抽到", "想要", "手气", "概率", "随机", "款式"),
    "Gifting & Education": ("送给", "送朋友", "礼物", "小朋友", "孩子", "教学", "学习", "考古"),
}


def normalize_text(value: object) -> str:
    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def first_rule_match(text: str, rules: tuple[tuple[str, tuple[str, ...]], ...], default: str) -> str:
    for label, keywords in rules:
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return label
    return default


def detect_aspects(text: str) -> list[str]:
    return [
        aspect
        for aspect, keywords in ASPECT_RULES.items()
        if any(keyword in text for keyword in keywords)
    ]
