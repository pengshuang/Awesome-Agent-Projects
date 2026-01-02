#!/usr/bin/env python3
"""
测试文本 LLM API 可用性
测试阿里云 DashScope qwen 文本模型
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 配置参数
API_KEY = os.getenv("API_KEY", "")
API_BASE_URL = os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
TEXT_MODEL_NAME = os.getenv("TEXT_MODEL_NAME", "qwen3-max")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))
TEXT_API_TIMEOUT = int(os.getenv("TEXT_API_TIMEOUT", "60"))


def test_text_api():
    """测试文本 API 是否可用"""
    
    logger.info("=" * 80)
    logger.info("🧪 开始测试文本 LLM API")
    logger.info("=" * 80)
    
    # 检查配置
    logger.info(f"📝 配置信息:")
    logger.info(f"  • API 密钥: {'✅ 已配置' if API_KEY else '❌ 未配置'} (长度: {len(API_KEY)})")
    logger.info(f"  • API URL: {API_BASE_URL}")
    logger.info(f"  • 模型名称: {TEXT_MODEL_NAME}")
    logger.info(f"  • 超时时间: {TEXT_API_TIMEOUT}s")
    logger.info(f"  • Max Tokens: {MAX_TOKENS}")
    logger.info(f"  • 温度参数: {TEMPERATURE}")
    
    if not API_KEY:
        logger.error("❌ API 密钥未配置，请在 .env 文件中设置 API_KEY")
        return False
    
    logger.info("-" * 80)
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    test_message = "你好，请用一句话介绍一下旅游的意义。"
    
    payload = {
        "model": TEXT_MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "messages": [
            {"role": "system", "content": "你是一个有用的旅游助手。"},
            {"role": "user", "content": test_message}
        ]
    }
    
    logger.info(f"📤 发送测试请求:")
    logger.info(f"  • 请求 URL: {API_BASE_URL}/chat/completions")
    logger.info(f"  • 测试消息: {test_message}")
    logger.info(f"  • 请求体大小: {len(json.dumps(payload))} 字节")
    
    try:
        # 发送请求
        logger.info("⏳ 正在发送请求...")
        start_time = datetime.now()
        
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=TEXT_API_TIMEOUT
        )
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        
        # 检查响应状态
        logger.info(f"📥 收到响应 (耗时: {elapsed_time:.2f}s)")
        logger.info(f"  • 状态码: {response.status_code}")
        logger.info(f"  • 响应大小: {len(response.text)} 字节")
        
        if response.status_code == 200:
            logger.info("✅ HTTP 状态码正常 (200 OK)")
            
            # 解析响应
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                message_content = result["choices"][0]["message"]["content"]
                logger.info("✅ 响应格式正确")
                logger.info(f"📝 AI 回复 ({len(message_content)} 字符):")
                logger.info("-" * 80)
                logger.info(message_content)
                logger.info("-" * 80)
                
                # 检查使用量
                if "usage" in result:
                    usage = result["usage"]
                    logger.info(f"📊 Token 使用情况:")
                    logger.info(f"  • 输入: {usage.get('prompt_tokens', 'N/A')} tokens")
                    logger.info(f"  • 输出: {usage.get('completion_tokens', 'N/A')} tokens")
                    logger.info(f"  • 总计: {usage.get('total_tokens', 'N/A')} tokens")
                
                logger.info("=" * 80)
                logger.info("✅ 文本 API 测试成功！")
                logger.info("=" * 80)
                return True
            else:
                logger.error("❌ 响应中没有 choices 字段")
                logger.error(f"响应内容: {response.text}")
                return False
        else:
            logger.error(f"❌ HTTP 错误 {response.status_code}")
            logger.error(f"📝 错误响应:")
            logger.error(response.text[:500])
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ 请求超时 (超过 {TEXT_API_TIMEOUT}s)")
        logger.error("💡 建议: 检查网络连接或增加超时时间")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ 连接错误: {str(e)}")
        logger.error("💡 建议: 检查网络连接和 API URL 是否正确")
        return False
    except json.JSONDecodeError:
        logger.error("❌ 响应不是有效的 JSON")
        logger.error(f"响应内容: {response.text[:500]}")
        return False
    except Exception as e:
        logger.error(f"❌ 发生异常: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = test_text_api()
    sys.exit(0 if success else 1)
