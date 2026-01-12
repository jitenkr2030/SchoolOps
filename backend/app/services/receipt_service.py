"""
Receipt Generation Service

Generates PDF payment receipts using ReportLab.
ReportLab is open-source and free for commercial use.

Features:
- Professional receipt layout
- School branding support
- Automatic receipt number generation
- Configurable templates
"""

import os
from io import BytesIO
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus.flowables import HRFlowable


class ReceiptGenerator:
    """
    PDF Receipt Generator using ReportLab.
    
    Generates professional payment receipts with:
    - School header and branding
    - Payment details
    - Student information
    - Transaction summary
    """
    
    def __init__(self, school_name: str = "SchoolOps", school_address: str = ""):
        """
        Initialize receipt generator.
        
        Args:
            school_name: Name to display on receipts
            school_address: School address for receipt header
        """
        self.school_name = school_name
        self.school_address = school_address
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for receipts"""
        self.styles.add(ParagraphStyle(
            name="ReceiptTitle",
            parent=self.styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a365d"),
            alignment=1,  # Center
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name="ReceiptHeader",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2d3748"),
            spaceBefore=10,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name="ReceiptBody",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name="ReceiptLabel",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#4a5568"),
        ))
        
        self.styles.add(ParagraphStyle(
            name="ReceiptValue",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=colors.black,
        ))
    
    def generate_receipt(
        self,
        receipt_number: str,
        payment_date: datetime,
        student_name: str,
        admission_number: str,
        class_name: str,
        fee_name: str,
        amount_paid: Decimal,
        payment_method: str,
        transaction_reference: Optional[str] = None,
        total_paid: Optional[Decimal] = None,
        balance_due: Optional[Decimal] = None,
        school_logo_path: Optional[str] = None
    ) -> BytesIO:
        """
        Generate a PDF receipt.
        
        Args:
            receipt_number: Unique receipt identifier
            payment_date: Date of payment
            student_name: Student full name
            admission_number: Student admission number
            class_name: Current class/grade
            fee_name: Name of fee being paid
            amount_paid: Amount paid in this transaction
            payment_method: Payment method used
            transaction_reference: Bank/transaction reference if applicable
            total_paid: Total paid to date (for fee)
            balance_due: Remaining balance
            school_logo_path: Path to school logo image
            
        Returns:
            BytesIO buffer containing PDF data
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # Build receipt content
        story = []
        
        # School Header
        if school_logo_path and os.path.exists(school_logo_path):
            from reportlab.lib.utils import ImageReader
            logo = ImageReader(school_logo_path)
            aspect = logo.getSize()[0] / logo.getSize()[1]
            logo_table = Table([[Paragraph(f"<img src='{school_logo_path}' width='{50*mm}' height='{50*mm/aspect}'/>")]], colWidths=[100*mm])
            logo_table.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
            story.append(logo_table)
            story.append(Spacer(1, 10))
        
        story.append(Paragraph(self.school_name, self.styles["ReceiptTitle"]))
        if self.school_address:
            story.append(Paragraph(self.school_address, self.styles["ReceiptBody"]))
        
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a365d")))
        story.append(Spacer(1, 15))
        
        # Receipt Title
        story.append(Paragraph("PAYMENT RECEIPT", self.styles["ReceiptTitle"]))
        story.append(Spacer(1, 10))
        
        # Receipt Info Table
        receipt_info = [
            ["Receipt No.:", receipt_number, "Date:", payment_date.strftime("%d-%m-%Y %H:%M")],
            ["Admission No.:", admission_number, "Class:", class_name],
        ]
        
        info_table = Table(receipt_info, colWidths=[40*mm, 50*mm, 30*mm, 50*mm])
        info_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
            ("FONTNAME", (3, 0), (3, -1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4a5568")),
            ("TEXTCOLOR", (2, 0), (2, -1), colors.HexColor("#4a5568")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Student Name
        story.append(Paragraph("Student Name:", self.styles["ReceiptLabel"]))
        story.append(Paragraph(student_name, self.styles["ReceiptValue"]))
        story.append(Spacer(1, 10))
        
        # Payment Details Header
        story.append(Paragraph("PAYMENT DETAILS", self.styles["ReceiptHeader"]))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 10))
        
        # Fee Details
        fee_details = [
            ["Particulars", "Amount (₹)"],
            [fee_name, f"₹{float(amount_paid):.2f}"],
        ]
        
        if total_paid is not None and balance_due is not None:
            fee_details.extend([
                ["Total Paid (to date)", f"₹{float(total_paid):.2f}"],
                ["Balance Due", f"₹{float(balance_due):.2f}"],
            ])
        
        fee_table = Table(fee_details, colWidths=[80*mm, 40*mm])
        fee_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7fafc")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#4a5568")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ]))
        story.append(fee_table)
        story.append(Spacer(1, 15))
        
        # Total Amount
        total_table = Table([["TOTAL PAID", f"₹{float(amount_paid):.2f}"]], colWidths=[100*mm, 40*mm])
        total_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1a365d")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 12),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 15))
        
        # Payment Method
        payment_info = [
            ["Payment Method:", payment_method],
        ]
        if transaction_reference:
            payment_info.append(["Reference No.:", transaction_reference])
        
        payment_table = Table(payment_info, colWidths=[50*mm, 80*mm])
        payment_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4a5568")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 30))
        
        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 10))
        
        story.append(Paragraph("This is a computer-generated receipt.", self.styles["ReceiptBody"]))
        story.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", self.styles["ReceiptBody"]))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_receipt_from_data(self, data: Dict[str, Any]) -> BytesIO:
        """
        Generate receipt from dictionary data.
        
        Args:
            data: Dictionary containing receipt fields
            
        Returns:
            BytesIO buffer with PDF
        """
        return self.generate_receipt(
            receipt_number=data["receipt_number"],
            payment_date=data["payment_date"],
            student_name=data["student_name"],
            admission_number=data["admission_number"],
            class_name=data["class_name"],
            fee_name=data["fee_name"],
            amount_paid=data["amount_paid"],
            payment_method=data["payment_method"],
            transaction_reference=data.get("transaction_reference"),
            total_paid=data.get("total_paid"),
            balance_due=data.get("balance_due"),
            school_logo_path=data.get("school_logo_path")
        )


# Singleton instance
receipt_generator = ReceiptGenerator()


def generate_receipt_bytesio(**kwargs) -> BytesIO:
    """Helper function to generate receipt"""
    return receipt_generator.generate_receipt(**kwargs)
