from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Client(Base):
	__tablename__ = "clients"
	id = Column(Integer, primary_key=True, index=True)
	company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
	nome = Column(String, nullable=False)
	email = Column(String, nullable=False)
	telefone = Column(String, nullable=True)

	company = relationship("Company", back_populates="clients")
	contracts = relationship("Contract", back_populates="client")
