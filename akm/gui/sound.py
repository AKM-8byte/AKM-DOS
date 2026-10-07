"""Non-blocking startup audio, local to the presentation layer."""
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect


class StartupSound(QObject):
    warning = Signal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.requested = False
        self.effect = QSoundEffect(self)
        self.effect.setVolume(0.35)
        self.effect.setLoopCount(1)
        self.effect.statusChanged.connect(self._status_changed)

    def play(self):
        if not self.path.is_file():
            self.warning.emit('Başlangıç sesi bulunamadı; sessiz devam ediliyor.')
            return
        self.requested = True
        self.effect.setSource(QUrl.fromLocalFile(str(self.path.resolve())))
        self._status_changed()

    def _status_changed(self):
        if not self.requested:
            return
        if self.effect.status() == QSoundEffect.Status.Ready:
            self.requested = False
            self.effect.play()
        elif self.effect.status() == QSoundEffect.Status.Error:
            self.requested = False
            self.warning.emit('Ses aygıtı veya dosyası kullanılamıyor; sessiz devam ediliyor.')

    def stop(self):
        self.requested = False
        self.effect.stop()
