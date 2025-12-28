"""
创建示例 SQLite 数据库
用于演示和测试
"""

import sqlite3
from pathlib import Path
import random
from datetime import datetime, timedelta

# 确保数据库目录存在
db_dir = Path(__file__).parent.parent / "data" / "databases"
db_dir.mkdir(parents=True, exist_ok=True)

db_path = db_dir / "example_sales.db"

# 创建数据库连接
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print(f"正在创建示例数据库: {db_path}")

# 创建产品表
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL
)
""")

# 创建销售表
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    region TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
)
""")

# 插入产品数据
products = [
    (1, "笔记本电脑", "电子产品", 5999.00),
    (2, "无线鼠标", "电子产品", 129.00),
    (3, "机械键盘", "电子产品", 399.00),
    (4, "显示器", "电子产品", 1299.00),
    (5, "办公椅", "家具", 899.00),
    (6, "办公桌", "家具", 1299.00),
    (7, "台灯", "家具", 199.00),
    (8, "文件柜", "家具", 599.00),
    (9, "白板", "办公用品", 299.00),
    (10, "投影仪", "电子产品", 3999.00),
]

cursor.executemany(
    "INSERT OR REPLACE INTO products (product_id, product_name, category, price) VALUES (?, ?, ?, ?)",
    products
)

# 插入销售数据（生成最近6个月的数据）
regions = ["华东", "华南", "华北", "华中", "西南", "西北", "东北"]
start_date = datetime.now() - timedelta(days=180)

sales_data = []
for i in range(500):  # 生成500条销售记录
    product_id = random.randint(1, 10)
    sale_date = start_date + timedelta(days=random.randint(0, 180))
    quantity = random.randint(1, 20)
    region = random.choice(regions)
    
    sales_data.append((product_id, sale_date.strftime('%Y-%m-%d'), quantity, region))

cursor.executemany(
    "INSERT INTO sales (product_id, sale_date, quantity, region) VALUES (?, ?, ?, ?)",
    sales_data
)

# 提交更改
conn.commit()

# 验证数据
cursor.execute("SELECT COUNT(*) FROM products")
product_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sales")
sales_count = cursor.fetchone()[0]

print(f"✅ 数据库创建成功！")
print(f"   产品数量: {product_count}")
print(f"   销售记录: {sales_count}")

# 显示示例查询
print("\n示例查询：")
print("-" * 50)

# 查询1：每个类别的销售总额
cursor.execute("""
SELECT 
    p.category,
    COUNT(s.sale_id) as total_sales,
    SUM(s.quantity * p.price) as revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC
""")

print("\n1. 各类别销售统计：")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} 笔订单, 收入 ¥{row[2]:,.2f}")

# 查询2：各地区销售统计
cursor.execute("""
SELECT 
    region,
    COUNT(*) as order_count,
    SUM(quantity) as total_quantity
FROM sales
GROUP BY region
ORDER BY order_count DESC
""")

print("\n2. 各地区销售统计：")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} 笔订单, {row[2]} 件商品")

# 关闭连接
conn.close()

print("\n" + "=" * 50)
print("✅ 示例数据库已就绪！")
print(f"路径: {db_path}")
print("\n使用方法：")
print("1. 启动 Web UI")
print("2. 在「数据源管理」页面注册此数据库")
print(f"   名称: sales_db")
print(f"   路径: {db_path}")
print("3. 开始提问，例如：")
print("   - 查询销售总额最高的产品")
print("   - 分析各地区的销售情况")
print("   - 统计每月的销售趋势")
print("=" * 50)
