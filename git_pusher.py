import os
import subprocess

def run_command_shell(cmd):
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

def run_command_safe(args):
    result = subprocess.run(args, capture_output=True)

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

def check_git_auth():
    stdout, _, _ = run_command_shell("git config user.name")
    name = stdout.strip()
    if not name:
        print("❌ Не установлено имя пользователя Git (git config user.name)")
        return False

    stdout, _, _ = run_command_shell("git config user.email")
    email = stdout.strip()
    if not email:
        print("❌ Не установлен email пользователя Git (git config user.email)")
        return False

    stdout, _, code = run_command_shell("gh auth status")
    if code == 0:
        print(f"✅ Авторизован в GitHub через GitHub CLI как: {name}")
        return True
    else:
        print(f"⚠️ GitHub CLI не авторизован, но Git настроен: {name} <{email}>")
        print("💡 Если используешь SSH или токен — всё должно работать.")
        return True

def get_modified_and_untracked_files():
    """
    Возвращает:
    - modified: список изменённых/удалённых и т.д. файлов
    - untracked: список новых файлов (??)
    """
    stdout, stderr, code = run_command_shell("git status --porcelain")
    if code != 0:
        print(f"❌ Ошибка выполнения 'git status': {stderr}")
        return [], []

    modified = []
    untracked = []

    for line in stdout.splitlines():
        if line.strip():
            status = line[:2].strip()  # Например: 'M ', '??'
            file_path = line[3:]
            if status in ['M', 'A', 'D', 'R', 'C']:
                modified.append(file_path)
            elif status == '??':  # Новый файл
                untracked.append(file_path)

    return modified, untracked

def main():
    print("🔍 Проверка статуса репозитория и авторизации...")

    _, _, code = run_command_shell("git status")
    if code != 0:
        print("❌ Текущая директория не является Git-репозиторием.")
        return

    if not check_git_auth():
        print("❌ Пожалуйста, настройте Git или GitHub CLI перед продолжением.")
        return

    modified, untracked = get_modified_and_untracked_files()

    if not modified and not untracked:
        print("✅ Нет изменённых или новых файлов.")
        print("💡 Если файлы новые — добавьте их вручную через 'git add <файл>' или 'git add .', затем снова запустите скрипт.")
        return

    print(f"📝 Обнаружены изменённые файлы:\n{chr(10).join(modified) if modified else 'Нет'}")
    print(f"🆕 Обнаружены новые файлы:\n{chr(10).join(untracked) if untracked else 'Нет'}")

    confirm = input("\n✅ Автоматически закоммитить и отправить все эти файлы? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Отменено пользователем.")
        return

    commit_msg = input("📝 Введите сообщение коммита: ").strip()
    if not commit_msg:
        print("❌ Сообщение коммита не может быть пустым.")
        return

    print("\n🔄 Добавляем все изменённые и новые файлы в коммит (git add .)...")
    out, err, code = run_command_shell("git add .")
    if code != 0:
        print(f"❌ Ошибка при добавлении файлов: {err}")
        return

    print("📝 Делаем коммит...")
    out, err, code = run_command_safe(["git", "commit", "-m", commit_msg])
    if code != 0:
        print(f"❌ Ошибка при коммите: {err}")
        return

    print("🔄 Синхронизируем с GitHub (git pull)...")
    out, err, code = run_command_shell("git pull --rebase")
    if code != 0:
        print(f"⚠️ Ошибка при pull (может быть конфликт): {err}")
        print("💡 Рекомендуется вручную разрешить конфликты или выполнить git pull без --rebase.")
        return

    print("📤 Отправляем изменения на GitHub...")
    out, err, code = run_command_shell("git push")
    if code != 0:
        print(f"❌ Ошибка при отправке: {err}")
        return

    print("✅ Успешно отправлено на GitHub!")

if __name__ == "__main__":
    main()