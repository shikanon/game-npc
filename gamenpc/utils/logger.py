import logging

class DebugLogger:
    """
    DebugLogger 类用于在调试模式下记录日志信息
    """
    def __init__(self, name):
        """
        初始化 DebugLogger 类

        参数:
            name (str): 类的名称，用于在日志记录中标识
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

                # 创建日志处理器，设置日志级别为INFO，输出日志到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # 日志格式化
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 增加格式化到处理器
        ch.setFormatter(formatter)

        # 将处理器添加到日志记录器中
        self.logger.addHandler(ch)

    def debug(self, message):
        """
        在调试模式下记录日志信息

        参数:
            message (str): 要记录的日志信息
        """
        # if self.logger.isEnabledFor(logging.DEBUG):
        self.logger.debug(message)
    
    def info(self, message):
        """
        在运行模式下记录日志信息

        参数:
            message (str): 要记录的日志信息
        """
        # if self.logger.isEnabledFor(logging.INFO):
        self.logger.info(message)

debuglog = DebugLogger("game npc web")