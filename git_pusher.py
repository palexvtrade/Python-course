import os
import subprocess

def run_command(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def check_git_auth():
    stdout, _, _ = run_command("git config user.name")
    name = stdout.strip()
    if not name:
        print("❌ Не установлено имя пользователя Git (git config user.name)")
        return False

    stdout, _, _ = run_command("git config user.email")
    email = stdout.strip()
    if not email:
        print("❌ Не установлен email пользователя Git (git config user.email)")
        return False

    stdout, _, code = run_command("gh auth status")
    if code == 0:
        print(f"✅ Авторизован в GitHub через GitHub CLI как: {name}")
        return True
    else:
        print(f"⚠️ GitHub CLI не авторизован, но Git настроен: {name} <{email}>")
        print("💡 Если используешь SSH или токен — всё должно работать.")
        return True

def get_modified_files():
    stdout, stderr, code = run_command("git status --porcelain")
    if code != 0:
        print(f"❌ Ошибка выполнения 'git status': {stderr}")
        return []

    modified = []
    for line in stdout.splitlines():
        if line.strip():
            status = line[:2].strip()
            file_path = line[3:]
            if status in ['M', 'A', 'D', 'R', 'C']:
                modified.append(file_path)
    return modified

def main():
    print("🔍 Проверка статуса репозитория и авторизации...")

    _, _, code = run_command("git status")
    if code != 0:
        print("❌ Текущая директория не является Git-репозиторием.")
        return

    if not check_git_auth():
        print("❌ Пожалуйста, настройте Git или GitHub CLI перед продолжением.")
        return

    modified = get_modified_files()

    if not modified:
        print("✅ Нет изменённых или отслеживаемых файлов.")
        print("💡 Если файлы новые — добавьте их вручную через 'git add <файл>' или 'git add .', затем снова запустите скрипт.")
        return

    print(f"📝 Обнаружены изменённые файлы:\n{chr(10).join(modified)}")

    confirm = input("\n✅ Автоматически закоммитить и отправить эти файлы? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Отменено пользователем.")
        return

    commit_msg = input("📝 Введите сообщение коммита: ").strip()
    if not commit_msg:
        print("❌ Сообщение коммита не может быть пустым.")
        return

    print("\n🔄 Добавляем все изменённые файлы в коммит...")
    out, err, code = run_command("git add .")
    if code != 0:
        print(f"❌ Ошибка при добавлении файлов: {err}")
        return

    print("📝 Делаем коммит...")
    # Теперь используем безопасное форматирование сообщения коммита
    # Оборачиваем в двойные кавычки и экранируем
    import shlex
    cmd_commit = ["git", "commit", "-m", commit_msg]
    result = subprocess.run(cmd_commit, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Ошибка при коммите: {result.stderr}")
        return

    print("📤 Отправляем изменения на GitHub...")
    out, err, code = run_command("git push")
    if code != 0:
        print(f"❌ Ошибка при отправке: {err}")
        return

    print("✅ Успешно отправлено на GitHub!")

if __name__ == "__main__":
    main()