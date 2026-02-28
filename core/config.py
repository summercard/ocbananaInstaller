"""
配置管理工具
负责配置的保存、加载和验证
"""

import json
import os
from typing import Dict, Any, Optional
from utils.logger import get_logger
from utils.platform import Platform

class Config:
    """配置管理类"""

    def __init__(self, config_path=None):
        """
        初始化配置管理

        Args:
            config_path: 配置文件路径（默认为应用数据目录/config.json）
        """
        self.logger = get_logger()

        # 设置配置文件路径
        if config_path is None:
            config_dir = Platform.get_app_dir()
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'config.json')

        self.config_path = config_path
        self.config = self._load_default_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        # 获取默认安装目录
        default_install_dir = os.path.join(os.path.expanduser("~"), "openclaw")
        
        return {
            "openclaw": {
                "version": "latest",
                "install_dir": default_install_dir,
                "port": 3000,
                "auto_start": False
            },
            "paths": {
                "nodejs": "",
                "openclaw": ""
            },
            "advanced": {
                "log_level": "INFO",
                "max_log_files": 10
            }
        }

    def load(self) -> bool:
        """
        从文件加载配置

        Returns:
            加载成功返回True，失败返回False
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置（保留新版本的默认值）
                    self._merge_config(loaded_config)
                self.logger.info(f"配置已加载: {self.config_path}")
                return True
            else:
                self.logger.info("配置文件不存在，使用默认配置")
                return False
        except Exception as e:
            self.logger.error(f"加载配置失败: {e}")
            return False

    def save(self) -> bool:
        """
        保存配置到文件

        Returns:
            保存成功返回True，失败返回False
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            self.logger.info(f"配置已保存: {self.config_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
            return False

    def _merge_config(self, loaded_config: Dict[str, Any]):
        """合并配置（保留新版本的默认值）"""
        for key, value in loaded_config.items():
            if key in self.config:
                if isinstance(value, dict) and isinstance(self.config[key], dict):
                    # 递归合并
                    self.config[key].update(value)
                else:
                    self.config[key] = value
            else:
                self.config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项

        Args:
            key: 配置键（支持点号分隔的嵌套键，如'openclaw.port'）
            default: 默认值

        Returns:
            配置值
        """
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> bool:
        """
        设置配置项

        Args:
            key: 配置键（支持点号分隔的嵌套键，如'openclaw.port'）
            value: 配置值

        Returns:
            设置成功返回True，失败返回False
        """
        try:
            keys = key.split('.')
            config = self.config
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            self.logger.debug(f"配置已更新: {key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"设置配置失败: {e}")
            return False

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self.config.copy()

    def reset(self) -> bool:
        """
        重置为默认配置

        Returns:
            重置成功返回True，失败返回False
        """
        try:
            self.config = self._load_default_config()
            self.logger.info("配置已重置为默认值")
            return True
        except Exception as e:
            self.logger.error(f"重置配置失败: {e}")
            return False

    def validate(self) -> tuple:
        """
        验证配置

        Returns:
            (is_valid, error_message)
            is_valid: 是否有效
            error_message: 错误信息（如果无效）
        """
        errors = []

        # 验证OpenClaw配置
        port = self.get('openclaw.port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("openclaw.port 必须是1-65535之间的整数")

        # 验证日志级别
        log_level = self.get('advanced.log_level')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if log_level not in valid_levels:
            errors.append(f"advanced.log_level 必须是: {', '.join(valid_levels)}")

        if errors:
            return False, '; '.join(errors)
        else:
            return True, None

# 测试代码
if __name__ == '__main__':
    config = Config()
    print("默认配置:", config.get_all())

    # 设置配置
    config.set('openclaw.port', 8080)
    config.set('openclaw.auto_start', True)
    print("更新后配置:", config.get_all())

    # 验证配置
    is_valid, error = config.validate()
    print(f"配置有效: {is_valid}, 错误: {error}")

    # 保存配置
    config.save()
    print("配置已保存")
