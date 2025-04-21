# Documentation Technique - PfeProject avec ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

# Création du document
pdf_path = "Documentation_PfeProject_BahaEddine.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter)

# Styles
styles = getSampleStyleSheet()
# Création de nouveaux styles avec des noms uniques
styles.add(ParagraphStyle(name='MyTitle', fontSize=20, alignment=1, textColor=colors.HexColor("#0066CC")))
styles.add(ParagraphStyle(name='MySubTitle', fontSize=16, alignment=1))
styles.add(ParagraphStyle(name='MyChapterTitle', fontSize=14, textColor=colors.HexColor("#004682")))
styles.add(ParagraphStyle(name='MyCode', fontName='Courier', fontSize=11,
                         backColor=colors.HexColor("#E6E6E6"),
                         borderWidth=1, borderColor=colors.black,
                         leading=14, leftIndent=10))

# Contenu du document
story = []

# Page de garde
story.append(Paragraph("Documentation Technique", styles['MyTitle']))
story.append(Spacer(1, 20))
story.append(Paragraph("Projet : PfeProject", styles['MySubTitle']))
story.append(Spacer(1, 10))
story.append(Paragraph("Auteur : Baha Eddine Somrani", styles['MySubTitle']))
story.append(Spacer(1, 60))

# Introduction
story.append(Paragraph("Introduction", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
intro_text = """Ce document décrit les étapes nécessaires pour installer et exécuter le projet PfeProject, un système d'automatisation de tests Android Automotive via Appium et Robot Framework."""
story.append(Paragraph(intro_text, styles['Normal']))
story.append(Spacer(1, 15))

# Pré-requis
story.append(Paragraph("Pré-requis", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
prereq_text = """- Android Studio avec SDK API 34 et 35<br/>
- AVD Manager configuré<br/>
- Docker & Docker Compose<br/>
- Git installé"""
story.append(Paragraph(prereq_text, styles['Normal']))
story.append(Spacer(1, 15))

# Cloner projet
story.append(Paragraph("1. Cloner le projet", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
story.append(Paragraph("git clone https://github.com/bahaeddine20/PfeProject.git<br/>cd PfeProject", styles['MyCode']))
story.append(Spacer(1, 15))

# Emulateurs
story.append(Paragraph("2. Lancer les deux émulateurs", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
story.append(Paragraph("Depuis Android Studio ou en ligne de commande :", styles['Normal']))
story.append(Spacer(1, 5))
story.append(Paragraph("emulator -avd automotive_api_34<br/>emulator -avd phone_api_35", styles['MyCode']))
story.append(Spacer(1, 5))
emulators_text = """Assurez-vous que les AVD sont configurés avec :<br/>
- Automotive (1408p landscape) avec Google Play – API 34-ext9<br/>
- Medium Phone – API 35"""
story.append(Paragraph(emulators_text, styles['Normal']))
story.append(Spacer(1, 15))

# Docker Compose
story.append(Paragraph("3. Accéder au dossier pfeDockerpull et exécuter docker-compose", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
story.append(Paragraph("cd PfeProject/pfeDockerpull<br/>docker-compose up ", styles['MyCode']))
story.append(Spacer(1, 5))
docker_text = """Cela lance l'environnement de test avec Appium et les services nécessaires."""
story.append(Paragraph(docker_text, styles['Normal']))
story.append(Spacer(1, 15))

# Conclusion
story.append(Paragraph("Conclusion", styles['MyChapterTitle']))
story.append(Spacer(1, 5))
conclusion_text = """Votre environnement est maintenant prêt pour exécuter les scénarios automatisés sur les émulateurs Android.<br/>
Pour plus de détails, référez-vous aux fichiers README.md et aux scripts dans le dépôt."""
story.append(Paragraph(conclusion_text, styles['Normal']))

# Génération du PDF
doc.build(story)
print(f"PDF généré avec succès : {pdf_path}")