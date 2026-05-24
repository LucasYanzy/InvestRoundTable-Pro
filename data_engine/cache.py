"""二级缓存系统：内存 LRU + 本地 pickle 文件。"""

import os
import time
import pickle
import hashlib
import logging
from collections import OrderedDict
from typing import Any, Optional

import config

logger = logging.getLogger(__name__)

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: str, value: Any):
        self.cache[key] = value
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

class DataCache:
    """二级缓存系统（内存LRU + 本地文件）"""
    
    def __init__(self):
        self.memory_cache = LRUCache(config.MEMORY_CACHE_SIZE)
        self.cache_dir = config.CACHE_DIR
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def _generate_file_path(self, cache_key: str) -> str:
        """生成安全的文件名，防止特殊字符"""
        safe_key = hashlib.md5(cache_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{safe_key}.pkl")
        
    def _is_file_valid(self, file_path: str, ttl_hours: float) -> bool:
        if not os.path.exists(file_path):
            return False
        file_age = time.time() - os.path.getmtime(file_path)
        return file_age < (ttl_hours * 3600)
        
    def get(self, cache_key: str, is_fundamental: bool = False) -> Optional[Any]:
        # 1. 查内存
        mem_data = self.memory_cache.get(cache_key)
        if mem_data is not None:
            return mem_data
            
        # 2. 查文件
        file_path = self._generate_file_path(cache_key)
        ttl = config.FUNDAMENTAL_CACHE_TTL_HOURS if is_fundamental else config.CACHE_TTL_HOURS
        
        if self._is_file_valid(file_path, ttl):
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                # 回写到内存
                self.memory_cache.put(cache_key, data)
                return data
            except Exception as e:
                logger.warning("读取缓存文件失败 %s: %s", file_path, e)
                
        return None
        
    def set(self, cache_key: str, data: Any):
        # 1. 写内存
        self.memory_cache.put(cache_key, data)
        # 2. 写文件
        file_path = self._generate_file_path(cache_key)
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            logger.warning("写入缓存文件失败 %s: %s", file_path, e)

# 全局单例
global_cache = DataCache()
