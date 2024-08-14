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
    files_for_folder = []
    files_for_ftp = []
    files_for_cloud = []
    for file_info in FILES_ENDPOINTS["files"]:
        src_file = Path(args.src) / file_info["name"]
        for endpoint in file_info["endpoints"]:
            if endpoint == "folder":
                files_for_folder.append(src_file)
            elif endpoint == "ftp":
                files_for_ftp.append(src_file)
            elif endpoint == "owncloud":
                files_for_cloud.append(src_file)
            else:
                print(f"Unknown endpoint: {endpoint}")
                continue
    if files_for_folder:
        folder_delivery = LocalFileDelivery(
            files_for_folder,
            str(BASE_DIR) + (os.getenv("FOLDER_NAME")),
            override=args.override,
            dry_run=args.dry
        )
        folder_delivery.deliver_files()
    if files_for_ftp:
        ftp_delivery = FTPFileDelivery(
            files_for_ftp,
            os.getenv("FTP_PATH"),
            ftp_details,
            override=args.override,
            dry_run=args.dry
        )
        ftp_delivery.deliver_files()
    if files_for_cloud:
        cloud_delivery = OwnCloudFileDelivery(
            files_for_cloud,
            owncloud_details,
            override=args.override,
            dry_run=args.dry
        )
        cloud_delivery.deliver_files()


if __name__ == "__main__":
    main()
