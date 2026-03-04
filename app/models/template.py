from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from app.db.base import Base

class ContractTemplate(Base):
	__tablename__ = "contract_templates"
	id = Column(Integer, primary_key=True, index=True)
	company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
	nome = Column(String, nullable=False)
	tipo = Column(String, nullable=True)
	html_template = Column(Text, nullable=False)
	ativo = Column(Boolean, default=True)

	company = relationship("Company", back_populates="templates")
	contracts = relationship("Contract", back_populates="template")
