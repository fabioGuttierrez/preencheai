from sqlalchemy import Column, Integer, String, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Company(Base):
	__tablename__ = "companies"
	id = Column(Integer, primary_key=True, index=True)
	nome = Column(String, nullable=False)
	email_envio = Column(String, nullable=False)
	smtp_config = Column(JSON, nullable=True)
	plano = Column(String, nullable=True)
	ativo = Column(Boolean, default=True)

	clients = relationship("Client", back_populates="company")
	templates = relationship("ContractTemplate", back_populates="company")
	contracts = relationship("Contract", back_populates="company")
