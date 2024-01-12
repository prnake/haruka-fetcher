---
title: Examples of converting PDF to HTML using command-line
metaTitle: PDF to HTML Command-line Conversion Examples | PDFTron CLI
---

PDFTron's PDF2HTML is a command-line application designed to convert PDF documents
to HTML files while preserving the contents of the PDF. This section covers the
basic usage of PDF2HTML, explaining all of the available options.

Basic Syntax
----------------

The basic command-line syntax is:

`pdf2html [options] -in inputfile -out outputfile`

The '-in' parameter can be abbreviated as '-i', and the '-out' parameter
can be abbreviated as '-o'.

If you are calling PDF2HTML from the console or an .sh file, you may use relative file names.
However, if you are calling it from an application or a server, you should be using
absolute file names.

See more options in [Command-Line Summary](https://www.pdftron.com/documentation/cli/guides/pdf2html/cmd-options/) for PDF2HTML.

General Usage Examples
--------------------------

### **Example 1. The simplest command line: Convert PDF to HTML.**

Note:

Notes:

-   The '-in' (or '-i') parameter is used to specify the input file.
    You can use relative and/or absolute file name.

-   The '-out' (or '-o') parameter is used to specify the output file.
    You can use relative and/or absolute file name.

`pdf2html -in my.pdf -out my.html`

### **Example 2. Convert PDF to HTM.**

Note:

-   Use ".htm" as the file extension when specifying the output file name.

`pdf2html -in my.pdf -out outHTM.htm`

### **Example 3. Convert a password-protected PDF.**

Notes:

-   The '-password' parameter is used to specify the master password required to open
    the protected document.
-   The password provided must give unrestricted content extraction permissions.

`pdf2html -password MyPDFPassword -in my.pdf -out myOut.html`

### **Example 4. Convert specific pages in PDF.**

Notes:

-   The '-pages' parameter is used to specify which page(s) to convert.
-   You can specify a single page, e.g. '-pages 1' or a range of pages, e.g. '-pages 1-2'.

`pdf2html -pages 1-2 -in my.pdf -out my.html`

### **Example 5. Batch convert PDF files.**

Notes:

-   The '-in' (or '-i') parameter supports multiple input file names.
    Separate each input file name with a space.
-   Output files will be generated in the same folder as the input,
    e.g. 'a.html', 'b.html' and 'c.html'.
-   The number of input file names must match the number of output file names.

`pdf2html -in a.pdf b.pdf c.pdf -out a.html b.html c.html`

Exit Codes
----------

To provide additional feedback, PDF2HTML returns exit codes after completing processing.
The exit codes can be used to provide user feedback, for logging, etc.
This is particularly important for applications running in an unattended environment.

The following table lists possible exit codes and their descriptions:

```
Exit Code       Description
--------------- ---------------------------------------------------------------
0               All files converted successfully.
1               Invalid parameter. One or more parameters were invalid.
2               License problem. Invalid license; license or evaluation
                expired; the feature you are trying to use is not enabled with
                the license you have.
3               Cannot open input. Input file name is invalid; file does not
                exist; network is unavailable; drive was ejected; not enough
                permissions to access the input file.
4               Cannot create output. Output file name is invalid; network is
                unavailable; drive was ejected or full; another application has
                opened the same file; not enough permission to create the
                output file.
5               Invalid input. Input file exists, but it is invalid. Usually
                indicates an invalid or corrupt PDF, or any other input file
                parsing problem, other than password problems.
6               Invalid output. Output file was created, but it is invalid.
                There were some problems, such as fonts could not be embedded,
                some issues that make the output corrupt.
7               Encrypted input. Input file is encrypted, and there is no
                password, or the password is invalid, or the password does not
                give permission to complete the requested operation.
8               Timeout. The whole or part of the operation has timed out. You
                may get better luck by increasing the timeout, because some
                operations take a lot of time to complete.
9               Cancelled. The operation has been cancelled. This is very
                unlikely in an SDK, which has no user interaction.
10              Access denied. Temporary file could not be created; registry
                could not be accessed; any other system-level denial of access.
                Exception: If the input or output file cannot be accessed, the
                error codes 3 and 4 are used instead.
17              Invalid setup. The product is not set up correctly. Files or
                registry got corrupted. Please reinstall.
18              Out of memory. There was not enough memory to complete the
                operation. Note: It is not guaranteed that you get this error
                when you run out of memory. You could also get 19 - Internal
                error.
19              Internal error. Invalid operation; unknown error; crash; access
                violation.
20              Page too large. PDF page is too large for HTML.
```

All codes other then '0' indicate that there was an error during the
conversion process.
