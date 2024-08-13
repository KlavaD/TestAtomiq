import argparse
import os
from pathlib import Path

from dotenv import load_dotenv

from enter_data import FILES_ENDPOINTS
from models import LocalFileDelivery, FTPFileDelivery, OwnCloudFileDelivery

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


def configure_argument_parser():
    parser = argparse.ArgumentParser(
        description="Доставка файлов по нескольким маршрутам."
    )
    parser.add_argument(
        "src",
        type=str,
        help="Путь до исходных файлов."
    )
    parser.add_argument(
        "-o",
        "--override",
        action="store_true",
        help="Перезаписать имеющийся файл."
    )
    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        help="Запуск в режиме 'DRY'."
    )
    return parser


def main():
    parser = configure_argument_parser()
    args = parser.parse_args()
    ftp_details = {
        "host": os.getenv("FTP_HOST"),
        "username": os.getenv("FTP_USERNAME"),
        "password": os.getenv("FTP_PASSWORD")
    }
    owncloud_details = {
        "url": os.getenv("CLOUD_URL"),
        "password": os.getenv("CLOUD_PASSWORD")
    }
    for file_info in FILES_ENDPOINTS["files"]:
        src_file = Path(args.src) / file_info["name"]
        for endpoint in file_info["endpoints"]:
            if endpoint == "folder":
                dest_path = str(BASE_DIR) + (os.getenv("FOLDER_NAME"))
                delivery = LocalFileDelivery(
                    src_file,
                    dest_path,
                    override=args.override,
                    dry_run=args.dry
                )
            elif endpoint == "ftp":
                delivery = FTPFileDelivery(
                    src_file, "/", ftp_details,
                    override=args.override,
                    dry_run=args.dry
                )
            elif endpoint == "owncloud":
                delivery = OwnCloudFileDelivery(
                    src_file,
                    owncloud_details,
                    override=args.override,
                    dry_run=args.dry
                )
            else:
                print(f"Unknown endpoint: {endpoint}")
                continue

            delivery.deliver_file()


if __name__ == "__main__":
    main()
