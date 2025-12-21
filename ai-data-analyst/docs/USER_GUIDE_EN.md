# User Guide

This guide is designed for regular users to learn how to use the AI Data Analysis Assistant for data analysis.

## 📋 Table of Contents

- [Installation and Configuration](#installation-and-configuration)
- [Quick Start](#quick-start)
- [Feature Usage](#feature-usage)
- [Common Issues](#common-issues)

## Installation and Configuration

### 1. System Requirements

- Python 3.8+
- LLM API Key (OpenAI/DeepSeek/Qwen, etc.)

### 2. Installation Steps

```bash
# Clone the project
git clone <repository-url>
cd ai-data-analyst

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

### 3. Configure LLM

Edit the `.env` file and choose an LLM provider:

**OpenAI (Recommended GPT-3.5/4)**
```bash
LLM_API_KEY=sk-your-api-key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

**DeepSeek (Recommended, cost-effective)**
```bash
LLM_API_KEY=sk-your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**Qwen (Tongyi Qianwen)**
```bash
LLM_API_KEY=sk-your-api-key
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

### 4. Start the Service

```bash
python web_ui.py
```

Access http://localhost:7860

## Quick Start

### Create Sample Data

```bash
python data/create_example_db.py
```

This will create a sample database with sales data.

### Basic Usage Flow

1. **Initialize System** - Switch to "⚙️ System Settings" and click "Initialize System"
2. **Register Data Source** - Add database or files in "🗄️ Data Source Management"
3. **Start Analysis** - Ask questions in natural language in "💬 Chat Analysis"

## Feature Usage

### Data Source Management

#### Add SQLite Database

1. Switch to "🗄️ Data Source Management" tab
2. Fill in information:
   - Data Source Name: `my_db`
   - Database Path: `data/databases/example.db`
3. Click "✅ Register Database"

#### Add File Data Source

Supported formats: CSV, Excel, JSON, Parquet

1. Place the file in the `data/files/` directory
2. Register in data source management:
   - Data Source Name: `sales_data`
   - File Path: `data/files/sales.csv`

### Natural Language Queries

In the "💬 Chat Analysis" tab, ask questions directly in natural language:

**Basic Queries**
```
Query all customer information
Show sales data from the last month
```

**Statistical Analysis**
```
What is the total sales volume for each product?
Which customer has the highest purchase amount?
```

**Trend Analysis**
```
Show monthly sales revenue trends
Compare sales performance across products
```

### Data Visualization

#### Method 1: Generate via Chat

Request visualization directly in the chat:
```
Query monthly sales revenue and generate a line chart
```

#### Method 2: Manual Configuration

1. Switch to "📊 Data Visualization" tab
2. Select data source and click "Load Data"
3. Configure chart:
   - Select chart type (bar/line/pie, etc.)
   - Set X-axis and Y-axis fields
   - Set chart title
4. Click "Generate Chart"

#### Supported Chart Types

- 📊 **Bar Chart** - Compare data
- 📈 **Line Chart** - Trend analysis
- 🥧 **Pie Chart** - Proportion analysis
- 🔵 **Scatter Plot** - Correlation analysis
- 📉 **Box Plot** - Distribution analysis
- 🌡️ **Heatmap** - Multi-dimensional data

### Query Examples

**Sales Analysis**
```
Query monthly sales revenue
Find the top 5 products by sales volume
Calculate total spending for each customer
```

**Data Filtering**
```
Query sales data for 2024
Show orders with sales amount greater than 1000
Find customers who purchased laptops
```

**Aggregate Statistics**
```
Group by product and calculate total quantity and revenue
Calculate average order amount per month
Count the number of customers in each region
```

## Common Issues

### Q1: Prompt "LLM_API_KEY not set"

**Solution**: Check if `LLM_API_KEY` is correctly configured in the `.env` file

### Q2: Query returns empty results

**Reasons**:
- Data source not registered
- SQL query conditions don't match
- Database actually has no data

**Solutions**:
1. Check if data source is registered
2. View Schema in data source management
3. Use broader query conditions

### Q3: Visualization fails

**Reasons**:
- Data type mismatch
- Incorrect field names
- Empty data

**Solutions**:
1. Ensure data is correctly queried
2. Check if field names are correct
3. Confirm data type is suitable for chart type

### Q4: Chat has no context

**Solution**: 
- Ensure continuous conversation in the same session
- Don't refresh the page (clears history)
- Check "History Turns" setting

### Q5: Which SQL dialects are supported?

Currently mainly supports SQLite. Other databases (MySQL, PostgreSQL) can be configured via the `SQL_DIALECT` environment variable.

### Q6: How to improve query accuracy?

**Suggestions**:
1. Use clear and specific questions
2. Include specific field names
3. Specify conditions like time ranges
4. View data source Schema to understand field information

### Q7: Is the data secure?

- All data is processed locally
- Only query questions are sent to the LLM
- Raw data is not uploaded
- Recommend using read-only database connections

## 🎯 Usage Tips

1. **Understand data structure first** - View Schema in data source management
2. **Start simple** - Begin with simple queries, then gradually add complexity
3. **Use examples** - Refer to sample query statements
4. **Multi-turn conversations** - Continue asking based on previous results
5. **Verify results** - Validate query results through visualization charts

## 📞 Get Help

- View [Developer Guide](DEVELOPER_GUIDE_EN.md)
- Submit an [Issue](https://github.com/your-repo/issues)
- Check example code in `examples/`

> Installation, configuration, and usage tutorials for regular users

---

## 🚀 Quick Start

### System Requirements

- Python 3.8+
- 8GB RAM (recommended)
- Stable internet connection

### Installation Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env file (see below)

# 3. Start service
python web_ui.py

# 4. Access interface
# http://localhost:7860
```

---

## ⚙️ Environment Configuration

### Required Configuration

Edit the `.env` file to configure LLM API:

```bash
# LLM API Configuration (Required)
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
TEMPERATURE=0.1
```

### Common API Configurations

**OpenAI**
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-3.5-turbo
```

**DeepSeek**
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**Qwen (Tongyi Qianwen)**
```bash
LLM_API_KEY=sk-...
LLM_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-turbo
```

**Local Model (Ollama)**
```bash
LLM_API_KEY=ollama
LLM_API_BASE=http://localhost:11434/v1
LLM_MODEL=llama3
```

### Optional Configuration

```bash
# Embedding Model
EMBEDDING_PROVIDER=huggingface
EMBEDDING_MODEL_NAME=BAAI/bge-small-zh-v1.5

# Chat History Turns
MAX_HISTORY_TURNS=10

# Web Search (Optional)
ENABLE_WEB_SEARCH=false
WEB_SEARCH_API_KEY=your-search-api-key
```

---

## 📖 User Tutorial

### Step 1: Initialize System

1. Open http://localhost:7860
2. Switch to "⚙️ System Settings" tab
3. Click "🔄 Initialize System"
4. Wait for initialization to complete

### Step 2: Register Data Sources

Switch to "🗄️ Data Source Management" tab

#### Register Database

```
Database Name: sales_db
Database Path: data/databases/sales.db
```

Click "➕ Register Database"

#### Register File

```
File Name: sales_data
File Path: data/files/sales.csv
```

Supports: CSV, Excel, JSON, Parquet

#### Register Knowledge Base

1. Place documents in `data/knowledge_base/`
2. Enter knowledge base name
3. Click "➕ Register Knowledge Base"

Supports: PDF, Word, Markdown, TXT

#### Enable Web Search

Configure `.env` and click "🔌 Enable Web Search"

### Step 3: Data Analysis

Switch to "💬 Chat Analysis" tab

#### Example Queries

**Database Queries**
```
- Count total sales revenue for each month
- Find the top 10 products by sales
- Analyze 2024 sales trends
```

**File Analysis**
```
- How many rows are in this dataset?
- Analyze the data distribution for each column
- Find outliers in the price column
```

**Knowledge Base Q&A**
```
- What is the company's vacation policy?
- How do I apply for reimbursement?
```

#### Multi-turn Conversations

```
User: Query sales data
Assistant: [Displays data]

User: Group by region
Assistant: [Understands context, re-queries]

User: Show only top 5
Assistant: [Continues based on context]
```

### Step 4: Data Visualization

1. Execute query in "Chat Analysis"
2. Switch to "📊 Data Visualization" tab
3. Click "🔄 Load Data"
4. Configure chart:
   - Select chart type
   - Select X-axis and Y-axis
   - Optional: Color grouping
5. Click "🎨 Generate Chart"

#### Chart Type Selection

| Chart | Use Case |
|------|---------|
| Bar Chart | Category comparison |
| Line Chart | Trend analysis |
| Scatter Plot | Correlation analysis |
| Pie Chart | Proportion analysis |
| Area Chart | Cumulative trends |
| Box Plot | Distribution analysis |

---

## 💡 Best Practices

### Question Techniques

✅ **Good Questions**
- "Query sales revenue for each product from January to June 2024, sorted by amount in descending order"
- "Analyze the correlation between price and quantity in the sales table"
- "What are the company's regulations regarding annual leave?"

❌ **Bad Questions**
- "Check it" (not specific)
- "There's a problem with the data" (no specific description)
- "What should I do" (lacks context)

### Data Source Management

- Use meaningful names
- Update data regularly
- Backup important data

### Performance Optimization

- Use fast models (gpt-3.5-turbo)
- Limit returned data volume (use LIMIT)
- Reduce history turns

---

## ❓ Common Questions

### Q: Initialization failed?

**Checklist**
- [ ] `.env` file configured correctly
- [ ] API Key is valid
- [ ] Network connection is normal
- [ ] Check `logs/` directory

### Q: SQL generation is inaccurate?

**Solutions**
- Provide more detailed problem descriptions
- Use multi-turn conversations to clarify step by step
- Check if database schema is correctly loaded

### Q: No results from knowledge base?

**Checklist**
- [ ] Document placed in directory
- [ ] Document format supported
- [ ] Index built successfully
- [ ] Try different phrasing

### Q: Slow response?

**Optimization Suggestions**
- Use faster model
