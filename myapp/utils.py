from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_booking_pdf(order):

    booking = order.booking_details
    items = order.items.all()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    content = []

    # Title
    content.append(
        Paragraph(
            "VEHICLE RENTAL BOOKING CONFIRMATION",
            title_style
        )
    )

    content.append(Spacer(1, 10))

    # Order information
    order_data = [
        ["Order Number", order.order_number],
        ["Order Status", order.get_order_status_display()],
        ["Payment Status", order.get_payment_status_display()],
        ["Order Date", order.created_at.strftime("%d-%m-%Y %H:%M")],
    ]

    order_table = Table(
        order_data,
        colWidths=[45 * mm, 110 * mm]
    )

    order_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    content.append(order_table)
    content.append(Spacer(1, 15))

    # Customer details
    content.append(
        Paragraph("Customer Details", heading_style)
    )

    customer_data = [
        ["Full Name", booking.full_name],
        ["Email", booking.email],
        ["Phone", booking.phone_number],
        ["Date of Birth", booking.dob.strftime("%d-%m-%Y")],
        ["Location", booking.location],
        ["Address", booking.address],
    ]

    customer_table = Table(
        customer_data,
        colWidths=[45 * mm, 110 * mm]
    )

    customer_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    content.append(customer_table)
    content.append(Spacer(1, 15))

    # Rental details
    content.append(
        Paragraph("Rental Details", heading_style)
    )

    rental_data = [
        ["Rental Start", booking.rental_start.strftime("%d-%m-%Y %H:%M")],
        ["Rental End", booking.rental_end.strftime("%d-%m-%Y %H:%M")],
    ]

    rental_table = Table(
        rental_data,
        colWidths=[45 * mm, 110 * mm]
    )

    rental_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    content.append(rental_table)
    content.append(Spacer(1, 15))

    # Vehicle details
    content.append(
        Paragraph("Vehicle Details", heading_style)
    )

    vehicle_data = [
        [
            "Vehicle",
            "Plan",
            "Hours",
            "Qty",
            "Price",
            "Subtotal",
        ]
    ]

    for item in items:
        vehicle_data.append([
            item.vehicle_name,
            item.get_plan_display()
            if hasattr(item, "get_plan_display")
            else item.plan,
            str(item.hours),
            str(item.quantity),
            f"₹{item.price}",
            f"₹{item.subtotal}",
        ])

    vehicle_table = Table(
        vehicle_data,
        colWidths=[
            35 * mm,
            25 * mm,
            20 * mm,
            15 * mm,
            25 * mm,
            30 * mm,
        ]
    )

    vehicle_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ])
    )

    content.append(vehicle_table)
    content.append(Spacer(1, 15))

    # Total
    total_data = [
        ["Total Amount", f"₹{order.total_amount}"]
    ]

    total_table = Table(
        total_data,
        colWidths=[100 * mm, 55 * mm]
    )

    total_table.setStyle(
        TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ])
    )

    content.append(total_table)
    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            "Thank you for choosing our vehicle rental service.",
            normal_style
        )
    )

    document.build(content)

    buffer.seek(0)

    return buffer