import shutil
from abc import abstractmethod, ABC
from ftplib import FTP
from pathlib import Path

import owncloud
import requests
from six.moves.urllib import parse

MESSAGE_SUCCESS_COPIED = "Файл {src_file} доставлен в {dest_file}"
DRY_MODE_MESSAGE = "Был бы доставлен файл {src_file} в {dest_file}"
SKIP_MESSAGE = "Файл уже существует в {dest_file}. "


class CustomClientForOwnCloud(owncloud.Client):
    """
    Клиент для работы с owncloud,
     с корректировкой _webdav_url
    (owncloud/public.php/webdav).
    """

    def anon_login(self, folder_token, folder_password=''):
        self._session = requests.session()
        self._session.verify = self._verify_certs
        self._session.auth = (folder_token, folder_password)

        url_components = parse.urlparse(self.url)
        self._davpath = url_components.path + 'owncloud/public.php/webdav'
        self._webdav_url = self.url + 'owncloud/public.php/webdav'


class FileDelivery(ABC):
    """ Абстрактный класс доставки файлов. """

    def __init__(self, src_files, dest_path=None, override=False, dry_run=False):
        self.src_files = src_files
        self.dest_path = dest_path
        self.override = override
        self.dry_run = dry_run

    @abstractmethod
    def deliver_files(self):
        pass


class LocalFileDelivery(FileDelivery):
    """ Класс доставки в папку. """

    def deliver_files(self):
        for src_file in self.src_files:
            dest_file = Path(self.dest_path) / src_file.name
            if self.dry_run:
                print(DRY_MODE_MESSAGE.format(
                    src_file=src_file,
                    dest_file=dest_file
                ))
            else:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                if self.override or not dest_file.exists():
                    try:
                        shutil.copy2(src_file, dest_file)
                        print(MESSAGE_SUCCESS_COPIED.format(
                            src_file=src_file,
                            dest_file=dest_file
                        ))
                    except KeyboardInterrupt:
                        print("Путь до исходных файлов должен быть полным.")
                else:
                    print(SKIP_MESSAGE.format(dest_file=dest_file))


class FTPFileDelivery(FileDelivery):
    """ Класс доставки на FTP сервер. """

    def __init__(self, src_files, dest_path, ftp_details, override=False,
                 dry_run=False):
        super().__init__(src_files, dest_path, override, dry_run)
        self.ftp = FTP(ftp_details['host'])
        self.ftp.login(ftp_details['username'], ftp_details['password'])

    def deliver_files(self):
        for src_file in self.src_files:
            dest_file = str(
                Path(self.dest_path) / src_file.name
            ).replace("\\", "/")
            if self.dry_run:
                print(DRY_MODE_MESSAGE.format(
                    src_file=src_file,
                    dest_file=self.ftp.host
                ))
            else:
                if self.override or not (src_file.name in self.ftp.nlst()):
                    with open(src_file, 'rb') as file:
                        self.ftp.storbinary(f'STOR {dest_file}', file)
                    print(MESSAGE_SUCCESS_COPIED.format(
                            src_file=src_file,
                            dest_file=self.ftp.host
                        ))
                else:
                    print(SKIP_MESSAGE.format(dest_file=self.ftp.host))
        self.ftp.quit()


class OwnCloudFileDelivery(FileDelivery):
    """ Класс доставки в облачное хранилище."""

    def __init__(self, src_files, owncloud_details, override=False,
                 dry_run=False):
        super().__init__(src_files, owncloud_details["url"], override, dry_run)
        self.oc = CustomClientForOwnCloud.from_public_link(
            owncloud_details["url"],
            folder_password=owncloud_details["password"]
        )

    def deliver_files(self):
        for src_file in self.src_files:
            if self.dry_run:
                print(DRY_MODE_MESSAGE.format(
                    src_file=src_file,
                    dest_file=self.dest_path
                ))
            else:
                try:
                    self.oc.file_info(src_file.name)
                    file_not_exist = False
                except owncloud.HTTPResponseError:
                    file_not_exist = True
                if self.override or file_not_exist:
                    self.oc.drop_file(src_file)
                    print(MESSAGE_SUCCESS_COPIED.format(
                            src_file=src_file,
                            dest_file=self.dest_path
                        ))
                else:
                    print(SKIP_MESSAGE.format(dest_file=self.dest_path))
