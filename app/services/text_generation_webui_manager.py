"""
Сервис для управления процессом text-generation-webui.

Обеспечивает автоматический запуск и остановку сервера text-generation-webui
при старте и завершении основного приложения.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import aiohttp

from app.config.settings import get_settings
from loguru import logger


class TextGenerationWebUIManager:
    """Менеджер для управления процессом text-generation-webui."""
    
    def __init__(self):
        """Инициализация менеджера."""
        self.settings = get_settings()
        self.process: Optional[subprocess.Popen] = None
        self.server_url = (
            f"http://{self.settings.text_generation_webui_host}:"
            f"{self.settings.text_generation_webui_port}"
        )
        self.is_running = False
        
        # Путь к text-generation-webui
        self.webui_path = Path(self.settings.text_generation_webui_path)
        self.server_script = self.webui_path / "server.py"
        
        # Проверяем существование сервера
        if not self.server_script.exists():
            raise FileNotFoundError(
                f"Сервер text-generation-webui не найден по пути: "
                f"{self.server_script}"
            )
    
    async def start_server(self) -> bool:
        """
        Запускает сервер text-generation-webui.
        
        Returns:
            bool: True если сервер успешно запущен, False в противном случае
        """
        try:
            # Проверяем, не запущен ли уже сервер
            if await self.is_server_running():
                logger.info("Сервер text-generation-webui уже запущен")
                self.is_running = True
                return True
            
            # Формируем команду запуска
            cmd = [
                sys.executable,  # Используем текущий Python интерпретатор
                "server.py",  # Используем относительный путь
                "--api",
                "--listen",
                "--listen-port", str(self.settings.text_generation_webui_port)
            ]
            
            # Добавляем дополнительные параметры если указаны
            if self.settings.text_generation_webui_model:
                cmd.extend(["--model", self.settings.text_generation_webui_model])
            
            if self.settings.text_generation_webui_loader:
                cmd.extend(["--loader", self.settings.text_generation_webui_loader])
            
            # Явно указываем папку моделей
            cmd.extend([
                "--model-dir", self.settings.text_generation_webui_model_dir
            ])
            
            # Оптимизации для больших моделей
            cmd.extend([
                "--gpu-layers", "35",  # Количество слоев на GPU
                "--threads", "8",      # Количество потоков CPU
                "--ctx-size", "8192",  # Размер контекста
                "--batch-size", "512"  # Размер батча
            ])
            
            logger.info(f"Запускаем text-generation-webui: {' '.join(cmd)}")
            
            # Запускаем процесс
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.webui_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            # Ждем запуска сервера
            max_wait_time = 180  # секунд (увеличено для долгой инициализации)
            wait_interval = 2   # секунд
            waited_time = 0
            
            while waited_time < max_wait_time:
                if await self.is_server_running():
                    self.is_running = True
                    logger.info(f"Сервер text-generation-webui успешно запущен на {self.server_url}")
                    return True
                
                # Проверяем, не завершился ли процесс с ошибкой
                if self.process.poll() is not None:
                    stdout, stderr = self.process.communicate()
                    logger.error(f"Сервер завершился с ошибкой. stdout: {stdout}, stderr: {stderr}")
                    return False
                
                # Логируем прогресс каждые 30 секунд
                if waited_time % 30 == 0 and waited_time > 0:
                    logger.info(f"Сервер все еще инициализируется... ({waited_time}/{max_wait_time}s)")
                
                await asyncio.sleep(wait_interval)
                waited_time += wait_interval
                logger.info(f"Ожидание запуска сервера... ({waited_time}/{max_wait_time}s)")
            
            logger.error("Превышено время ожидания запуска сервера")
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при запуске сервера: {e}")
            return False
    
    async def stop_server(self) -> bool:
        """
        Останавливает сервер text-generation-webui.
        
        Returns:
            bool: True если сервер успешно остановлен, False в противном случае
        """
        try:
            if not self.process:
                logger.info("Процесс сервера не найден")
                return True
            
            logger.info("Останавливаем сервер text-generation-webui...")
            
            # Пытаемся корректно завершить процесс
            self.process.terminate()
            
            # Ждем завершения процесса
            try:
                self.process.wait(timeout=10)
                logger.info("Сервер text-generation-webui корректно остановлен")
            except subprocess.TimeoutExpired:
                # Принудительно завершаем процесс
                logger.warning("Принудительное завершение процесса сервера")
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            self.process = None
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при остановке сервера: {e}")
            return False
    
    async def is_server_running(self) -> bool:
        """
        Проверяет, запущен ли сервер text-generation-webui.
        
        Returns:
            bool: True если сервер запущен и отвечает, False в противном случае
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/v1/model") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_server_info(self) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о сервере.
        
        Returns:
            Optional[Dict[str, Any]]: Информация о сервере или None при ошибке
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/v1/model") as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Ошибка при получении информации о сервере: {e}")
        
        return None
    
    def __del__(self):
        """Деструктор для корректного завершения процесса."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                pass


# Глобальный экземпляр менеджера
_webui_manager: Optional[TextGenerationWebUIManager] = None


def get_webui_manager() -> TextGenerationWebUIManager:
    """
    Получает глобальный экземпляр менеджера text-generation-webui.
    
    Returns:
        TextGenerationWebUIManager: Экземпляр менеджера
    """
    global _webui_manager
    if _webui_manager is None:
        _webui_manager = TextGenerationWebUIManager()
    return _webui_manager


async def start_webui_server() -> bool:
    """
    Запускает сервер text-generation-webui.
    
    Returns:
        bool: True если сервер успешно запущен
    """
    manager = get_webui_manager()
    return await manager.start_server()


async def stop_webui_server() -> bool:
    """
    Останавливает сервер text-generation-webui.
    
    Returns:
        bool: True если сервер успешно остановлен
    """
    manager = get_webui_manager()
    return await manager.stop_server()


async def is_webui_server_running() -> bool:
    """
    Проверяет статус сервера text-generation-webui.
    
    Returns:
        bool: True если сервер запущен
    """
    manager = get_webui_manager()
    return await manager.is_server_running() 