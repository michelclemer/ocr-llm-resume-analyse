"""
Implementação do serviço de extração de texto usando Tesseract e PyPDF2
"""

import os
import mimetypes
from typing import Optional
from PIL import Image
import pytesseract
import PyPDF2
from io import BytesIO

from ...application.interfaces.services import ITextExtractionService
from ...domain.value_objects.curriculum_values import FileType


class TesseractTextExtractor(ITextExtractionService):
    """
    Implementação de extração de texto usando Tesseract OCR e PyPDF2
    """
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Inicializa o extrator de texto
        
        Args:
            tesseract_path: Caminho para o executável do Tesseract (opcional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        self.supported_image_types = {
            FileType.JPEG, FileType.JPG, FileType.PNG, 
            FileType.BMP, FileType.TIFF, FileType.GIF, FileType.WEBP
        }
        self.supported_pdf_types = {FileType.PDF}
    
    def extract_from_bytes(self, content: bytes, file_type: FileType) -> str:
        """
        Extrai texto de bytes de arquivo
        
        Args:
            content: Conteúdo do arquivo em bytes
            file_type: Tipo do arquivo
            
        Returns:
            Texto extraído do arquivo
            
        Raises:
            ValueError: Se o tipo não é suportado
            Exception: Se houver erro na extração
        """
        if not self.is_supported_type(file_type):
            raise ValueError(f"Tipo de arquivo não suportado: {file_type.value}")
        
        try:
            if file_type in self.supported_image_types:
                return self._extract_from_image_bytes(content)
            elif file_type in self.supported_pdf_types:
                return self._extract_from_pdf_bytes(content)
            else:
                raise ValueError(f"Tipo não implementado: {file_type.value}")
                
        except Exception as e:
            raise Exception(f"Erro na extração de texto: {str(e)}")
    
    def is_supported_type(self, file_type: FileType) -> bool:
        """
        Verifica se o tipo de arquivo é suportado
        
        Args:
            file_type: Tipo do arquivo
            
        Returns:
            True se suportado, False caso contrário
        """
        return file_type in (self.supported_image_types | self.supported_pdf_types)
    
    def _extract_from_image_bytes(self, content: bytes, lang: str = 'por') -> str:
        """
        Extrai texto de bytes de imagem usando OCR
        
        Args:
            content: Bytes da imagem
            lang: Idioma para OCR
            
        Returns:
            Texto extraído
        """
        try:
            # Abrir imagem dos bytes
            image = Image.open(BytesIO(content))
            
            # Aplicar OCR
            text = pytesseract.image_to_string(image, lang=lang)
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Erro no OCR da imagem: {str(e)}")
    
    def _extract_from_pdf_bytes(self, content: bytes) -> str:
        """
        Extrai texto de bytes de PDF
        
        Args:
            content: Bytes do PDF
            
        Returns:
            Texto extraído
        """
        try:
            # Ler PDF dos bytes
            pdf_reader = PyPDF2.PdfReader(BytesIO(content))
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise Exception(f"Erro na extração de PDF: {str(e)}")
    
    def get_supported_types(self) -> dict:
        """
        Retorna os tipos de arquivo suportados
        
        Returns:
            Dicionário com tipos suportados
        """
        return {
            'images': [ft.value for ft in self.supported_image_types],
            'documents': [ft.value for ft in self.supported_pdf_types],
            'all': [ft.value for ft in (self.supported_image_types | self.supported_pdf_types)]
        }