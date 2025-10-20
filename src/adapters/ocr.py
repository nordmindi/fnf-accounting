"""OCR adapter for document text extraction."""

import io
import re
from datetime import date
from decimal import Decimal
from typing import Any

import pytesseract
from PIL import Image


class OCRAdapter:
    """OCR adapter using Tesseract."""

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.tesseract_config = config.get("tesseract", {})

    async def extract_receipt(self, file_content: bytes, content_type: str) -> dict[str, Any]:
        """Extract receipt data from document."""
        if content_type.startswith("text/"):
            # Handle text files directly
            raw_text = file_content.decode('utf-8')
        else:
            # Convert to image and extract text using OCR
            image = self._convert_to_image(file_content, content_type)
            raw_text = pytesseract.image_to_string(
                image,
                config=self._get_tesseract_config()
            )

        # Parse structured data from text
        parsed_data = self._parse_receipt_text(raw_text)

        return {
            "total": parsed_data["total"],
            "currency": parsed_data["currency"],
            "vat_lines": parsed_data["vat_lines"],
            "vendor": parsed_data.get("vendor"),
            "date": parsed_data["date"],
            "raw_text": raw_text,
            "confidence": parsed_data["confidence"]
        }

    def _convert_to_image(self, file_content: bytes, content_type: str) -> Image.Image:
        """Convert file content to PIL Image."""
        if content_type.startswith("image/"):
            return Image.open(io.BytesIO(file_content))
        elif content_type.startswith("text/"):
            # For text files, we'll handle them differently in extract_receipt
            raise ValueError("Text files should be handled directly, not converted to image")
        else:
            # For PDFs, we would need additional libraries like pdf2image
            # For now, assume it's an image
            return Image.open(io.BytesIO(file_content))

    def _get_tesseract_config(self) -> str:
        """Get Tesseract configuration string."""
        config_parts = []

        if self.tesseract_config.get("language"):
            config_parts.append(f"-l {self.tesseract_config['language']}")

        if self.tesseract_config.get("psm"):
            config_parts.append(f"--psm {self.tesseract_config['psm']}")

        return " ".join(config_parts)

    def _parse_receipt_text(self, text: str) -> dict[str, Any]:
        """Parse receipt text to extract structured data."""
        # This is a simplified parser - in production, you'd want more sophisticated parsing

        # Extract total amount
        total = self._extract_total(text)

        # Extract currency
        currency = self._extract_currency(text)

        # Extract VAT lines
        vat_lines = self._extract_vat_lines(text, total)

        # Extract vendor
        vendor = self._extract_vendor(text)

        # Extract date
        receipt_date = self._extract_date(text)

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(text, total, vendor, receipt_date)

        return {
            "total": total,
            "currency": currency,
            "vat_lines": vat_lines,
            "vendor": vendor,
            "date": receipt_date,
            "confidence": confidence
        }

    def _extract_total(self, text: str) -> Decimal:
        """Extract total amount from text."""
        # Look for patterns like "Total: 123.45", "Summa: 123,45", etc.
        patterns = [
            r"(?i)total[:\s]+([0-9,.\s]+)",
            r"(?i)summa[:\s]+([0-9,.\s]+)",
            r"(?i)att betala[:\s]+([0-9,.\s]+)",
            r"(?i)amount[:\s]+([0-9,.\s]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(",", ".").replace(" ", "")
                try:
                    return Decimal(amount_str)
                except:
                    continue

        # Fallback: look for the largest number that could be a total
        numbers = re.findall(r'[0-9]+[.,]?[0-9]*', text)
        if numbers:
            # Convert and find the largest reasonable amount
            amounts = []
            for num in numbers:
                try:
                    amount = Decimal(num.replace(",", "."))
                    if 1 <= amount <= 100000:  # Reasonable range for receipts
                        amounts.append(amount)
                except:
                    continue

            if amounts:
                return max(amounts)

        return Decimal("0")

    def _extract_currency(self, text: str) -> str:
        """Extract currency from text."""
        # Look for currency symbols or codes
        currency_patterns = [
            r"SEK|kr|:-",
            r"EUR|€|euro",
            r"USD|\$|dollar",
            r"NOK|nkr",
            r"DKK|dkk"
        ]

        for pattern in currency_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                if "SEK" in pattern or "kr" in pattern or ":-" in pattern:
                    return "SEK"
                elif "EUR" in pattern or "€" in pattern:
                    return "EUR"
                elif "USD" in pattern or "$" in pattern:
                    return "USD"
                elif "NOK" in pattern:
                    return "NOK"
                elif "DKK" in pattern:
                    return "DKK"

        return "SEK"  # Default to SEK for Swedish receipts

    def _extract_vat_lines(self, text: str, total: Decimal) -> list[dict[str, Any]]:
        """Extract VAT lines from text."""
        vat_lines = []

        # Look for VAT patterns
        vat_patterns = [
            r"(?i)moms?\s+(\d+)%?\s*:?\s*([0-9,.\s]+)",
            r"(?i)vat\s+(\d+)%?\s*:?\s*([0-9,.\s]+)",
        ]

        for pattern in vat_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    rate = int(match.group(1))
                    amount_str = match.group(2).replace(",", ".").replace(" ", "")
                    amount = Decimal(amount_str)

                    # Calculate base amount
                    base_amount = amount / (rate / 100)

                    vat_lines.append({
                        "rate": Decimal(str(rate)),
                        "amount": amount,
                        "base_amount": base_amount
                    })
                except:
                    continue

        # If no VAT lines found, try to infer from total
        if not vat_lines and total > 0:
            # Common Swedish VAT rates
            for rate in [25, 12, 6]:
                vat_amount = total * Decimal(str(rate)) / (100 + rate)
                base_amount = total - vat_amount

                if vat_amount > 0:
                    vat_lines.append({
                        "rate": Decimal(str(rate)),
                        "amount": vat_amount,
                        "base_amount": base_amount
                    })
                    break

        return vat_lines

    def _extract_vendor(self, text: str) -> str:
        """Extract vendor name from text."""
        lines = text.split('\n')

        # Usually the vendor name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if line and len(line) > 2 and not re.match(r'^[0-9\s,.-]+$', line):
                # Skip lines that are just numbers/punctuation
                return line

        return None

    def _extract_date(self, text: str) -> date:
        """Extract date from text."""
        # Look for date patterns
        date_patterns = [
            r"(\d{4})-(\d{2})-(\d{2})",  # YYYY-MM-DD
            r"(\d{2})/(\d{2})/(\d{4})",  # MM/DD/YYYY
            r"(\d{2})\.(\d{2})\.(\d{4})",  # DD.MM.YYYY
            r"(\d{2})-(\d{2})-(\d{4})",  # DD-MM-YYYY
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if pattern.startswith(r"(\d{4})"):  # YYYY-MM-DD
                        year, month, day = match.groups()
                    else:  # DD/MM/YYYY or similar
                        day, month, year = match.groups()

                    return date(int(year), int(month), int(day))
                except:
                    continue

        # Fallback to today's date
        return date.today()

    def _calculate_confidence(self, text: str, total: Decimal, vendor: str, receipt_date: date) -> float:
        """Calculate confidence score based on extracted data quality."""
        confidence = 0.0

        # Text length (more text usually means better OCR)
        if len(text) > 50:
            confidence += 0.2
        elif len(text) > 20:
            confidence += 0.1

        # Total amount found
        if total > 0:
            confidence += 0.3

        # Vendor found
        if vendor:
            confidence += 0.2

        # Date found and reasonable
        if receipt_date and receipt_date.year >= 2020:
            confidence += 0.2

        # Check for common receipt keywords
        receipt_keywords = ["kvitto", "receipt", "total", "summa", "moms", "vat"]
        if any(keyword in text.lower() for keyword in receipt_keywords):
            confidence += 0.1

        return min(confidence, 1.0)
