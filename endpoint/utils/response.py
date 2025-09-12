"""
统一响应格式工具类
"""
from typing import Any


class ResponseCode:
    """响应状态码定义"""
    # 成功
    SUCCESS = 200

    # 业务异常 (10xxx)
    MISSING_FIELDS = 10001
    USERNAME_EXISTS = 10002
    EMAIL_EXISTS = 10003
    INVALID_CREDENTIALS = 10004
    ACCOUNT_DISABLED = 10005
    MISSING_CREDENTIALS = 10006
    PORTFOLIO_NOT_FOUND = 10007
    MISSING_INDEX_CODE = 10008
    MISSING_SYMBOL = 10009
    NO_SYMBOLS = 10010
    NOT_FOUND = 10011
    BAD_REQUEST = 10012
    UNAUTHORIZED = 10013
    DATA_SOURCE_EXISTS = 10014
    DATA_SOURCE_IN_USE = 10015

    # 系统异常 (50xxx)
    INTERNAL_ERROR = 50001
    DATA_SOURCE_ERROR = 50002
    DATA_SOURCE_INIT_ERROR = 50003
    SYNC_ERROR = 50004
    FETCH_ERROR = 50005
    GET_DATA_ERROR = 50006
    GET_SYMBOLS_ERROR = 50007
    GET_STATS_ERROR = 50008
    HEALTH_CHECK_ERROR = 50009
    CREATE_ERROR = 50010
    UPDATE_ERROR = 50011
    DELETE_ERROR = 50012
    TEST_ERROR = 50013


class ResponseMessage:
    """响应消息定义"""
    SUCCESS = "成功！"

    # 业务异常消息
    MISSING_FIELDS = "缺少必要字段"
    USERNAME_EXISTS = "用户名已存在"
    EMAIL_EXISTS = "邮箱已存在"
    INVALID_CREDENTIALS = "用户名或密码错误"
    ACCOUNT_DISABLED = "账户已被禁用"
    MISSING_CREDENTIALS = "缺少用户名或密码"
    PORTFOLIO_NOT_FOUND = "投资组合不存在或无权限访问"
    MISSING_INDEX_CODE = "缺少指数代码"
    MISSING_SYMBOL = "缺少股票代码"
    NO_SYMBOLS = "没有找到需要更新的股票"
    NOT_FOUND = "资源未找到"
    BAD_REQUEST = "请求参数错误"
    UNAUTHORIZED = "未授权访问"
    DATA_SOURCE_EXISTS = "数据来源名称已存在"
    DATA_SOURCE_IN_USE = "数据来源正在使用中"

    # 系统异常消息
    INTERNAL_ERROR = "内部服务器错误"
    DATA_SOURCE_ERROR = "数据源错误"
    DATA_SOURCE_INIT_ERROR = "数据源初始化失败"
    SYNC_ERROR = "数据同步失败"
    FETCH_ERROR = "数据获取失败"
    GET_DATA_ERROR = "获取市场数据失败"
    GET_SYMBOLS_ERROR = "获取股票列表失败"
    GET_STATS_ERROR = "获取统计信息失败"
    HEALTH_CHECK_ERROR = "健康检查失败"
    CREATE_ERROR = "创建失败"
    UPDATE_ERROR = "更新失败"
    DELETE_ERROR = "删除失败"
    TEST_ERROR = "测试失败"


