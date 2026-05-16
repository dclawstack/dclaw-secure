"""Asset model for the security asset inventory."""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import String, Text, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.core.utils import utc_now


class AssetType(StrEnum):
    SERVER = "server"
    CONTAINER = "container"
    DATABASE = "database"
    S3_BUCKET = "s3_bucket"
    API = "api"
    DOMAIN = "domain"
    REPOSITORY = "repository"
    WORKSTATION = "workstation"


class Environment(StrEnum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"


class AssetStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"


class CloudProvider(StrEnum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on_premise"


class Asset(Base):
    """A registerable asset in the security inventory."""

    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False)
    environment: Mapped[Environment] = mapped_column(
        Enum(Environment), nullable=False, default=Environment.PRODUCTION
    )
    status: Mapped[AssetStatus] = mapped_column(
        Enum(AssetStatus), nullable=False, default=AssetStatus.ACTIVE
    )
    cloud_provider: Mapped[CloudProvider | None] = mapped_column(
        Enum(CloudProvider), nullable=True
    )
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    owner_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:
        return f"<Asset {self.name} ({self.asset_type.value})>"
