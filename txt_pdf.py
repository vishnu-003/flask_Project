# #Importing the FPDF library.
# from fpdf import FPDF
# pdf = FPDF()  
# pdf.add_page() 
# pdf.set_font("Arial", size = 15) 
# pdf.cell(200, 10, txt = "Python Pool",  
#          ln = 1, align = 'C') 
  
# # add another cell 
# pdf.cell(200, 10, txt = "Start your Python Learning journey now with Python Pool", 
#          ln = 2, align = 'C') 

# pdf.output("PP.pdf")
# Python program to convert text file to PDF using FPDF


from fpdf import FPDF 
 
pdf = FPDF() 
pdf.add_page() 
pdf.set_font("Arial", size = 15) 
f = open("input.txt", "r") 
for x in f: 
	pdf.cell(200, 10, txt = x, ln = 1, align = 'C')

pdf.output("gamer.pdf") 