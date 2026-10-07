"""Startup orchestration without a dependency on a GUI framework."""

from pathlib import Path

from akm import AKMCore


class BootSession:
    """One startup attempt. A failed attempt never provides a desktop core."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.core: AKMCore | None = None
        self.error = ''
        self.service_status = {}
        self.system_info = {}
        self.prepared_core: AKMCore | None = None
        self.suggested_username = ''

    def prepare(self) -> AKMCore:
        """POST initializes services, but never invents a user before login."""
        self.core = None
        self.error = ''
        self.service_status = {}
        self.system_info = {}
        self.prepared_core = None
        self.suggested_username = ''
        try:
            core = AKMCore(self.root)
            self.system_info = core.platform.system_info()
            name = core.settings.legacy_username(core.root / 'Kullanıcı' / 'kullanıcı_ad.txt')
            if not name:
                saved = core.settings.get('user.name')
                if isinstance(saved, str) and saved.strip():
                    name = saved
            if not name:
                name = core.settings.profile_username(core.root / 'Users') or ''
            self.suggested_username = name
            self.prepared_core = core
            self.service_status = dict(core.service_status)
            return core
        except Exception as exc:
            self.error = str(exc)
            raise

    def login(self, fallback_username: str) -> AKMCore:
        """Start the existing single-user session; there is no password backend."""
        core = self.prepared_core
        if core is None:
            raise RuntimeError('BIOS preparation must complete before login.')
        self.core = None
        self.error = ''
        try:
            name = self.suggested_username or fallback_username
            if not isinstance(name, str):
                raise ValueError('Kaydedilmiş kullanıcı adı metin olmalıdır.')
            # Match the existing Shell's normalization of legacy names.
            name = ''.join(c for c in name if c.isalnum() or c in ' _-').strip()
            if not name:
                raise ValueError('Bir kullanıcı adı girin.')
            core.start(name)
            self.core = core
            self.service_status = dict(core.service_status)
            return core
        except Exception as exc:
            self.error = str(exc)
            if core:
                self.service_status = dict(core.service_status)
            raise

    def start(self, fallback_username: str) -> AKMCore:
        """Compatibility entry point for a complete, non-GUI startup attempt."""
        self.prepare()
        return self.login(fallback_username)
