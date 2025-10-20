"""Database repository for data access."""

import json
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.domain.models import Document, JournalEntry, JournalLine, PipelineRun
from src.rules.bas_dataset import BASAccount

Base = declarative_base()


class DocumentModel(Base):
    """Document database model."""
    __tablename__ = "documents"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    company_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    storage_key = Column(String(500), nullable=False)
    hash = Column(String(64), nullable=False, unique=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(PostgresUUID(as_uuid=True))


class JournalEntryModel(Base):
    """Journal entry database model."""
    __tablename__ = "journal_entries"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    company_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    series = Column(String(10), nullable=False)
    number = Column(String(20), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(PostgresUUID(as_uuid=True))

    # Relationships
    lines = relationship("JournalLineModel", back_populates="entry")


class JournalLineModel(Base):
    """Journal line database model."""
    __tablename__ = "journal_lines"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    entry_id = Column(PostgresUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    account = Column(String(20), nullable=False)
    side = Column(String(1), nullable=False)  # D or K
    amount = Column(Numeric(15, 2), nullable=False)
    dimension_project = Column(String(50))
    dimension_cost_center = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    entry = relationship("JournalEntryModel", back_populates="lines")


class PipelineRunModel(Base):
    """Pipeline run database model."""
    __tablename__ = "pipeline_runs"

    id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    document_id = Column(PostgresUUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    company_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    status = Column(String(20), default="pending")
    current_step = Column(String(50))
    receipt_doc = Column(JSONB)
    intent = Column(JSONB)
    proposal = Column(JSONB)
    journal_entry_id = Column(PostgresUUID(as_uuid=True))
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class PolicyModel(Base):
    """Policy database model."""
    __tablename__ = "policies"

    id = Column(String(50), primary_key=True)
    version = Column(String(20), nullable=False)
    country = Column(String(2), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    rules = Column(JSONB, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(PostgresUUID(as_uuid=True))


class BASAccountModel(Base):
    """BAS account database model."""
    __tablename__ = "bas_accounts"

    number = Column(String(10), primary_key=True)
    name = Column(String(200), nullable=False)
    account_class = Column(String(10), nullable=False)
    account_type = Column(String(50), nullable=False)
    vat_hint = Column(Numeric(4, 2))
    allowed_regions = Column(ARRAY(String(2)))
    bas_version = Column(String(20), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseRepository:
    """Database repository for data access."""

    def __init__(self, database_url: str):
        # Convert sync URL to async URL
        if database_url.startswith("postgresql://"):
            async_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            async_url = database_url

        self.engine = create_async_engine(async_url)
        self.SessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_session(self) -> AsyncSession:
        """Get database session."""
        return self.SessionLocal()

    # Document methods
    async def save_document(self, document: Document) -> Document:
        """Save document to database."""
        session = await self.get_session()
        try:
            db_document = DocumentModel(
                id=document.id,
                company_id=document.company_id,
                filename=document.filename,
                content_type=document.content_type,
                size=document.size,
                storage_key=document.storage_key,
                hash=document.hash,
                uploaded_at=document.uploaded_at,
                uploaded_by=document.uploaded_by
            )
            session.add(db_document)
            await session.commit()
            await session.refresh(db_document)
            return document
        finally:
            await session.close()

    async def get_document(self, document_id: UUID) -> Document | None:
        """Get document by ID."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(DocumentModel).filter(DocumentModel.id == document_id)
            )
            db_document = result.scalar_one_or_none()

            if not db_document:
                return None

            return Document(
                id=db_document.id,
                company_id=db_document.company_id,
                filename=db_document.filename,
                content_type=db_document.content_type,
                size=db_document.size,
                storage_key=db_document.storage_key,
                hash=db_document.hash,
                uploaded_at=db_document.uploaded_at,
                uploaded_by=db_document.uploaded_by
            )
        finally:
            await session.close()

    async def find_document_by_hash(self, file_hash: str) -> Document | None:
        """Find document by file hash."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(DocumentModel).filter(DocumentModel.hash == file_hash)
            )
            db_document = result.scalar_one_or_none()

            if not db_document:
                return None

            return Document(
                id=db_document.id,
                company_id=db_document.company_id,
                filename=db_document.filename,
                content_type=db_document.content_type,
                size=db_document.size,
                storage_key=db_document.storage_key,
                hash=db_document.hash,
                uploaded_at=db_document.uploaded_at,
                uploaded_by=db_document.uploaded_by
            )
        finally:
            await session.close()

    async def list_documents(self, company_id: UUID, limit: int = 50, offset: int = 0) -> list[Document]:
        """List documents for a company with pagination."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(DocumentModel)
                .filter(DocumentModel.company_id == company_id)
                .order_by(DocumentModel.uploaded_at.desc())
                .limit(limit)
                .offset(offset)
            )
            db_documents = result.scalars().all()

            documents = []
            for db_document in db_documents:
                document = Document(
                    id=db_document.id,
                    company_id=db_document.company_id,
                    filename=db_document.filename,
                    content_type=db_document.content_type,
                    size=db_document.size,
                    storage_key=db_document.storage_key,
                    hash=db_document.hash,
                    uploaded_at=db_document.uploaded_at,
                    uploaded_by=db_document.uploaded_by
                )
                documents.append(document)

            return documents
        finally:
            await session.close()

    # Journal entry methods
    async def save_journal_entry(self, entry: JournalEntry, lines: list[JournalLine]) -> JournalEntry:
        """Save journal entry and lines."""
        session = await self.get_session()
        try:
            # Save entry
            db_entry = JournalEntryModel(
                id=entry.id,
                company_id=entry.company_id,
                date=entry.date,
                series=entry.series,
                number=entry.number,
                notes=entry.notes,
                created_at=entry.created_at,
                created_by=entry.created_by
            )
            session.add(db_entry)

            # Save lines
            for line in lines:
                db_line = JournalLineModel(
                    id=line.id,
                    entry_id=line.entry_id,
                    account=line.account,
                    side=line.side,
                    amount=line.amount,
                    dimension_project=line.dimension_project,
                    dimension_cost_center=line.dimension_cost_center,
                    description=line.description,
                    created_at=line.created_at
                )
                session.add(db_line)

            await session.commit()
            return entry
        finally:
            await session.close()

    async def get_last_journal_number(self, company_id: UUID, series: str) -> str | None:
        """Get last journal number for series."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(JournalEntryModel).filter(
                    JournalEntryModel.company_id == company_id,
                    JournalEntryModel.series == series
                ).order_by(JournalEntryModel.number.desc()).limit(1)
            )
            db_entry = result.scalar_one_or_none()

            return db_entry.number if db_entry else None
        finally:
            await session.close()

    async def get_journal_entry(self, entry_id: UUID) -> JournalEntry | None:
        """Get journal entry by ID."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(JournalEntryModel).filter(JournalEntryModel.id == entry_id)
            )
            db_entry = result.scalar_one_or_none()

            if not db_entry:
                return None

            # Get journal lines
            lines_result = await session.execute(
                select(JournalLineModel).filter(JournalLineModel.entry_id == entry_id)
            )
            db_lines = lines_result.scalars().all()

            lines = []
            for db_line in db_lines:
                line = JournalLine(
                    id=db_line.id,
                    entry_id=db_line.entry_id,
                    account=db_line.account,
                    side=db_line.side,
                    amount=db_line.amount,
                    dimension_project=db_line.dimension_project,
                    dimension_cost_center=db_line.dimension_cost_center,
                    description=db_line.description,
                    created_at=db_line.created_at
                )
                lines.append(line)

            entry = JournalEntry(
                id=db_entry.id,
                company_id=db_entry.company_id,
                date=db_entry.date,
                series=db_entry.series,
                number=db_entry.number,
                notes=db_entry.notes,
                created_at=db_entry.created_at,
                created_by=db_entry.created_by,
                lines=lines
            )

            return entry
        finally:
            await session.close()

    async def list_journal_entries(self, company_id: UUID, limit: int = 50, offset: int = 0) -> list[JournalEntry]:
        """List journal entries for a company with pagination."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(JournalEntryModel)
                .filter(JournalEntryModel.company_id == company_id)
                .order_by(JournalEntryModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            db_entries = result.scalars().all()

            entries = []
            for db_entry in db_entries:
                # Get journal lines for this entry
                lines_result = await session.execute(
                    select(JournalLineModel).filter(JournalLineModel.entry_id == db_entry.id)
                )
                db_lines = lines_result.scalars().all()

                lines = []
                for db_line in db_lines:
                    line = JournalLine(
                        id=db_line.id,
                        entry_id=db_line.entry_id,
                        account=db_line.account,
                        side=db_line.side,
                        amount=db_line.amount,
                        dimension_project=db_line.dimension_project,
                        dimension_cost_center=db_line.dimension_cost_center,
                        description=db_line.description,
                        created_at=db_line.created_at
                    )
                    lines.append(line)

                entry = JournalEntry(
                    id=db_entry.id,
                    company_id=db_entry.company_id,
                    date=db_entry.date,
                    series=db_entry.series,
                    number=db_entry.number,
                    notes=db_entry.notes,
                    created_at=db_entry.created_at,
                    created_by=db_entry.created_by,
                    lines=lines
                )
                entries.append(entry)

            return entries
        finally:
            await session.close()

    # Pipeline run methods
    async def save_pipeline_run(self, pipeline_run: PipelineRun) -> PipelineRun:
        """Save pipeline run."""
        session = await self.get_session()
        try:
            db_run = PipelineRunModel(
                id=pipeline_run.id,
                document_id=pipeline_run.document_id,
                company_id=pipeline_run.company_id,
                status=pipeline_run.status,
                current_step=pipeline_run.current_step,
                receipt_doc=json.loads(pipeline_run.receipt_doc.json()) if pipeline_run.receipt_doc else None,
                intent=json.loads(pipeline_run.intent.json()) if pipeline_run.intent else None,
                proposal=json.loads(pipeline_run.proposal.json()) if pipeline_run.proposal else None,
                journal_entry_id=pipeline_run.journal_entry_id,
                error_message=pipeline_run.error_message,
                started_at=pipeline_run.started_at,
                completed_at=pipeline_run.completed_at,
                created_at=pipeline_run.created_at
            )
            session.add(db_run)
            await session.commit()
            return pipeline_run
        finally:
            await session.close()

    async def get_pipeline_run(self, run_id: UUID) -> PipelineRun | None:
        """Get pipeline run by ID."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(PipelineRunModel).filter(PipelineRunModel.id == run_id)
            )
            db_run = result.scalar_one_or_none()

            if not db_run:
                return None

            # Convert JSONB fields back to models
            receipt_doc = None
            if db_run.receipt_doc:
                from src.domain.models import ReceiptDoc
                receipt_doc = ReceiptDoc(**db_run.receipt_doc)

            intent = None
            if db_run.intent:
                from src.domain.models import Intent
                intent = Intent(**db_run.intent)

            proposal = None
            if db_run.proposal:
                from src.domain.models import PostingProposal
                proposal = PostingProposal(**db_run.proposal)

            return PipelineRun(
                id=db_run.id,
                document_id=db_run.document_id,
                company_id=db_run.company_id,
                status=db_run.status,
                current_step=db_run.current_step,
                receipt_doc=receipt_doc,
                intent=intent,
                proposal=proposal,
                journal_entry_id=db_run.journal_entry_id,
                error_message=db_run.error_message,
                started_at=db_run.started_at,
                completed_at=db_run.completed_at,
                created_at=db_run.created_at
            )
        finally:
            await session.close()

    async def list_pipeline_runs(self, company_id: UUID, limit: int = 50, offset: int = 0) -> list[PipelineRun]:
        """List pipeline runs for a company with pagination."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(PipelineRunModel)
                .filter(PipelineRunModel.company_id == company_id)
                .order_by(PipelineRunModel.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            db_runs = result.scalars().all()

            pipeline_runs = []
            for db_run in db_runs:
                # Convert JSONB fields back to models
                receipt_doc = None
                if db_run.receipt_doc:
                    from src.domain.models import ReceiptDoc
                    receipt_doc = ReceiptDoc(**db_run.receipt_doc)

                intent = None
                if db_run.intent:
                    from src.domain.models import Intent
                    intent = Intent(**db_run.intent)

                proposal = None
                if db_run.proposal:
                    from src.domain.models import PostingProposal
                    proposal = PostingProposal(**db_run.proposal)

                pipeline_run = PipelineRun(
                    id=db_run.id,
                    document_id=db_run.document_id,
                    company_id=db_run.company_id,
                    status=db_run.status,
                    current_step=db_run.current_step,
                    receipt_doc=receipt_doc,
                    intent=intent,
                    proposal=proposal,
                    journal_entry_id=db_run.journal_entry_id,
                    error_message=db_run.error_message,
                    started_at=db_run.started_at,
                    completed_at=db_run.completed_at,
                    created_at=db_run.created_at
                )
                pipeline_runs.append(pipeline_run)

            return pipeline_runs
        finally:
            await session.close()

    # Policy methods
    async def get_active_policies(self, country: str) -> list[dict]:
        """Get active policies for country."""
        session = await self.get_session()
        try:
            from sqlalchemy import and_, or_, select
            today = date.today()
            result = await session.execute(
                select(PolicyModel).filter(
                    and_(
                        PolicyModel.country == country,
                        PolicyModel.effective_from <= today,
                        or_(
                            PolicyModel.effective_to.is_(None),
                            PolicyModel.effective_to >= today
                        )
                    )
                )
            )
            db_policies = result.scalars().all()

            return [
                {
                    "id": policy.id,
                    "version": policy.version,
                    "country": policy.country,
                    "effective_from": policy.effective_from.isoformat(),
                    "effective_to": policy.effective_to.isoformat() if policy.effective_to else None,
                    "name": policy.name,
                    "description": policy.description,
                    "rules": policy.rules
                }
                for policy in db_policies
            ]
        finally:
            await session.close()

    async def get_policy(self, policy_id: str) -> dict | None:
        """Get policy by ID."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(PolicyModel).filter(PolicyModel.id == policy_id)
            )
            db_policy = result.scalar_one_or_none()

            if not db_policy:
                return None

            return {
                "id": db_policy.id,
                "version": db_policy.version,
                "country": db_policy.country,
                "effective_from": db_policy.effective_from.isoformat(),
                "effective_to": db_policy.effective_to.isoformat() if db_policy.effective_to else None,
                "name": db_policy.name,
                "description": db_policy.description,
                "rules": db_policy.rules
            }
        finally:
            await session.close()

    async def create_policy(self, policy_data: dict) -> dict:
        """Create a new policy."""
        session = await self.get_session()
        try:
            from datetime import date

            db_policy = PolicyModel(
                id=policy_data["id"],
                version=policy_data["version"],
                country=policy_data["country"],
                effective_from=date.fromisoformat(policy_data["effective_from"]),
                effective_to=date.fromisoformat(policy_data["effective_to"]) if policy_data.get("effective_to") else None,
                name=policy_data["name"],
                description=policy_data["description"],
                rules=policy_data["rules"]
            )
            session.add(db_policy)
            await session.commit()
            await session.refresh(db_policy)

            return {
                "id": db_policy.id,
                "version": db_policy.version,
                "country": db_policy.country,
                "effective_from": db_policy.effective_from.isoformat(),
                "effective_to": db_policy.effective_to.isoformat() if db_policy.effective_to else None,
                "name": db_policy.name,
                "description": db_policy.description,
                "rules": db_policy.rules
            }
        finally:
            await session.close()

    async def update_policy(self, policy_id: str, policy_data: dict) -> dict:
        """Update an existing policy."""
        session = await self.get_session()
        try:
            from datetime import date

            from sqlalchemy import select

            result = await session.execute(
                select(PolicyModel).filter(PolicyModel.id == policy_id)
            )
            db_policy = result.scalar_one_or_none()

            if not db_policy:
                raise ValueError(f"Policy {policy_id} not found")

            # Update fields
            if "version" in policy_data:
                db_policy.version = policy_data["version"]
            if "country" in policy_data:
                db_policy.country = policy_data["country"]
            if "effective_from" in policy_data:
                db_policy.effective_from = date.fromisoformat(policy_data["effective_from"])
            if "effective_to" in policy_data:
                db_policy.effective_to = date.fromisoformat(policy_data["effective_to"]) if policy_data["effective_to"] else None
            if "name" in policy_data:
                db_policy.name = policy_data["name"]
            if "description" in policy_data:
                db_policy.description = policy_data["description"]
            if "rules" in policy_data:
                db_policy.rules = policy_data["rules"]

            await session.commit()
            await session.refresh(db_policy)

            return {
                "id": db_policy.id,
                "version": db_policy.version,
                "country": db_policy.country,
                "effective_from": db_policy.effective_from.isoformat(),
                "effective_to": db_policy.effective_to.isoformat() if db_policy.effective_to else None,
                "name": db_policy.name,
                "description": db_policy.description,
                "rules": db_policy.rules
            }
        finally:
            await session.close()

    # BAS account methods
    async def save_bas_account(self, account: BASAccount, bas_version: str = "2025_v1.0") -> BASAccount:
        """Save BAS account to database."""
        session = await self.get_session()
        try:
            db_account = BASAccountModel(
                number=account.number,
                name=account.name,
                account_class=account.account_class,
                account_type=account.account_type,
                vat_hint=account.vat_hint,
                allowed_regions=account.allowed_regions,
                bas_version=bas_version,
                effective_from=date.today(),
                effective_to=None
            )
            session.add(db_account)
            await session.commit()
            return account
        finally:
            await session.close()

    async def get_bas_account(self, account_number: str) -> BASAccount | None:
        """Get BAS account by number."""
        session = await self.get_session()
        try:
            from sqlalchemy import select
            result = await session.execute(
                select(BASAccountModel).filter(BASAccountModel.number == account_number)
            )
            db_account = result.scalar_one_or_none()

            if not db_account:
                return None

            return BASAccount(
                number=db_account.number,
                name=db_account.name,
                account_class=db_account.account_class,
                account_type=db_account.account_type,
                vat_hint=float(db_account.vat_hint) if db_account.vat_hint else None,
                allowed_regions=db_account.allowed_regions or [],
                description=None
            )
        finally:
            await session.close()

    async def validate_bas_account(self, account_number: str, region: str = "SE") -> bool:
        """Validate BAS account exists and is allowed for region."""
        account = await self.get_bas_account(account_number)
        if not account:
            return False

        if account.allowed_regions and region not in account.allowed_regions:
            return False

        return True

    async def load_bas_accounts_from_dataset(self, accounts: list[BASAccount], bas_version: str = "2025_v1.0") -> None:
        """Load BAS accounts from dataset into database."""
        session = await self.get_session()
        try:
            for account in accounts:
                db_account = BASAccountModel(
                    number=account.number,
                    name=account.name,
                    account_class=account.account_class,
                    account_type=account.account_type,
                    vat_hint=account.vat_hint,
                    allowed_regions=account.allowed_regions,
                    bas_version=bas_version,
                    effective_from=date.today(),
                    effective_to=None
                )
                session.add(db_account)
            await session.commit()
        finally:
            await session.close()
