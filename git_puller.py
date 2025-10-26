import subprocess

def run_command_shell(cmd):
    """
    Выполняет shell-команду и возвращает:
    - stdout: вывод команды (в виде строки)
    - stderr: ошибки (в виде строки)
    - returncode: код возврата (0 — успех)
    """
    result = subprocess.run(cmd, shell=True, capture_output=True)

    encodings = ['utf-8', 'cp1251', 'latin-1']
    stdout = ""
    stderr = ""

    for enc in encodings:
        try:
            stdout = result.stdout.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        stdout = result.stdout.decode('utf-8', errors='replace')

    for enc in encodings:
        try:
            stderr = result.stderr.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue
    else:
        stderr = result.stderr.decode('utf-8', errors='replace')

    return stdout, stderr, result.returncode

def main():
    print("🔍 Проверка, является ли директория Git-репозиторием...")

    _, _, code = run_command_shell("git status")
    if code != 0:
        print("❌ Текущая директория не является Git-репозиторием.")
        return

    print("🔄 Проверяем наличие обновлений с GitHub...")

    # Обновляем информацию о состоянии удалённого репозитория
    out, err, code = run_command_shell("git fetch")
    if code != 0:
        print(f"❌ Ошибка при выполнении 'git fetch':\n{err}")
        return

    # Проверяем, отличается ли локальная ветка от удалённой
    out, err, code = run_command_shell("git status --porcelain=2 --branch")

    if code != 0:
        print(f"❌ Ошибка при проверке статуса:\n{err}")
        return

    has_updates = False
    for line in out.splitlines():
        if line.startswith("# branch"):
            # Пример строки: # branch.ab +0 -0
            # +0 -0 означает, что локальная ветка на 0 вперёд и 0 позади от удалённой
            if "+0 -0" not in line:
                has_updates = True
                break

    if has_updates:
        print("📥 Обнаружены обновления на GitHub.")
        confirm = input("✅ Загрузить их в локальный репозиторий? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Отменено пользователем.")
            return

        print("🔄 Выполняем 'git pull'...")
        out, err, code = run_command_shell("git pull")
        if code != 0:
            print(f"❌ Ошибка при выполнении 'git pull':\n{err}")
            print("💡 Возможно, есть конфликты слияния. Попробуйте разрешить их вручную.")
            return

        print(f"📥 Изменения успешно загружены:\n{out}")
    else:
        print("✅ Нет новых изменений на GitHub — локальная версия актуальна.")

if __name__ == "__main__":
    main()