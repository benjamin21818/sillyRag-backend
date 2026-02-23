from html import unescape
import os
import re
import jieba

from src.utils.conf import BASE_DIR

# uv add jieba

protected_words = [
    'http', 'https', 'ftp', 'tcp', 'file',
    'url', 'email', 'www'
]

for word in protected_words:
    jieba.add_word(word)

def load_stopwords(file_path: str) -> set:
    """
    从文件中加载停用词
    :param file_path: 停用词文件路径
    :return: 停用词集合
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        stopwords = {line.strip() for line in f if line.strip()}
    return stopwords

# 停用词
stopwords = load_stopwords(os.path.join(BASE_DIR, "src","utils","stopwords.txt"))

# 定义要保留的字符（中文、字母、数字）
TEXT_PATTERN = re.compile(r'[^\u4e00-\u9fa5a-zA-Z0-9]+')

def clean_text(text, remove_digits=False):
    """
    中文文本清洗函数，用于分词前的预处理
    
    参数:
        text: 原始文本字符串
        remove_digits: 是否去除数字，默认为False
        
    返回:
        清洗后的文本字符串
    """
    if not isinstance(text, str):
        return ""
    
    # 1. 去除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 2. 解码HTML实体（如&amp; -> &）
    text = unescape(text)
    
    # 3. 去除URL
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # 4. 去除邮箱
    text = re.sub(r'\S+@\S+', '', text)
    
    # 5. 去除特殊字符和标点，保留中文、英文、数字和基本标点
    # 这里保留了中文、字母、数字和常见标点，可根据需求调整
    if remove_digits:
        # 去除数字
        text = re.sub(r'[0-9]', '', text)
        # 保留中文、字母和部分标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z,.?!，。？！；;：:]', ' ', text)
    else:
        # 保留中文、字母、数字和部分标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9,.?!，。？！；;：:]', ' ', text)
    
    # 6. 去除多余空格（包括换行符、制表符等）
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 7. 去除首尾空格
    text = text.strip()
    
    return text

def to_query(text: str,mode: str='search'):
    cleaned_text = clean_text(text)
    words = None
    
    if mode == 'full': # 全模式 找出所有可能的词汇组合，包括子词
        words = jieba.lcut(cleaned_text, cut_all=True)
    elif mode == 'exact': # 精确模式 精确切分，只返回最有可能的词汇组合
        words = jieba.lcut(cleaned_text, cut_all=False)
    else: # 搜索引擎模式   在精确模式的基础上，对长词再次切分
        words = jieba.cut_for_search(cleaned_text)
        
    filtered_words = [word for word in words if word not in stopwords]
    result = " | ".join(filtered_words)
    return result