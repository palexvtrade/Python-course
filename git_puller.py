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

    # Получаем имя текущей ветки
    current_branch_out, err, code = run_command_shell("git branch --show-current")
    if code != 0:
        print(f"❌ Не удалось получить имя текущей ветки:\n{err}")
        return

    current_branch = current_branch_out.strip()
    if not current_branch:
        print("❌ Не удалось определить текущую ветку.")
        return

    # Проверяем, отличается ли локальная ветка от удалённой
    # git status --porcelain=2 --branch показывает, например: # branch.ab +3 -0
    out, err, code = run_command_shell("git status --porcelain=2 --branch")

    if code != 0:
        print(f"❌ Ошибка при проверке статуса:\n{err}")
        return

    has_updates = False
    for line in out.splitlines():
        if line.startswith("# branch"):
            if "+0 -0" not in line:
                has_updates = True
                break

    if has_updates:
        print("📥 Обнаружены обновления на GitHub.")
        print(f"💡 Будет выполнено слияние изменений из 'origin/{current_branch}' в '{current_branch}'.")

        # Получаем список изменений между локальной и удалённой веткой
        diff_cmd = f"git diff --name-status HEAD origin/{current_branch}"
        diff_out, diff_err, diff_code = run_command_shell(diff_cmd)

        if diff_code != 0:
            print(f"⚠️ Не удалось получить список изменённых файлов:\n{diff_err}")
            # Продолжаем, даже если не удалось получить список
            # Но НЕ предлагаем подтверждение, если diff не удался
            confirm = input("\n✅ Не удалось получить список файлов. Всё равно загрузить обновления? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ Отменено пользователем.")
                return
        else:
            if diff_out.strip():
                print("\n📝 Файлы, изменённые на GitHub (по сравнению с локально):")
                print(diff_out)
                confirm = input("\n✅ Загрузить обновления в локальный репозиторий? (y/N): ").strip().lower()
                if confirm != 'y':
                    print("❌ Отменено пользователем.")
                    return
            else:
                # Если git diff не вернул файлов, но git status показал +X -Y, это странно.
                # Возможно, это только изменения в истории коммитов (например, rebase).
                print("\n📝 Нет различий в содержимом файлов между локальной и удалённой веткой (только изменения в истории коммитов).")
                confirm = input("\n✅ Всё равно выполнить 'git pull' для синхронизации истории? (y/N): ").strip().lower()
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