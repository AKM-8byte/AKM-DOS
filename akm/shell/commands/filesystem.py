"""File command presentation; all file operations use FileSystemService."""

from pathlib import Path
from typing import Protocol

from ...services.filesystem import FileSystemService


class FileContext(Protocol):
    filesystem: FileSystemService
    home: Path
    cwd: Path


def directory(context: FileContext, argument: str) -> None:
    target = context.filesystem.resolve(argument, context.cwd) if argument else context.cwd
    if not context.filesystem.is_directory(target):
        print('Klasör bulunamadı.')
        return
    entries = context.filesystem.list_directory(target)
    if not entries:
        print('(boş klasör)')
    for item in entries:
        marker = '<DIR>' if item.is_directory else '     '
        print(f'{marker} {item.name}')


def change_directory(context: FileContext, argument: str) -> None:
    target = context.filesystem.resolve(argument, context.cwd)
    if context.filesystem.is_directory(target):
        context.cwd = target
    else:
        print('Klasör bulunamadı.')


def mkdir(context: FileContext, argument: str) -> None:
    if not argument:
        print('Kullanım: mkdir <klasör-adı>')
        return
    context.filesystem.mkdir(argument, context.cwd)
    print('Klasör oluşturuldu.')


def touch(context: FileContext, argument: str) -> None:
    if not argument:
        print('Kullanım: touch <dosya-adı>')
        return
    context.filesystem.touch(argument, context.cwd)
    print('Dosya hazır.')


def show_text(context: FileContext, argument: str) -> None:
    if not argument:
        print('Kullanım: type <dosya>')
        return
    if not context.filesystem.is_file(argument, context.cwd):
        print('Dosya bulunamadı.')
        return
    try:
        print(context.filesystem.read_text(argument, context.cwd))
    except UnicodeDecodeError:
        print('Bu dosya UTF-8 metin dosyası değil.')


def delete(context: FileContext, argument: str) -> None:
    if not argument:
        print('Kullanım: sil <dosya-veya-boş-klasör>')
        return
    if context.filesystem.resolve(argument, context.cwd) == context.home:
        print('Kullanıcı ana klasörü silinemez.')
        return
    kind = context.filesystem.delete(argument, context.cwd)
    messages = {'file': 'Dosya silindi.', 'directory': 'Boş klasör silindi.',
                None: 'Dosya veya klasör bulunamadı.'}
    print(messages[kind])
