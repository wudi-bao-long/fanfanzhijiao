import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_md5_hex(filepath: str):                    # 获取文件的md5十六进制字符串
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(chunk_size):                  # 读取数据
                md5_obj.update(chunk)                           # 把读取到的数据存到变量chunk里
            """
            chunk = f.read(chunk_size)
            while chunk:
            
                md5_obj.update(chunk)
                chunk = f.read(chunk_size)
            """

            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败,{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):                # 返回文件夹内的文件列表（允许的文件后缀）
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return allowed_types

    for f in os.listdir(path):                          # os.listdir(path)是获取文件夹内所有内容的文字
        if f.endswith(allowed_types):                   # 过滤文件后缀
            files.append(os.path.join(path, f))         # 拼接完整路径  path文件路径和f文件名拼接在一起

    return tuple(files)                                 # 转换为元组返回


# 这个函数是将PDF文件加载成Langchain能理解的Document对象
def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    return PyPDFLoader(filepath, passwd).load()


# 这个函数是将TXT文件加载成Langchain能理解的Document对象
def txt_loader(filepath: str) -> list[Document]:
    return TextLoader(filepath, encoding="utf-8").load()                  # TextLoader是创建文本加载器实例,然后.load()就是加载文件内容
