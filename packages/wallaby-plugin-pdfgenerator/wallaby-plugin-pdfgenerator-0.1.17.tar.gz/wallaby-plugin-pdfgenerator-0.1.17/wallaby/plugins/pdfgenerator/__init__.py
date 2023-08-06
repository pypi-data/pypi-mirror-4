from Cheetah.Template import Template
from Cheetah.Filters import EncodeUnicode
from twisted.internet import defer
import tempfile, codecs, subprocess, os, shutil
import os.path

class LatexError(Exception):
    def __init__(self, retcode, output, input):
        self._error = (retcode, output, input)

    def __str__(self):
        return str(self._error)

class LatexFilter(EncodeUnicode):
    def filter(self,  value, **kwargs):
        tmp = '<%%>'
        s = super(LatexFilter, self).filter(value, **kwargs)
        s = s.replace("\\", "\\textbackslash"+tmp)
        s = s.replace("^", "\\textasciicircum"+tmp)
        s = s.replace("~", "\\~"+tmp)
        s = s.replace("{", "\\{")
        s = s.replace("}", "\\}")
        s = s.replace(tmp, "{}")
        s = s.replace("\n", "\\\\")
        s = s.replace("#", "\\#")
        s = s.replace("$", "\\$")
        s = s.replace("%", "\\%")
        s = s.replace("&", "\\&")
        s = s.replace("_", "\\_")
        return s

class PDFGenerator:
    def __init__(self, templateFile):
        self._template = Template.compile(file=templateFile) #precompile template
        self._path = os.path.dirname(templateFile)
        self._deferreds = {}

    def generatePDF(self, namespaces):
        d = defer.Deferred()
        from twisted.internet import reactor
        reactor.callLater(0, self._generatePDF, namespaces, d)

        return d

    def _generatePDF(self, namespaces, d):
        template = self._template(namespaces=namespaces, filter=LatexFilter)
        tempdir = tempfile.mkdtemp()

        texfile = None
        stdout = None
        pdf = None

        try:
            #save latex file
            texfile = codecs.open(os.path.join(tempdir, 'document.tex'),'w','utf-8')
            texfile.write(template.respond())
            texfile.close()

            path = "c:\\wallaby\\miktex\\miktex\\bin\\"
            if not os.path.exists(path):
                path = "" 
                
            print path + 'pdflatex -draftmode -halt-on-error -output-directory="'+tempdir+'" "'+os.path.join(tempdir,'document.tex')+'"'
            print "in folder", self._path

            #compile latex file
            stdout = open(os.path.join(tempdir, 'stdout.log'), 'w')
            retcode = subprocess.call(path + 'pdflatex -draftmode -halt-on-error -output-directory="'+tempdir+'" "'+os.path.join(tempdir,'document.tex')+'"', shell=True, cwd=self._path, stderr=subprocess.STDOUT, stdout=stdout)
            stdout.close()

            if retcode != 0:
                stdout = open(os.path.join(tempdir,'stdout.log'), 'r')
                output = stdout.read()
                stdout.close()

                try:
                    output = output.encode('ascii')
                except:
                    try:
                        output = output.encode('cp1252')
                    except:
                        output = "Bad encoding"

                d.errback(LatexError(retcode, output, template.respond()))
        
            else:
                #compile latex file, 2nd run
                stdout = open(os.path.join(tempdir,'stdout.log'), 'w')
                print path + 'pdflatex -halt-on-error -output-directory="'+tempdir+'" "'+os.path.join(tempdir,'document.tex') + '"'
                print "in folder", self._path
                retcode = subprocess.call(path + 'pdflatex -halt-on-error -output-directory="'+tempdir+'" "'+os.path.join(tempdir,'document.tex') + '"', shell=True, cwd=self._path, stderr=subprocess.STDOUT, stdout=stdout)
                stdout.close()

                if retcode != 0:
                    stdout = open(os.path.join(tempdir,'stdout.log'), 'r')
                    output = stdout.read()
                    stdout.close()

                    try:
                        output = output.encode('ascii')
                    except:
                        try:
                            output = output.encode('cp1252')
                        except:
                            output = "Bad encoding"
    
                    d.errback(LatexError(retcode, output, template.respond()))
                else:
                    pdf = open(os.path.join(tempdir,'document.pdf'), 'rb')
                    pdfData = pdf.read()
                    pdf.close()

                    d.callback(pdfData)
        finally:
            if texfile and texfile.closed == False:
                texfile.close()
            if stdout and stdout.closed == False:
                stdout.close()
            if pdf and pdf.closed == False:
                pdf.close()

            # shutil.rmtree(tempdir)
