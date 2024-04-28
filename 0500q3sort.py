#!/usr/bin/env python3

import PyPDF2
import sys
import os

if "_qp_" in sys.argv[1]:
    qp = True
    ins = False
elif "_in_" in sys.argv[1]:
    qp = False
    ins = True
else:
    print('*** "%s" does not look like a question paper or insert' % sys.argv[1])
    exit(1)

f = open(sys.argv[1], "rb")
r = PyPDF2.PdfReader(f)
w = PyPDF2.PdfWriter()
flag = False
err = False
additional = False

for i in range(len(r.pages)): 
    t = r.pages[i].extract_text().lower()
    if (("blank page" in t) or ("blankpage" in t)) and flag:
        break
    elif (("additional page" in t) or ("additionalpage" in t)) and flag:
        additional = True
        break
    elif ("question 3" in t or "question3" in t) or flag:
        try:
            if qp:
                w.append(fileobj=f, pages=(i, i + 1))
                flag = True
            elif ins:
                w.append(fileobj=f, pages=(i, i + 1))
                flag = True
        except Exception:
            err = True


if err:
    print('*** "%s" error' % sys.argv[1])
    os.system("cp %s trouble/%s" % (sys.argv[1], sys.argv[1]))
    w.close()
elif (not additional) and qp:
    print('*** "%s" qp does not contain "Additional Page"' % sys.argv[1])
elif flag:
    g = open("trim/" + sys.argv[1].replace(".pdf", ".trim.pdf"), "wb")
    w.write(g)
    w.close()
    g.close()
else:
    print('*** "%s" does not contain "Question 3"' % sys.argv[1])
    os.system("cp %s noq/%s" % (sys.argv[1], sys.argv[1]))
    w.close()
