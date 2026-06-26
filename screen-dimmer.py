import tkinter as tk
from tkinter import Toplevel
from screeninfo import get_monitors
import datetime
import time

# ================== НАСТРОЙКИ ==================
# Время начала затемнения (часы:минуты, 24-часовой формат)
START_HOUR = 22
START_MINUTE = 30   # 22:30

# Время окончания затемнения
END_HOUR = 6
END_MINUTE = 15     # 06:15
# ===============================================

black_windows = []   # список чёрных окон


def get_time_in_minutes():
    """Возвращает текущее время в минутах от полуночи (0..1439)."""
    now = datetime.datetime.now()
    return now.hour * 60 + now.minute


def is_time_in_interval():
    """
    Проверяет, входит ли текущее время (в минутах) в заданный интервал.
    Учитывает переход через полночь.
    """
    current = get_time_in_minutes()
    start = START_HOUR * 60 + START_MINUTE
    end = END_HOUR * 60 + END_MINUTE

    if start < end:
        return start <= current < end
    else:   # интервал пересекает полночь, например 22:30 – 06:15
        return current >= start or current < end


def log(message):
    """Выводит сообщение в консоль с временной меткой."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def create_black_windows(root):
    """Создаёт чёрные окна на всех мониторах, кроме основного."""
    global black_windows
    if black_windows:
        log("Чёрные окна уже существуют, пропускаем создание.")
        return

    monitors = get_monitors()
    log(f"Найдено мониторов: {len(monitors)}")
    created = 0
    for mon in monitors:
        if mon.is_primary:
            log(f"Пропускаем основной монитор: {mon.width}x{mon.height} (primary)")
            continue

        x, y, w, h = mon.x, mon.y, mon.width, mon.height
        log(f"Создаём чёрное окно для монитора {mon.width}x{mon.height} (x={x}, y={y})")
        win = Toplevel(root)
        win.overrideredirect(True)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.configure(bg='black')
        win.attributes('-topmost', True)
        win.lift()
        black_windows.append(win)
        created += 1

    log(f"Создано чёрных окон: {created}")


def destroy_black_windows():
    """Закрывает все чёрные окна и очищает список."""
    global black_windows
    if not black_windows:
        return
    log(f"Закрываем {len(black_windows)} чёрных окон...")
    for win in black_windows:
        win.destroy()
    black_windows.clear()
    log("Все чёрные окна закрыты.")


def check_time(root):
    """
    Периодическая проверка времени (каждую минуту).
    Включает или выключает затемнение в зависимости от текущего времени.
    """
    now_str = datetime.datetime.now().strftime("%H:%M")
    in_interval = is_time_in_interval()
    log(f"Проверка времени: {now_str} – {'в интервале' if in_interval else 'вне интервала'}")

    if in_interval:
        if not black_windows:
            create_black_windows(root)
        else:
            log("Затемнение уже активно.")
    else:
        if black_windows:
            destroy_black_windows()
        else:
            log("Затемнение не активно.")

    # Запланировать следующую проверку через 60 секунд
    root.after(60000, check_time, root)


def on_closing(root):
    """Корректное завершение: закрываем все окна и выходим."""
    log("Завершение работы программы...")
    destroy_black_windows()
    root.destroy()


def main():
    log("=== Программа затемнения экранов запущена ===")
    log(f"Интервал затемнения: {START_HOUR:02d}:{START_MINUTE:02d} – {END_HOUR:02d}:{END_MINUTE:02d}")

    root = tk.Tk()
    root.withdraw()   # скрываем главное окно

    # Первая проверка выполняется сразу
    root.after(0, check_time, root)

    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop()


if __name__ == "__main__":
    main()