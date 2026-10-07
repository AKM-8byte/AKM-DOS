"""AKM-DOS 0.8 - existing command shell backed by shared core services."""

import json
from pathlib import Path

from akm import AKMCore
from akm.shell.commands import filesystem as file_commands
from akm.version import VERSION

ROOT = Path(__file__).resolve().parent
USERS_DIR = ROOT / "Users"
LEGACY_USER_FILE = ROOT / "Kullanıcı" / "kullanıcı_ad.txt"


class AKMShell:
    def __init__(self, core: AKMCore | None = None) -> None:
        self.running = True
        self.core = core if core is not None else AKMCore(ROOT)
        if self.core.started:
            assert self.core.username is not None
            self.username = self.core.username
        else:
            self.username = self._load_user()
        self._prepare_home()
        assert self.core.filesystem is not None
        self.filesystem = self.core.filesystem
        self.home = self.filesystem.home
        self.cwd = self.home

        self.commands = {
            "yardım": self.cmd_help,
            "help": self.cmd_help,
            "sürüm": self.cmd_version,
            "version": self.cmd_version,
            "temizle": self.cmd_clear,
            "clear": self.cmd_clear,
            "pwd": self.cmd_pwd,
            "dir": self.cmd_dir,
            "ls": self.cmd_dir,
            "cd": self.cmd_cd,
            "mkdir": self.cmd_mkdir,
            "touch": self.cmd_touch,
            "type": self.cmd_type,
            "cat": self.cmd_type,
            "sil": self.cmd_delete,
            "del": self.cmd_delete,
            "hesap": self.cmd_calc,
            "aka": self.cmd_explorer,
            "web": self.cmd_browser,
            "notepad": self.cmd_notepad,
            "aygıtlar": self.cmd_devices,
            "systeminfo": self.cmd_systeminfo,
            "settings": self.cmd_settings,
            "renk": self.cmd_color,
            "çıkış": self.cmd_exit,
            "kapat": self.cmd_exit,
            "exit": self.cmd_exit,
        }

    def _load_user(self) -> str:
        # Eski AKM-DOS kullanıcı adını mümkünse koru.
        name = self.core.settings.legacy_username(self.core.root / 'Kullanıcı' / 'kullanıcı_ad.txt')
        if name:
            return self._safe_username(name)
        name = self.core.settings.get('user.name')
        if isinstance(name, str) and name.strip():
            return self._safe_username(name)
        name = self.core.settings.profile_username(self.core.root / 'Users')
        if name:
            return self._safe_username(name)

        print("AKM-DOS'a hoş geldin. Sana ne ile hitap etmeliyim?")
        name = input("> ").strip() or "User"
        return self._safe_username(name)

    @staticmethod
    def _safe_username(name: str) -> str:
        safe = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        return safe or "User"

    def _prepare_home(self) -> None:
        if not self.core.started:
            self.core.start(self.username)

    def prompt(self) -> str:
        try:
            relative = self.cwd.relative_to(self.home)
            location = "~" if str(relative) == "." else f"~/{relative}"
        except ValueError:
            location = self.filesystem.virtual_path(self.cwd) or str(self.cwd)
        return f"{self.username}@AKM-DOS:{location}> "

    def run(self) -> None:
        print(f"AKM Komut Sistemi {VERSION}")
        print("'yardım' yazarak komutları görebilirsin.\n")

        while self.running:
            try:
                raw = input(self.prompt()).strip()
                if not raw:
                    continue

                command, *rest = raw.split(maxsplit=1)
                argument = rest[0] if rest else ""
                handler = self.commands.get(command.lower())

                if handler:
                    handler(argument)
                else:
                    print(f"Bilinmeyen komut: {command}. Yardım için 'yardım' yaz.")
            except (KeyboardInterrupt, EOFError):
                self.running = False
                print("\nAKM-DOS kapatılıyor...")
                break
            except Exception as exc:
                self._log_error(exc)
                print(f"Hata: {exc}")

    def _log_error(self, exc: Exception) -> None:
        try:
            self.core.log_error(exc)
        except OSError as log_error:
            print(f'Hata kaydı yazılamadı: {log_error}')

    def resolve_path(self, value: str | Path) -> Path:
        return self.filesystem.resolve(value, self.cwd)

    def cmd_help(self, _):
        print(
            """AKM-DOS komutları:
  yardım              Komut listesini göster
  sürüm               Sürümü göster
  dir / ls            Dosyaları listele
  cd <klasör>         Klasör değiştir
  pwd                 Mevcut konumu göster
  mkdir <ad>          Klasör oluştur
  touch <ad>          Boş dosya oluştur
  type <dosya>        Metin dosyasını göster
  sil <yol>           Dosya veya boş klasör sil
  hesap               Hesap makinesi
  aka                 Dosya gezginini aç
  web                 AKM Browser'ı aç
  notepad             Not defterini aç
  aygıtlar            Windows Aygıt Yöneticisi
  systeminfo          Sistem bilgisini göster
  settings            Ortak JSON ayarlarını göster / değiştir
  renk <kod>          Windows konsol rengini değiştir
  temizle             Ekranı temizle
  kapat / çıkış       AKM-DOS'u kapat"""
        )

    def cmd_version(self, _):
        print(f"AKM-DOS / AKS {VERSION}")

    def cmd_clear(self, _):
        self.core.platform.clear_console()

    def cmd_pwd(self, _):
        print(self.filesystem.virtual_path(self.cwd) or self.cwd)

    def cmd_dir(self, argument):
        file_commands.directory(self, argument)

    def cmd_cd(self, argument):
        file_commands.change_directory(self, argument)

    def cmd_mkdir(self, argument):
        file_commands.mkdir(self, argument)

    def cmd_touch(self, argument):
        file_commands.touch(self, argument)

    def cmd_type(self, argument):
        file_commands.show_text(self, argument)

    def cmd_delete(self, argument):
        file_commands.delete(self, argument)

    def cmd_calc(self, _):
        try:
            first = float(input("1. sayı: "))
            operator = input("İşlem (+, -, *, /): ").strip()
            second = float(input("2. sayı: "))
            operations = {
                "+": lambda: first + second,
                "-": lambda: first - second,
                "*": lambda: first * second,
                "/": lambda: first / second,
            }
            if operator not in operations:
                print("Geçersiz işlem.")
                return
            print("Sonuç:", operations[operator]())
        except (ValueError, ZeroDivisionError) as exc:
            print("Hesaplama hatası:", exc)

    def _open_python_program(self, relative_path: str | Path) -> None:
        try:
            self.core.platform.launch_python(relative_path)
        except FileNotFoundError:
            print(f"Program bulunamadı: {relative_path}")

    def cmd_explorer(self, _):
        self._open_python_program("aka.py")

    def cmd_browser(self, _):
        self._open_python_program(Path("Programs") / "webbrowser.py")

    def cmd_notepad(self, _):
        self._open_python_program(Path("Programs") / "notepad.py")

    def cmd_devices(self, _):
        self.core.platform.open_device_manager()

    def cmd_systeminfo(self, _):
        info = self.core.platform.system_info()
        print(f"Sistem : {info['system']} {info['release']}")
        print(f"Makine : {info['machine']}")
        print(f"Python : {info['python']}")
        print(f"Kullanıcı: {self.username}")

    def cmd_color(self, argument):
        if not argument:
            print("Kullanım: renk <Windows renk kodu>")
            return
        self.core.platform.set_console_color(argument)

    def cmd_settings(self, argument):
        parts = argument.split(maxsplit=2)
        if not parts:
            print(json.dumps(self.core.settings.all(), ensure_ascii=False, indent=2))
        elif parts[0] == 'get' and len(parts) == 2:
            values = self.core.settings.all()
            print(json.dumps(values[parts[1]], ensure_ascii=False) if parts[1] in values else 'Ayar bulunamadı.')
        elif parts[0] == 'set' and len(parts) == 3:
            if parts[1] == 'user.name':
                print('Aktif kullanıcı adı settings komutuyla değiştirilemez.')
                return
            try:
                value = json.loads(parts[2])
            except json.JSONDecodeError:
                value = parts[2]
            self.core.settings.set(parts[1], value)
            print('Ayar kaydedildi.')
        else:
            print('Kullanım: settings | settings get <anahtar> | settings set <anahtar> <değer>')

    def cmd_exit(self, _):
        self.running = False
        print("AKM-DOS kapatıldı.")


def main() -> int:
    try:
        AKMShell().run()
    except (KeyboardInterrupt, EOFError):
        print('\nAKM-DOS kapatılıyor...')
    except Exception as exc:
        print(f'AKM-DOS başlatılamadı: {exc}')
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
