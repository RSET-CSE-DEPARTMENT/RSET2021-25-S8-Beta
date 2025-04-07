from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import os
from glob import glob

def generate_report(patient_folder, output_path, patient, doctor):
    patient_folder = os.path.abspath(patient_folder)  # Convert to absolute path
    images_folder = os.path.join(patient_folder, "reportimages")  
    heatmaps_folder = os.path.join(patient_folder, "reportheat")  
    
    print(f"🔍 Searching Images Inside: {images_folder}")
    print(f"🔍 Searching Heatmaps Inside: {heatmaps_folder}")

    c = canvas.Canvas(output_path)

    def add_footer():
        """Adds the blue footer bar and date/time at the bottom of every page."""
        c.setFillColor(HexColor("#5e7dac"))
        c.roundRect(10, 5, 575, 15, 5, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.white)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawString(175, 8, f"Report generated on: {current_time}")

    def create_first_page():
        """Creates the cover page with patient and doctor details."""
        c.setFillColor(HexColor("#ffffff"))
        c.rect(0, 0, 600, 900, stroke=0, fill=1)

        # Header
        c.setFillColor(HexColor("#5e7dac"))
        c.roundRect(10, 5, 575, 15, 5, stroke=0, fill=1)
        c.roundRect(-30, 750, 5000000, 595, 200, stroke=0, fill=1)

        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.white)
        c.drawString(220, 785, "REPORT")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(430, 802, "FractureVision")
        c.drawString(440, 785, "Hospital")
        c.drawImage("H.jpg", 520, 769, height=50, width=50)

        # Patient details
        c.setFillColor(HexColor("#5e7dac"))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 700, "Patient Details:")
        c.setFillColor(colors.black)
        c.rect(50, 420, 500, 230, stroke=1, fill=0)

        c.setFont("Helvetica", 16)
        patient_details = [
            ("First Name:", patient.first_name),
            ("Last Name:", patient.last_name),
            ("Gender:", patient.gender),
            ("Date of Birth:", patient.dob.strftime('%Y-%m-%d')),
            ("Age:", patient.age),
            ("Diagnosis:", patient.diagnosis)
        ]

        y_position = 620
        for label, value in patient_details:
            c.drawString(60, y_position, label)
            c.drawString(200, y_position, str(value))
            y_position -= 30

        # Doctor details
        c.setFillColor(HexColor("#5e7dac"))
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 300, "Doctor Details:")
        c.setFillColor(colors.black)
        c.rect(50, 160, 500, 85, stroke=1, fill=0)

        c.setFont("Helvetica", 16)
        doctor_details = [
            ("Doctor ID:", doctor.doctor_id),
            ("Doctor Name:", doctor.doctor_name)
        ]

        y_position = 210
        for label, value in doctor_details:
            c.drawString(60, y_position, label)
            c.drawString(200, y_position, str(value))
            y_position -= 30

        add_footer()
        c.showPage()

    def top_bar():
        """Adds a top bar with the title."""
        c.setFillColor(HexColor("#5e7dac"))
        c.roundRect(10, 5, 575, 15, 5, stroke=0, fill=1)
        c.roundRect(-30, 750, 5000000, 595, 200, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(150, 795, "CT Scan Images & Heatmaps")
        c.setFont("Helvetica-Bold", 12)
        c.drawString(430, 802, "FractureVision")
        c.drawString(440, 785, "Hospital")
        c.drawImage("H.jpg", 520, 769, height=50, width=50)

    def add_images(image_list, heatmap_list):
        """Adds pairs of images from 'reportimage' and 'report heat' side by side."""
        images_per_page = 3  # 3 rows per page
        x_positions = [50, 320]  # Left column (CT Scan) and Right column (Heatmap)
        y_positions = [520, 280, 70]  # Three rows

        for i, (img_path, heatmap_path) in enumerate(zip(image_list, heatmap_list)):
            if i % images_per_page == 0:
                if i != 0:
                    top_bar()
                    add_footer()
                    c.showPage()  # Start a new page

            row = i % images_per_page
            try:
                # Left column - Original CT scan
                c.drawImage(img_path, x_positions[0], y_positions[row], width=240, height=200)
                # Right column - Heatmap
                c.drawImage(heatmap_path, x_positions[1], y_positions[row], width=240, height=200)

                print(f"Added Image Pair: {img_path} | {heatmap_path}")
            except Exception as e:
                print(f"Error adding images {img_path} and {heatmap_path}: {e}")

        add_footer()

    # Generate first page
    create_first_page()

    # Fetch images
    image_files = sorted(glob(os.path.join(images_folder, "*.jpg")) + 
                         glob(os.path.join(images_folder, "*.jpeg")) + 
                         glob(os.path.join(images_folder, "*.png")))

    heatmap_files = sorted(glob(os.path.join(heatmaps_folder, "*.jpg")) + 
                           glob(os.path.join(heatmaps_folder, "*.jpeg")) + 
                           glob(os.path.join(heatmaps_folder, "*.png")))

    # Ensure matching number of images
    min_length = min(len(image_files), len(heatmap_files))
    image_files = image_files[:min_length]
    heatmap_files = heatmap_files[:min_length]

    # Debugging: Print matched image pairs
    print(f"Matched Image Pairs Found: {list(zip(image_files, heatmap_files))}")

    if image_files and heatmap_files:
        add_images(image_files, heatmap_files)
    else:
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.red)
        c.drawString(50, 700, "No images available in 'reportimage' or 'report heat'.")
        add_footer()
        print("No images found in 'reportimage' or 'report heat' folders.")

    # Save the final PDF
    # Ensure the output directory exists before saving
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        c.save()
        print(f"Report saved successfully: {output_path}")
    except PermissionError as e:
        print(f"Permission Error: {e}")
        print("Try running the script as Administrator or changing file permissions.")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    print("Ensure the directory exists and the path is correct.")

