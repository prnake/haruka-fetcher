---
title: Command-Line Summary for PDF2HTML
metaTitle: Command-line Summary for PDF to HTML | PDFTron CLI
---

```
Usage: pdf2html [options] -in inputfile -out outputfile

BASIC PARAMETERS:

  -in [ -i ] arg            The input file. The default input folder is the
                            current working folder. When running the
                            application from the console or an .sh file, you may
                            use relative file names. However, if you are
                            calling it from an application or a server, we
                            recommend using absolute file names for robustness.

  -out [ -o ] arg           The output file. When running the application from the
                            console or an .sh file, you may use relative file
                            names. However, if you are calling it from an
                            application or a server, we recommend using
                            absolute file names for robustness.

OPTIONS:

  -pages arg (=all)         Page numbers of pages to be converted. You may
                            specify a single page number, e.g. 2, or a range of
                            pages, e.g. 2-6. If omitted, all pages will be
                            converted.

  -fileTimeout arg (=300)   The maximum amount of time allowed, in seconds,
                            for each document conversion. The default timeout
                            is 300 seconds (5 minutes).

  -password arg             The master password to open the PDF. The password
                            must give unrestricted content extraction
                            permissions.

  -quality arg (=85)        The image compression quality for JPEG,
                            from 5 to 100. Quality is ignored for PNG images.
                            The default quality is 85.

  -compress                 The output image type, either JPEG ("jpeg") or
   [ -compression ]         PNG ("png"). The default is "jpeg".
   arg (=jpeg)

  -resolution [ -res ]      The resolution for the output images in dots per
   arg (=96)                inch, from 8 to 600.
                            The default resolution is 96 dpi.

  -embedImages arg          Flag to embed images inside the HTML output using
                            Base64 encoding ("on") or written out as external
                            JPEG/PNG files ("off"). Embedding images will
                            produce a larger output file, but the HTML file is
                            self-contained. When external image files are used,
                            you must keep them together with the HTML file.
                            External images are always placed in a separate
                            directory. If you move or delete your HTML file,
                            you should also move or delete your images folder
                            with it. Valid parameter values are "on" and "off".
                            By default, this option is turned "on" if specified
                            without an argument. However, if this option is
                            completely omitted, it defaults to "off".

  -title arg                The content that goes inside the HTML output's
                            <TITLE> tag. Please ensure that you use double
                            quotes when specifying your title,
                            e.g. -title "PDF converted to HTML". If this option
                            is not specified, the default title is
                            "Created by PDFTron".

  -ocred arg (=image+text)  Handling of special OCRed PDFs that only contain
                            full-page images with hidden selectable text. This
                            option is only applicable to a PDF produced by an
                            OCR engine based on a scanned image. Valid
                            parameter values are "image+text", "text", "image"
                            and "image+hiddenText". The default option,
                            "image+text", converts both images and text, making
                            the hidden text visible in the output. Use "text"
                            to convert only the text to make the hidden text
                            visible in the output or "image" to convert only
                            the images. If you want to convert the background
                            image and create a hidden selectable text layer
                            around it using complex JavaScript, use
                            "image+hiddenText".

  -simpleLists arg          Flag to use <P> tags ("off") or <LI> tags ("on")
                            for list items. Turning this flag "on" outputs
                            lists using <LI> tags and will give you the richest
                            logical content but with limited physical
                            formatting capabilities. For best visual accuracy,
                            turn this flag "off". Valid parameter values are
                            "on" and "off". By default, this option is turned
                            "on" if specified without an argument. However,
                            if this option is completely omitted, it defaults
                            to "off".

  -connectHyphens arg       Flag to re-connect basic English dictionary words
                            that are hyphenated at the end of a line. This
                            does not remove hyphens from expressions that
                            require a hyphen, such as "counter-clockwise" or
                            "well-intentioned". Valid parameter values are "on"
                            and "off". By default, this option is turned "on"
                            if specified without an argument. However, if this
                            option is completely omitted, it defaults to "off".

  -symbolToUnicode arg      Flag to translate Symbol font to Times New Roman
                            Unicode. It is not recommended to use Symbol font
                            in HTML files. We strongly recommend that you leave
                            this turned "on" unless your HTML is viewed using
                            Internet Explorer on Windows only. Turning this
                            "off" may produce HTML that looks corrupt on macOS,
                            iOS, Android and Linux. Valid parameter values are
                            "on" and "off". By default, this option is turned
                            "on" if specified without an argument. It also
                            defaults to "on" if this option is completely
                            omitted.

  -advanced [ -a ] arg      Advanced option to ignore angled text
                            (IgnoreAngledText=True) and/or vertical text
                            (IgnoreVerticalText=True).
                            By default, these are turned off.

  -silent                   Switches the application to Silent Mode. Warnings
                            and progress messages are not displayed. Only
                            errors that are considered failures are shown.



Examples:
  pdf2html -in myInput.pdf -out myOutput.html
  pdf2html -password MyPDFPassword -in my.pdf -out myHTM.htm
```
