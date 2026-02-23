from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter




class PartitionTXT:
    def __init__(self):
        pass

    async def partition_txt(self, file_path: str):
        try:
            loader = TextLoader(file_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=300,          # 每个块的最大字符数 值为300最佳
                        chunk_overlap=50,        # 相邻块之间的重叠字符数 值为50最佳
                        length_function=len,     # 计算文本长度的函数
                        # add_start_index=True,    # 是否添加起始索引
                    )
            split_docs = text_splitter.split_documents(docs)
            return split_docs

        except FileNotFoundError:
            print(f"文件 {file_path} 未找到。")
            return None