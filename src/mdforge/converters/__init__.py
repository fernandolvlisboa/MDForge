from .docx import DocxConverter
from .html import HtmlConverter
from .pdf import PdfConverter
from .pptx import PptxConverter
from .text import TextConverter
from .xlsx import XlsxConverter

BUILTIN_CONVERTERS = [
    DocxConverter(),
    HtmlConverter(),
    PdfConverter(),
    PptxConverter(),
    TextConverter(),
    XlsxConverter(),
]
