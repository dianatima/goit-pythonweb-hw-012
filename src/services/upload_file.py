import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Ініціалізація сервісу для завантаження файлів на Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантажує файл на Cloudinary і генерує URL для доступу до зображення.

        Формує унікальний ідентифікатор для користувача і завантажує файл на сервер.
        Після успішного завантаження повертає URL зображення з певними параметрами (розмір, обрізка).

        Аргументи:
            file: Файл для завантаження.
            username: Ім'я користувача для формування унікального public_id.

        Повертає:
            str: URL зображення, доступного на Cloudinary.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
