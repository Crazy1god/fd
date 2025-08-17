from typing import Optional, List
from sqlalchemy.orm import Session

from app.models import AppUser, Coords, Level, PerevalAdded, Image, PerevalStatus
from app.schemas import SubmitIn, ImageIn


class FSTRRepository:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_user(self, email: str, fam: str, name: str, otc: Optional[str], phone: Optional[str]) -> AppUser:
        user: Optional[AppUser] = self.db.query(AppUser).filter(AppUser.email == email).one_or_none()
        if user:
            # при желании — мягко обновляем контактные данные
            updated = False
            if phone and user.phone != phone:
                user.phone = phone
                updated = True
            if fam and user.fam != fam:
                user.fam = fam
                updated = True
            if name and user.name != name:
                user.name = name
                updated = True
            if otc is not None and user.otc != otc:
                user.otc = otc
                updated = True
            if updated:
                self.db.add(user)
            return user

        user = AppUser(email=email, fam=fam, name=name, otc=otc, phone=phone)
        self.db.add(user)
        self.db.flush()  # получаем user.id
        return user

    def _create_coords(self, latitude: float, longitude: float, height: Optional[int]) -> Coords:
        coords = Coords(latitude=latitude, longitude=longitude, height=height)
        self.db.add(coords)
        self.db.flush()
        return coords

    def _create_level(self, level_in: Optional[dict]) -> Optional[Level]:
        if not level_in:
            return None
        level = Level(
            winter=level_in.get("winter"),
            spring=level_in.get("spring"),
            summer=level_in.get("summer"),
            autumn=level_in.get("autumn"),
        )
        self.db.add(level)
        self.db.flush()
        return level

    def _create_images(self, pereval_id: int, images: List[ImageIn]) -> None:
        for img in images:
            image = Image(pereval_id=pereval_id, title=img.title, url=img.url)
            self.db.add(image)

    def create_pereval(self, payload: SubmitIn) -> int:
        # 1) пользователь
        user = self._get_or_create_user(
            email=payload.user.email,
            fam=payload.user.fam,
            name=payload.user.name,
            otc=payload.user.otc,
            phone=payload.user.phone,
        )

        # 2) координаты
        coords = self._create_coords(
            latitude=payload.coords.latitude,
            longitude=payload.coords.longitude,
            height=payload.coords.height,
        )

        # 3) уровень (опционально)
        level = self._create_level(payload.level.dict() if payload.level else None)

        # 4) перевал со статусом 'new' независимо от входных данных
        pereval = PerevalAdded(
            user_id=user.id,
            coords_id=coords.id,
            level_id=level.id if level else None,
            beauty_title=payload.beauty_title,
            title=payload.title,
            other_titles=payload.other_titles,
            connect=payload.connect,
            status=PerevalStatus.new,
        )
        self.db.add(pereval)
        self.db.flush()

        # 5) изображения
        if payload.images:
            self._create_images(pereval.id, payload.images)

        # 6) и коммит
        self.db.commit()
        return pereval.id