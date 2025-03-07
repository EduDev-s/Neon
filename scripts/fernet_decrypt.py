import os
import argparse
from cryptography.fernet import Fernet, InvalidToken
import colorama

# Инициализация цветного вывода
colorama.init()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
RESET = colorama.Fore.RESET


def print_success(message):
    print(f"{GREEN}[+] {message}{RESET}")


def print_error(message):
    print(f"{RED}[-] {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}[?] {message}{RESET}")


def get_fernet(key: str) -> Fernet:
    try:
        return Fernet(key.encode())
    except ValueError as e:
        print_error(f"Неверный формат ключа: {e}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Дешифратор файлов Fernet")
    parser.add_argument("-f", "--file", required=True, help="Путь к зашифрованному файлу")
    parser.add_argument("-k", "--key", help="Ключ шифрования")
    parser.add_argument("-o", "--output", help="Файл для сохранения результата")
    args = parser.parse_args()

    # Получаем ключ шифрования
    key = args.key or os.getenv("ENCRYPTION_KEY")
    if not key:
        print_warning("Ключ шифрования не найден в аргументах и переменных окружения")
        key = input(f"{YELLOW}[?] Введите ключ шифрования: {RESET}").strip()
        if not key:
            print_error("Ключ шифрования не предоставлен")
            exit(1)

    # Инициализируем Fernet
    fernet = get_fernet(key)

    # Чтение файла
    try:
        print_success("Начинаю чтение файла...")
        with open(args.file, "rb") as f:
            encrypted_data = f.read()
    except FileNotFoundError:
        print_error(f"Файл не найден: {args.file}")
        exit(1)
    except Exception as e:
        print_error(f"Ошибка чтения файла: {str(e)}")
        exit(1)

    # Дешифровка
    try:
        print_success("Начинаю дешифровку...")
        decrypted_data = fernet.decrypt(encrypted_data)
    except InvalidToken:
        print_error("Неверный ключ или поврежденные данные")
        exit(1)

    # Декодирование
    try:
        result = decrypted_data.decode("utf-8")
    except UnicodeDecodeError:
        print_error("Ошибка декодирования данных")
        exit(1)

    # Сохранение/вывод результата
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(result)
            print_success(f"Результат сохранен в: {args.output}")
        except Exception as e:
            print_error(f"Ошибка записи в файл: {str(e)}")
            exit(1)
    else:
        print("\nРезультат дешифровки:")
        print(result)

    print_success("Операция завершена успешно!")


if __name__ == "__main__":
    main()
