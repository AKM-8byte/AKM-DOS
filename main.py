"""AKM-DOS 0.6 - modular command shell."""

import os
import platform
import shutil
import subprocess
from pathlib import Path

VERSION = "0.6 Alpha"
ROOT = Path(__file__).resolve().parent
USERS_DIR = ROOT / "Users"
LEGACY_USER_FILE = ROOT / "Kullanıcı" / "kullanıcı_ad.txt"


class AKMShell:
    def __init__(self):
        self.running = True
        self.username = self._load_user()
        self.home = USERS_DIR / self.username
        self._prepare_home()
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
            "renk": self.cmd_color,
            "çıkış": self.cmd_exit,
            "kapat": self.cmd_exit,
            "exit": self.cmd_exit,
        }

    def _load_user(self):
        USERS_DIR.mkdir(exist_ok=True)

        # Eski AKM-DOS kullanıcı adını mümkünse koru.
        if LEGACY_USER_FILE.exists():
            name = LEGACY_USER_FILE.read_text(encoding="utf-8").strip()
            if name:
                return self._safe_username(name)

        print("AKM-DOS'a hoş geldin. Sana ne ile hitap etmeliyim?")
        name = input("> ").strip() or "User"
        return self._safe_username(name)

    @staticmethod
    def _safe_username(name):
        safe = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        return safe or "User"

    def _prepare_home(self):
        for folder in ("Desktop", "Documents", "Downloads", "Settings"):
            (self.home / folder).mkdir(parents=True, exist_ok=True)

        profile = self.home / "Settings" / "profile.txt"
        if not profile.exists():
            profile.write_text(f"username={self.username}\n", encoding="utf-8")

    def prompt(self):
        try:
            relative = self.cwd.relative_to(self.home)
            location = "~" if str(relative) == "." else f"~/{relative}"
        except ValueError:
            location = str(self.cwd)
        return f"{self.username}@AKM-DOS:{location}> "

    def run(self):
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
                print("\nAKM-DOS kapatılıyor...")
                break
            except Exception as exc:
                self._log_error(exc)
                print(f"Hata: {exc}")

    def _log_error(self, exc):
        (ROOT / "hatakyt.txt").write_text(
            f"{type(exc).__name__}: {exc}", encoding="utf-8"
        )

    def resolve_path(self, value):
        if not value or value == "~":
            return self.home
        path = Path(value)
        return path.resolve() if path.is_absolute() else (self.cwd / path).resolve()

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
  renk <kod>          Windows konsol rengini değiştir
  temizle             Ekranı temizle
  kapat / çıkış       AKM-DOS'u kapat"""
        )

    def cmd_version(self, _):
        print(f"AKM-DOS / AKS {VERSION}")

    def cmd_clear(self, _):
        os.system("cls" if os.name == "nt" else "clear")

    def cmd_pwd(self, _):
        print(self.cwd)

    def cmd_dir(self, argument):
        target = self.resolve_path(argument) if argument else self.cwd
        if not target.is_dir():
            print("Klasör bulunamadı.")
            return
        entries = sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        if not entries:
            print("(boş klasör)")
            return
        for item in entries:
            marker = "<DIR>" if item.is_dir() else "     "
            print(f"{marker} {item.name}")

    def cmd_cd(self, argument):
        target = self.resolve_path(argument)
        if target.is_dir():
            self.cwd = target
        else:
            print("Klasör bulunamadı.")

    def cmd_mkdir(self, argument):
        if not argument:
            print("Kullanım: mkdir <klasör-adı>")
            return
        self.resolve_path(argument).mkdir(parents=True, exist_ok=False)
        print("Klasör oluşturuldu.")

    def cmd_touch(self, argument):
        if not argument:
            print("Kullanım: touch <dosya-adı>")
            return
        target = self.resolve_path(argument)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
        print("Dosya hazır.")

    def cmd_type(self, argument):
        if not argument:
            print("Kullanım: type <dosya>")
            return
        target = self.resolve_path(argument)
        if not target.is_file():
            print("Dosya bulunamadı.")
            return
        try:
            print(target.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            print("Bu dosya UTF-8 metin dosyası değil.")

    def cmd_delete(self, argument):
        if not argument:
            print("Kullanım: sil <dosya-veya-boş-klasör>")
            return
        target = self.resolve_path(argument)
        if target == self.home:
            print("Kullanıcı ana klasörü silinemez.")
        elif target.is_file():
            target.unlink()
            print("Dosya silindi.")
        elif target.is_dir():
            target.rmdir()
            print("Boş klasör silindi.")
        else:
            print("Dosya veya klasör bulunamadı.")

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

    def _open_python_program(self, relative_path):
        path = ROOT / relative_path
        if not path.exists():
            print(f"Program bulunamadı: {relative_path}")
            return
        subprocess.Popen([os.sys.executable, str(path)], cwd=str(ROOT))

    def cmd_explorer(self, _):
        self._open_python_program("aka.py")

    def cmd_browser(self, _):
        self._open_python_program(Path("Programs") / "webbrowser.py")

    def cmd_notepad(self, _):
        self._open_python_program(Path("Programs") / "notepad.py")

    def cmd_devices(self, _):
        if os.name != "nt":
            print("Bu komut yalnızca Windows'ta kullanılabilir.")
            return
        subprocess.Popen(["devmgmt.msc"], shell=True)

    def cmd_systeminfo(self, _):
        print(f"Sistem : {platform.system()} {platform.release()}")
        print(f"Makine : {platform.machine()}")
        print(f"Python : {platform.python_version()}")
        print(f"Kullanıcı: {self.username}")

    def cmd_color(self, argument):
        if os.name != "nt":
            print("Renk komutu şu anda yalnızca Windows'ta destekleniyor.")
            return
        if not argument:
            print("Kullanım: renk <Windows renk kodu>")
            return
        os.system(f"color {argument}")

    def cmd_exit(self, _):
        self.running = False
        print("AKM-DOS kapatıldı.")


if __name__ == "__main__":
    AKMShell().run()
