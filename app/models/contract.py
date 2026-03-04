from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base
import datetime

class Contract(Base):
	__tablename__ = "contracts"
	id = Column(Integer, primary_key=True, index=True)
	company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
	client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
	template_id = Column(Integer, ForeignKey("contract_templates.id"), nullable=False)
	status = Column(String, default="pending")
	form_data = Column(JSON, nullable=True)
	pdf_path = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.datetime.utcnow)

	company = relationship("Company", back_populates="contracts")
	client = relationship("Client", back_populates="contracts")
	template = relationship("ContractTemplate", back_populates="contracts")
	tokens = relationship("FormToken", back_populates="contract")
