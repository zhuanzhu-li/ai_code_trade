#!/usr/bin/env python3
"""
测试接口返回格式是否符合response.py规范
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from endpoint.app import create_app
from endpoint.models import db, User, DataSource
from endpoint.utils.response import ResponseCode, ResponseMessage

def test_response_format():
    """测试接口返回格式"""
    app = create_app()
    
    with app.app_context():
        print("=== 接口返回格式测试 ===\n")
        
        # 测试成功响应格式
        print("1. 测试成功响应格式...")
        from endpoint.utils.response import success_response
        
        success_data = {"test": "data", "count": 1}
        success_msg = "测试成功"
        
        response, status_code = success_response(success_data, success_msg)
        response_data = response.get_json()
        
        expected_format = {
            "code": ResponseCode.SUCCESS,
            "msg": success_msg,
            "data": success_data
        }
        
        if response_data == expected_format and status_code == 200:
            print("✓ 成功响应格式正确")
        else:
            print("✗ 成功响应格式错误")
            print(f"  期望: {expected_format}")
            print(f"  实际: {response_data}")
        
        # 测试业务错误响应格式
        print("\n2. 测试业务错误响应格式...")
        from endpoint.utils.response import business_error_response
        
        error_response, error_status = business_error_response(ResponseCode.NOT_FOUND, "资源不存在")
        error_data = error_response.get_json()
        
        expected_error = {
            "code": ResponseCode.NOT_FOUND,
            "msg": "资源不存在",
            "data": None
        }
        
        if error_data == expected_error and error_status == 400:
            print("✓ 业务错误响应格式正确")
        else:
            print("✗ 业务错误响应格式错误")
            print(f"  期望: {expected_error}")
            print(f"  实际: {error_data}")
        
        # 测试系统错误响应格式
        print("\n3. 测试系统错误响应格式...")
        from endpoint.utils.response import system_error_response
        
        sys_error_response, sys_error_status = system_error_response(ResponseCode.INTERNAL_ERROR, "内部错误")
        sys_error_data = sys_error_response.get_json()
        
        expected_sys_error = {
            "code": ResponseCode.INTERNAL_ERROR,
            "msg": "内部错误",
            "data": None
        }
        
        if sys_error_data == expected_sys_error and sys_error_status == 500:
            print("✓ 系统错误响应格式正确")
        else:
            print("✗ 系统错误响应格式错误")
            print(f"  期望: {expected_sys_error}")
            print(f"  实际: {sys_error_data}")
        
        # 测试默认消息
        print("\n4. 测试默认消息...")
        default_error_response, _ = business_error_response(ResponseCode.MISSING_FIELDS)
        default_error_data = default_error_response.get_json()
        
        if default_error_data["msg"] == ResponseMessage.MISSING_FIELDS:
            print("✓ 默认消息正确")
        else:
            print("✗ 默认消息错误")
            print(f"  期望: {ResponseMessage.MISSING_FIELDS}")
            print(f"  实际: {default_error_data['msg']}")
        
        # 测试所有响应代码
        print("\n5. 测试所有响应代码...")
        test_codes = [
            (ResponseCode.MISSING_FIELDS, ResponseMessage.MISSING_FIELDS, 400),
            (ResponseCode.USERNAME_EXISTS, ResponseMessage.USERNAME_EXISTS, 400),
            (ResponseCode.EMAIL_EXISTS, ResponseMessage.EMAIL_EXISTS, 400),
            (ResponseCode.INVALID_CREDENTIALS, ResponseMessage.INVALID_CREDENTIALS, 400),
            (ResponseCode.ACCOUNT_DISABLED, ResponseMessage.ACCOUNT_DISABLED, 400),
            (ResponseCode.MISSING_CREDENTIALS, ResponseMessage.MISSING_CREDENTIALS, 400),
            (ResponseCode.PORTFOLIO_NOT_FOUND, ResponseMessage.PORTFOLIO_NOT_FOUND, 400),
            (ResponseCode.MISSING_INDEX_CODE, ResponseMessage.MISSING_INDEX_CODE, 400),
            (ResponseCode.MISSING_SYMBOL, ResponseMessage.MISSING_SYMBOL, 400),
            (ResponseCode.NO_SYMBOLS, ResponseMessage.NO_SYMBOLS, 400),
            (ResponseCode.NOT_FOUND, ResponseMessage.NOT_FOUND, 400),
            (ResponseCode.BAD_REQUEST, ResponseMessage.BAD_REQUEST, 400),
            (ResponseCode.UNAUTHORIZED, ResponseMessage.UNAUTHORIZED, 400),
            (ResponseCode.DATA_SOURCE_EXISTS, ResponseMessage.DATA_SOURCE_EXISTS, 400),
            (ResponseCode.DATA_SOURCE_IN_USE, ResponseMessage.DATA_SOURCE_IN_USE, 400),
            (ResponseCode.INTERNAL_ERROR, ResponseMessage.INTERNAL_ERROR, 500),
            (ResponseCode.DATA_SOURCE_ERROR, ResponseMessage.DATA_SOURCE_ERROR, 500),
            (ResponseCode.DATA_SOURCE_INIT_ERROR, ResponseMessage.DATA_SOURCE_INIT_ERROR, 500),
            (ResponseCode.SYNC_ERROR, ResponseMessage.SYNC_ERROR, 500),
            (ResponseCode.FETCH_ERROR, ResponseMessage.FETCH_ERROR, 500),
            (ResponseCode.GET_DATA_ERROR, ResponseMessage.GET_DATA_ERROR, 500),
            (ResponseCode.GET_SYMBOLS_ERROR, ResponseMessage.GET_SYMBOLS_ERROR, 500),
            (ResponseCode.GET_STATS_ERROR, ResponseMessage.GET_STATS_ERROR, 500),
            (ResponseCode.HEALTH_CHECK_ERROR, ResponseMessage.HEALTH_CHECK_ERROR, 500),
            (ResponseCode.CREATE_ERROR, ResponseMessage.CREATE_ERROR, 500),
            (ResponseCode.UPDATE_ERROR, ResponseMessage.UPDATE_ERROR, 500),
            (ResponseCode.DELETE_ERROR, ResponseMessage.DELETE_ERROR, 500),
            (ResponseCode.TEST_ERROR, ResponseMessage.TEST_ERROR, 500),
        ]
        
        all_codes_correct = True
        for code, expected_msg, expected_status in test_codes:
            if code >= 50000:  # 系统错误
                response, status = system_error_response(code)
            else:  # 业务错误
                response, status = business_error_response(code)
            
            response_data = response.get_json()
            
            if (response_data["code"] == code and 
                response_data["msg"] == expected_msg and 
                status == expected_status):
                continue
            else:
                print(f"✗ 响应代码 {code} 格式错误")
                print(f"  期望: code={code}, msg={expected_msg}, status={expected_status}")
                print(f"  实际: code={response_data['code']}, msg={response_data['msg']}, status={status}")
                all_codes_correct = False
        
        if all_codes_correct:
            print("✓ 所有响应代码格式正确")
        else:
            print("✗ 部分响应代码格式错误")
        
        # 测试数据验证
        print("\n6. 测试数据验证...")
        
        # 测试空数据
        empty_response, _ = success_response()
        empty_data = empty_response.get_json()
        if empty_data["data"] is None:
            print("✓ 空数据响应正确")
        else:
            print("✗ 空数据响应错误")
        
        # 测试复杂数据
        complex_data = {
            "users": [{"id": 1, "name": "test"}],
            "pagination": {"page": 1, "total": 10},
            "metadata": {"timestamp": datetime.now().isoformat()}
        }
        
        complex_response, _ = success_response(complex_data, "复杂数据测试")
        complex_response_data = complex_response.get_json()
        
        if complex_response_data["data"] == complex_data:
            print("✓ 复杂数据响应正确")
        else:
            print("✗ 复杂数据响应错误")
        
        print("\n=== 所有测试完成！ ===")

if __name__ == "__main__":
    test_response_format()
