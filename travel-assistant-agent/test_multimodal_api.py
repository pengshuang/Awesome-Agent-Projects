#!/usr/bin/env python3
"""
测试多模态 LLM API 可用性
测试阿里云 DashScope qwen-vl 视觉模型
"""

import os
import sys
import json
import logging
import requests
import base64
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
MULTIMODAL_MODEL_NAME = os.getenv("MULTIMODAL_MODEL_NAME", "qwen-vl-plus")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.85"))
MULTIMODAL_API_TIMEOUT = int(os.getenv("MULTIMODAL_API_TIMEOUT", "90"))


def create_test_image():
    """创建一个简单的测试图片 (1x1 红色像素)"""
    # 最小的有效 PNG 图片 (1x1 红色像素)
    png_data = bytes.fromhex(
        '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000a'
        '4944415408d7633f0000000001000000018b06abcf0000000049454e44ae426082'
    )
    return png_data


def create_sample_image_file():
    """创建样本图片文件用于测试"""
    test_dir = Path("tests")
    test_dir.mkdir(exist_ok=True)
    
    image_path = test_dir / "test_image.png"
    
    # 创建一个简单的测试图片
    png_data = create_test_image()
    
    with open(image_path, "wb") as f:
        f.write(png_data)
    
    logger.info(f"✅ 创建测试图片: {image_path} ({len(png_data)} 字节)")
    return image_path


def test_multimodal_api(image_path=None):
    """测试多模态 API 是否可用"""
    
    logger.info("=" * 80)
    logger.info("🧪 开始测试多模态 LLM API")
    logger.info("=" * 80)
    
    # 检查配置
    logger.info(f"📝 配置信息:")
    logger.info(f"  • API 密钥: {'✅ 已配置' if API_KEY else '❌ 未配置'} (长度: {len(API_KEY)})")
    logger.info(f"  • API URL: {API_BASE_URL}")
    logger.info(f"  • 模型名称: {MULTIMODAL_MODEL_NAME}")
    logger.info(f"  • 超时时间: {MULTIMODAL_API_TIMEOUT}s")
    logger.info(f"  • Max Tokens: {MAX_TOKENS}")
    logger.info(f"  • 温度参数: {TEMPERATURE}")
    
    if not API_KEY:
        logger.error("❌ API 密钥未配置，请在 .env 文件中设置 API_KEY")
        return False
    
    logger.info("-" * 80)
    
    # 准备图片
    if image_path is None:
        logger.info("📸 使用测试图片...")
        image_path = create_sample_image_file()
    
    if not Path(image_path).exists():
        logger.error(f"❌ 图片文件不存在: {image_path}")
        return False
    
    # 读取并编码图片
    logger.info(f"📖 读取图片文件: {image_path}")
    try:
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        file_size = Path(image_path).stat().st_size
        logger.info(f"  • 文件大小: {file_size} 字节")
        logger.info(f"  • Base64 编码长度: {len(image_data)} 字符")
    except Exception as e:
        logger.error(f"❌ 读取图片失败: {str(e)}")
        return False
    
    # 构建请求
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    test_prompt = "请描述这张图片的内容。"
    
    payload = {
        "model": MULTIMODAL_MODEL_NAME,
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "messages": [
            {
                "role": "system",
                "content": "你是一个有用的图片分析助手。请用中文描述图片内容。"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    },
                    {
                        "type": "text",
                        "text": test_prompt
                    }
                ]
            }
        ]
    }
    
    logger.info(f"📤 发送测试请求:")
    logger.info(f"  • 请求 URL: {API_BASE_URL}/chat/completions")
    logger.info(f"  • 测试提示: {test_prompt}")
    logger.info(f"  • 请求体大小: {len(json.dumps(payload)) / 1024:.2f} KB")
    
    try:
        # 发送请求
        logger.info("⏳ 正在发送请求...")
        start_time = datetime.now()
        
        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=MULTIMODAL_API_TIMEOUT
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
                logger.info(f"📝 AI 分析结果 ({len(message_content)} 字符):")
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
                logger.info("✅ 多模态 API 测试成功！")
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
        logger.error(f"❌ 请求超时 (超过 {MULTIMODAL_API_TIMEOUT}s)")
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
    import argparse
    
    parser = argparse.ArgumentParser(description="测试多模态 LLM API")
    parser.add_argument("--image", type=str, help="图片文件路径 (可选，不指定则使用测试图片)")
    
    args = parser.parse_args()
    
    success = test_multimodal_api(image_path=args.image)
    sys.exit(0 if success else 1)
