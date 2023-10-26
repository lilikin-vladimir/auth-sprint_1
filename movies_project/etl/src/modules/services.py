import abc
import json
import math
import time
from functools import wraps
from typing import Any, Type, Sequence

from loguru import logger


def backoff(start_sleep_time: int | float = 0.1, factor: int | float = 2, border_sleep_time: int | float = 10,
            exception: Type[Exception] | Sequence[Type[Exception]] = Exception):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка.
    Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)
    Чтобы постоянно не возводить в степень и не умножать большие числа, высчитывается номер попытки, после которой
    время сна не меняется.
    Формула:
        t = start_sleep_time * factor^(n) if t < border_sleep_time
            border_sleep_time >= start_sleep_time * factor^(n)
            factor^(n) <= border_sleep_time/start_sleep_time
            n <= math.log(border_sleep_time/start_sleep_time, factor)
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :param exception: исключение или исключения, которые обрабатываются
    :return: результат выполнения функции
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            sleep_time = start_sleep_time
            error_number = 0
            border_number = None  # чтобы лишний раз не считало большие числа
            while True:
                try:
                    return func(*args, **kwargs)
                except exception:
                    error_number += 1
                    if border_number is None:
                        border_number = math.log(border_sleep_time / start_sleep_time, factor) + 2
                    if error_number <= border_number:
                        sleep_time = start_sleep_time * factor ** (error_number - 1)
                        if sleep_time > border_sleep_time:
                            sleep_time = border_sleep_time
                    logger.warning(f"Ошибка №{error_number} в {func.__name__}. Повтор через {sleep_time} секунд.")
                    time.sleep(sleep_time)

        return inner

    return func_wrapper


class BaseStorage(abc.ABC):
    """Абстрактное хранилище состояния.

    Позволяет сохранять и получать состояние.
    Способ хранения состояния может варьироваться в зависимости
    от итоговой реализации. Например, можно хранить информацию
    в базе данных или в распределённом файловом хранилище.
    """

    @abc.abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):
    """Реализация хранилища, использующего локальный файл.

    Формат хранения: JSON
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, 'w') as f:
            json.dump(state, f)

    def retrieve_state(self) -> dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self.state = self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.state[key] = value
        self.storage.save_state(self.state)

    def get_state(self, key: str, default: Any = None) -> Any:
        """Получить состояние по определённому ключу."""
        return self.state.get(key, default)
