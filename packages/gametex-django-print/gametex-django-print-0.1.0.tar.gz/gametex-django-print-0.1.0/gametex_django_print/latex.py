#encoding=utf-8
from django.core.mail import mail_admins
import os, tempfile, subprocess
from django.conf import settings

def setup_texpath():
    if not settings.GAMETEX_PROJECT_ROOT in os.environ['TEXINPUTS']:
        os.environ['TEXINPUTS'] = "%s/LaTeX/:%s" % (settings.GAMETEX_PROJECT_ROOT, os.environ['TEXINPUTS'])

def pdflatex(entities, gametexclass, owner=None, target_dir=None):
    """
    Given a list of entities and a GameTeX class, generate a PDF.

    Returns a path to a filename, or None.

    WARNING: This could be *seriously insecure* if you don't sanitize the input.
    """
    setup_texpath()

    try:
        template = """
       \\documentclass[%(type)s]{%(class)s}
       \\begin{document}

       %(owner)s
       %(entities)s

       \\end{document}
       """

        template %= {
            'type': gametexclass,
            'class': settings.GAMETEX_NAME,
            'owner': ("\\name{%s}" % owner) if owner else '',
            'entities': "\n".join(["\\%s{}" % ent for ent in entities])
        }

        cwd = os.getcwd()
        tempf = tempfile.mkstemp(suffix='.tex')
        os.chdir(target_dir if target_dir else os.path.dirname(tempf[1]))
        tpf = os.fdopen(tempf[0], 'w')
        tpf.write(template)
        tpf.close()

        result = subprocess.check_output("pdflatex -halt-on-error %s" % tempf[1], shell=True)
        src = tempf[1].replace('.tex', '.pdf')
        tgt = ""
        if target_dir:
            tgt = os.path.join(target_dir, os.path.basename(src))
            os.rename(src, tgt)
        os.chdir(cwd)

        if target_dir:
            return tgt
        else:
            return src
    except subprocess.CalledProcessError as e:
        mail_admins("%s LaTeX Failure" % settings.GAMETEX_NAME, """
        Entities: %s
        GTClass: %s
        Owner: %s
        Output:
        %s
        """ % ("\n".join(entities), gametexclass, owner, e.output),
            fail_silently=True)
        return None