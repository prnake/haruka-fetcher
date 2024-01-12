---
title: Frequently Asked Questions
metaTitle: Frequently Asked Questions for PDF2HTML | PDFTron CLI
---

### Is PDF2HTML available as an SDK for integration with third party applications?

For developers who are looking for a software development component to integrate
into their applications, PDFTron offers a PDF to HTML conversion API.

For more details, please vist [www.pdftron.com](https://www.pdftron.com/) or
contact a [PDFTron representative](https://www.pdftron.com/company/contact-us/) for more information.

### Does PDF2HTML have any dependencies on third party components/software?

PDF2HTML is a completely stand-alone application and does not include any
dependencies on third-party components or software.

### How do I save converted files in a given folder?

To specify an output location, use the '-out' (or '-o') parameter with
an absolute file name. For example:

`pdf2html -in myIn.pdf -out "~/My Output/myOut.html"`

### How can I control the output name for converted files?

The output filename can be changed using the '-out' (or '-o')
option. For example, the following command-line generates an output
document named outdoc.html:

`pdf2html -in indoc.pdf -out outdoc.html`

### How do I specify which pages to convert?

By default, PDF2HTML will convert all PDF pages into an output HTML or HTM file.
You can specify a subset of pages to convert using the '-pages' option. For example:

`pdf2html -pages 2 -in in.pdf -out output.html`

will convert only page 2.

To specify a range of pages, use a dash character between numbers. For example:

`pdf2html -pages 1-3 -in in.pdf -out output.html`

will convert pages 1 to 3.

### How do I batch convert files?

PDF2HTML supports batch conversion of many PDF files in a single pass. For example,
to convert three PDFs, a.pdf, b.pdf and c.pdf, to a.htm, b.htm and c.htm, you could
use the following line:

`pdf2html -in a.pdf b.pdf c.pdf -out a.htm b.htm c.htm`

The number of input file names must match the number of output file names.

### How do I convert to HTM?

You can convert PDF to HTM by specifying the file extension as ".htm" in the
output file name. The following command-line would generate output as mydoc.htm:

`pdf2html -in mydoc.pdf -out mydoc.htm`

### How do I specify the Title of the HTML output?

PDF2HTML allows you to freely set the Title (&lt;TITLE&gt;) of the output HTML file.
Please make sure that you enclose the title text in double quotes. With the
'-title' option, the following command-line will set "My Title" as the Title of the output file:

`pdf2html -title "My Title" -in my.pdf -out my.html`

### How do I specify the resolution of the output images?

Output image resolution can be specified in dots per inch (dpi) using the '-resolution'
(or '-res') parameter option.

By default, PDF2HTML uses a resolution of 96 dpi. Smaller dpi numbers result in smaller
images while larger dpi numbers generate larger but higher quality images. For example,
to convert all images in a PDF at 200 dpi, use the following syntax:

`pdf2html -resolution 200 -in images.pdf -out images.html`

### How do I specify the output image type?

PDF2HTML can convert all images in a PDF to either JPEG or PNG format using the
'-compress' (or '-compression') parameter option. The default output image type is JPEG.
For example:

`pdf2html -compress jpeg -in in.pdf -out jpg.html`

will output images as JPEG.

Follow this example to convert images to PNG format:

`pdf2html -compress png -in in.pdf -out png.html`

### How do I convert a PDF with images into a self-contained HTML file?

PDF2HTML can convert a PDF with images into a self-contained HTML file by embedding the images.
The following command-line will embed all images and create a self-contained single.html output file:

`pdf2html -embedImages on -in images.pdf -out single.html`

### How do I convert a password protected PDF?

PDF2HTML will, without user intervention, convert documents secured with a master/owner password.

For unattended conversion, specify the master/owner password directly on the command-line
using the '-password' parameter option. The password provided must give unrestricted
content extraction permissions. For example, to convert a password protected secured.pdf
with the master password, 'secret', use the following syntax:

`pdf2html -password secret -in secured.pdf -out secured.html`
