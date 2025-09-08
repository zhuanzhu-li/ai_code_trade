"""
定时任务服务
负责管理定时获取市场数据的任务
"""

import logging
from datetime import datetime, time, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from typing import List, Dict, Optional

from services.market_data_service import MarketDataService
from models import Symbol

logger = logging.getLogger(__name__)

class SchedulerService:
    """定时任务服务类"""
    
    def __init__(self):
        """初始化定时任务服务"""
        self.scheduler = BackgroundScheduler()
        self.market_service = MarketDataService()
        
        # 添加事件监听器
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        # 任务状态跟踪
        self.job_status = {}
        
    def start(self):
        """启动调度器"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("定时任务调度器已启动")
                
                # 添加默认任务
                self._add_default_jobs()
                
        except Exception as e:
            logger.error(f"启动定时任务调度器失败: {e}")
    
    def stop(self):
        """停止调度器"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("定时任务调度器已停止")
        except Exception as e:
            logger.error(f"停止定时任务调度器失败: {e}")
    
    def _job_listener(self, event):
        """任务事件监听器"""
        job_id = event.job_id
        
        if event.exception:
            logger.error(f"任务 {job_id} 执行失败: {event.exception}")
            self.job_status[job_id] = {
                'status': 'error',
                'last_run': datetime.now(),
                'error': str(event.exception)
            }
        else:
            logger.info(f"任务 {job_id} 执行成功")
            self.job_status[job_id] = {
                'status': 'success',
                'last_run': datetime.now(),
                'error': None
            }
    
    def _add_default_jobs(self):
        """添加默认的定时任务"""
        try:
            # 每个交易日早上9:00获取最新数据
            self.add_daily_market_data_job()
            
            # 每个交易日收盘后15:30获取当日数据
            self.add_after_market_data_job()
            
            # 每周日凌晨2:00同步股票列表
            self.add_weekly_symbol_sync_job()
            
            logger.info("默认定时任务添加完成")
            
        except Exception as e:
            logger.error(f"添加默认定时任务失败: {e}")
    
    def add_daily_market_data_job(self):
        """添加每日市场数据获取任务"""
        job_id = 'daily_market_data'
        
        # 每个工作日早上9:00执行
        self.scheduler.add_job(
            func=self._fetch_daily_market_data,
            trigger=CronTrigger(
                day_of_week='mon-fri',  # 周一到周五
                hour=9,
                minute=0
            ),
            id=job_id,
            name='每日市场数据获取',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"已添加任务: {job_id}")
    
    def add_after_market_data_job(self):
        """添加收盘后数据获取任务"""
        job_id = 'after_market_data'
        
        # 每个工作日下午15:30执行
        self.scheduler.add_job(
            func=self._fetch_after_market_data,
            trigger=CronTrigger(
                day_of_week='mon-fri',  # 周一到周五
                hour=15,
                minute=30
            ),
            id=job_id,
            name='收盘后数据获取',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"已添加任务: {job_id}")
    
    def add_weekly_symbol_sync_job(self):
        """添加每周股票列表同步任务"""
        job_id = 'weekly_symbol_sync'
        
        # 每周日凌晨2:00执行
        self.scheduler.add_job(
            func=self._sync_symbols_weekly,
            trigger=CronTrigger(
                day_of_week='sun',  # 周日
                hour=2,
                minute=0
            ),
            id=job_id,
            name='每周股票列表同步',
            replace_existing=True,
            max_instances=1
        )
        
        logger.info(f"已添加任务: {job_id}")
    
    def add_custom_job(
        self, 
        job_id: str, 
        func_name: str, 
        trigger_type: str = 'cron',
        **trigger_kwargs
    ):
        """
        添加自定义任务
        
        Args:
            job_id: 任务ID
            func_name: 要执行的函数名
            trigger_type: 触发器类型 ('cron' 或 'interval')
            **trigger_kwargs: 触发器参数
        """
        try:
            # 获取要执行的函数
            func = getattr(self, f'_{func_name}', None)
            if not func:
                raise ValueError(f"函数 {func_name} 不存在")
            
            # 创建触发器
            if trigger_type == 'cron':
                trigger = CronTrigger(**trigger_kwargs)
            elif trigger_type == 'interval':
                trigger = IntervalTrigger(**trigger_kwargs)
            else:
                raise ValueError(f"不支持的触发器类型: {trigger_type}")
            
            # 添加任务
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=job_id,
                name=f'自定义任务_{job_id}',
                replace_existing=True,
                max_instances=1
            )
            
            logger.info(f"已添加自定义任务: {job_id}")
            
        except Exception as e:
            logger.error(f"添加自定义任务失败: {e}")
            raise
    
    def remove_job(self, job_id: str):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.job_status:
                del self.job_status[job_id]
            logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            logger.error(f"移除任务失败: {e}")
    
    def get_job_info(self, job_id: str) -> Optional[Dict]:
        """获取任务信息"""
        try:
            job = self.scheduler.get_job(job_id)
            if not job:
                return None
            
            status = self.job_status.get(job_id, {'status': 'pending', 'last_run': None, 'error': None})
            
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'status': status['status'],
                'last_run': status['last_run'].isoformat() if status['last_run'] else None,
                'error': status['error']
            }
            
        except Exception as e:
            logger.error(f"获取任务信息失败: {e}")
            return None
    
    def list_jobs(self) -> List[Dict]:
        """列出所有任务"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                job_info = self.get_job_info(job.id)
                if job_info:
                    jobs.append(job_info)
            return jobs
        except Exception as e:
            logger.error(f"列出任务失败: {e}")
            return []
    
    # ============================================
    # 任务执行函数
    # ============================================
    
    def _fetch_daily_market_data(self):
        """每日市场数据获取任务"""
        try:
            logger.info("开始执行每日市场数据获取任务...")
            
            # 初始化数据源
            if not self.market_service.initialize_data_source():
                raise Exception("数据源初始化失败")
            
            # 获取活跃股票列表
            active_symbols = Symbol.query.filter_by(is_active=True).all()
            symbols = [s.symbol for s in active_symbols]
            
            if not symbols:
                logger.warning("没有找到活跃股票")
                return
            
            # 批量获取最新数据
            results = self.market_service.batch_fetch_latest_data(symbols[:100])  # 限制数量，避免超时
            
            total_updated = sum(results.values())
            successful_symbols = len([k for k, v in results.items() if v > 0])
            
            logger.info(f"每日市场数据获取完成: 处理{len(symbols)}只股票，成功{successful_symbols}只，新增{total_updated}条记录")
            
        except Exception as e:
            logger.error(f"每日市场数据获取任务失败: {e}")
            raise
    
    def _fetch_after_market_data(self):
        """收盘后数据获取任务"""
        try:
            logger.info("开始执行收盘后数据获取任务...")
            
            # 与每日任务类似，但可能包含更多数据
            self._fetch_daily_market_data()
            
            logger.info("收盘后数据获取任务完成")
            
        except Exception as e:
            logger.error(f"收盘后数据获取任务失败: {e}")
            raise
    
    def _sync_symbols_weekly(self):
        """每周股票列表同步任务"""
        try:
            logger.info("开始执行每周股票列表同步任务...")
            
            # 初始化数据源
            if not self.market_service.initialize_data_source():
                raise Exception("数据源初始化失败")
            
            # 同步A股列表
            synced_count = self.market_service.sync_symbols('A股')
            
            # 同步上证500成分股
            index_count = self.market_service.sync_index_components('上证500')
            
            logger.info(f"每周股票列表同步完成: 同步股票{synced_count}只，指数成分股{index_count}只")
            
        except Exception as e:
            logger.error(f"每周股票列表同步任务失败: {e}")
            raise
    
    def _fetch_specific_symbols(self, symbols: List[str]):
        """获取指定股票的数据"""
        try:
            logger.info(f"开始获取指定股票数据: {len(symbols)}只")
            
            # 初始化数据源
            if not self.market_service.initialize_data_source():
                raise Exception("数据源初始化失败")
            
            # 批量获取数据
            results = self.market_service.batch_fetch_latest_data(symbols)
            
            total_updated = sum(results.values())
            successful_symbols = len([k for k, v in results.items() if v > 0])
            
            logger.info(f"指定股票数据获取完成: 处理{len(symbols)}只股票，成功{successful_symbols}只，新增{total_updated}条记录")
            
        except Exception as e:
            logger.error(f"获取指定股票数据失败: {e}")
            raise
    
    def trigger_immediate_fetch(self, symbols: Optional[List[str]] = None):
        """立即触发数据获取"""
        try:
            if symbols:
                self._fetch_specific_symbols(symbols)
            else:
                self._fetch_daily_market_data()
        except Exception as e:
            logger.error(f"立即获取数据失败: {e}")
            raise
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            'running': self.scheduler.running,
            'job_count': len(self.scheduler.get_jobs()),
            'jobs': self.list_jobs()
        }

# 全局调度器实例
scheduler_service = SchedulerService()