class ApiResponse:
    """统一API响应格式"""

    @staticmethod
    def success(data: Any = None, message: str = ResponseMessage.SUCCESS) -> tuple:
        """
        成功响应
        
        Args:
            data: 响应数据
            message: 响应消息，默认为"成功！"
            
        Returns:
            tuple: (jsonify对象, HTTP状态码)
        """
        response = {
            "code": ResponseCode.SUCCESS,
            "msg": message,
            "data": data
        }
        return response, 200

    @staticmethod
    def error(code: int, message: str, data: Any = None) -> tuple:
        """
        错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            data: 响应数据，默认为None
            
        Returns:
            tuple: (jsonify对象, HTTP状态码)
        """
        response = {
            "code": code,
            "msg": message,
            "data": data
        }

        # 根据错误码确定HTTP状态码
        if 10000 <= code < 20000:
            http_status = 400  # 业务异常
        elif 50000 <= code < 60000:
            http_status = 500  # 系统异常
        else:
            http_status = 400  # 默认业务异常

        return response, http_status

    @staticmethod
    def business_error(code: int, message: str = None, data: Any = None) -> tuple:
        """
        业务异常响应
        
        Args:
            code: 业务错误码
            message: 错误消息，如果为None则使用默认消息
            data: 响应数据
            
        Returns:
            tuple: (jsonify对象, HTTP状态码)
        """
        if message is None:
            message = ApiResponse._get_default_message(code)
        return ApiResponse.error(code, message, data)

    @staticmethod
    def system_error(code: int, message: str = None, data: Any = None) -> tuple:
        """
        系统异常响应
        
        Args:
            code: 系统错误码
            message: 错误消息，如果为None则使用默认消息
            data: 响应数据
            
        Returns:
            tuple: (jsonify对象, HTTP状态码)
        """
        if message is None:
            message = ApiResponse._get_default_message(code)
        return ApiResponse.error(code, message, data)

    @staticmethod
    def _get_default_message(code: int) -> str:
        """获取默认错误消息"""
        message_map = {
            ResponseCode.MISSING_FIELDS: ResponseMessage.MISSING_FIELDS,
            ResponseCode.USERNAME_EXISTS: ResponseMessage.USERNAME_EXISTS,
            ResponseCode.EMAIL_EXISTS: ResponseMessage.EMAIL_EXISTS,
            ResponseCode.INVALID_CREDENTIALS: ResponseMessage.INVALID_CREDENTIALS,
            ResponseCode.ACCOUNT_DISABLED: ResponseMessage.ACCOUNT_DISABLED,
            ResponseCode.MISSING_CREDENTIALS: ResponseMessage.MISSING_CREDENTIALS,
            ResponseCode.PORTFOLIO_NOT_FOUND: ResponseMessage.PORTFOLIO_NOT_FOUND,
            ResponseCode.MISSING_INDEX_CODE: ResponseMessage.MISSING_INDEX_CODE,
            ResponseCode.MISSING_SYMBOL: ResponseMessage.MISSING_SYMBOL,
            ResponseCode.NO_SYMBOLS: ResponseMessage.NO_SYMBOLS,
            ResponseCode.NOT_FOUND: ResponseMessage.NOT_FOUND,
            ResponseCode.BAD_REQUEST: ResponseMessage.BAD_REQUEST,
            ResponseCode.UNAUTHORIZED: ResponseMessage.UNAUTHORIZED,
            ResponseCode.DATA_SOURCE_EXISTS: ResponseMessage.DATA_SOURCE_EXISTS,
            ResponseCode.DATA_SOURCE_IN_USE: ResponseMessage.DATA_SOURCE_IN_USE,
            ResponseCode.INTERNAL_ERROR: ResponseMessage.INTERNAL_ERROR,
            ResponseCode.DATA_SOURCE_ERROR: ResponseMessage.DATA_SOURCE_ERROR,
            ResponseCode.DATA_SOURCE_INIT_ERROR: ResponseMessage.DATA_SOURCE_INIT_ERROR,
            ResponseCode.SYNC_ERROR: ResponseMessage.SYNC_ERROR,
            ResponseCode.FETCH_ERROR: ResponseMessage.FETCH_ERROR,
            ResponseCode.GET_DATA_ERROR: ResponseMessage.GET_DATA_ERROR,
            ResponseCode.GET_SYMBOLS_ERROR: ResponseMessage.GET_SYMBOLS_ERROR,
            ResponseCode.GET_STATS_ERROR: ResponseMessage.GET_STATS_ERROR,
            ResponseCode.HEALTH_CHECK_ERROR: ResponseMessage.HEALTH_CHECK_ERROR,
            ResponseCode.CREATE_ERROR: ResponseMessage.CREATE_ERROR,
            ResponseCode.UPDATE_ERROR: ResponseMessage.UPDATE_ERROR,
            ResponseCode.DELETE_ERROR: ResponseMessage.DELETE_ERROR,
            ResponseCode.TEST_ERROR: ResponseMessage.TEST_ERROR,
        }
        return message_map.get(code, "未知错误")


# 便捷函数
def success_response(data: Any = None, message: str = ResponseMessage.SUCCESS) -> tuple:
    """成功响应便捷函数"""
    return ApiResponse.success(data, message)


def error_response(code: int, message: str, data: Any = None) -> tuple:
    """错误响应便捷函数"""
    return ApiResponse.error(code, message, data)


def business_error_response(code: int, message: str = None, data: Any = None) -> tuple:
    """业务异常响应便捷函数"""
    return ApiResponse.business_error(code, message, data)


def system_error_response(code: int, message: str = None, data: Any = None) -> tuple:
    """系统异常响应便捷函数"""
    return ApiResponse.system_error(code, message, data)
