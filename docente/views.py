# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import MySQLdb

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    db = MySQLdb.connect(host="143.106.73.88",
                         user="htc",
                         passwd="htc_123456",
                         db="hackthecampus")

    cur = db.cursor()
    context = dict(
        chart = dict(
        )
    )

    cur.execute("select lu.matricula, lu.nome, lu.lotacao,  avg(fu.liquido) sal_medio from htc_lotacao_unicamp as lu left join htc_folha_unicamp as fu on(lu.matricula = fu.matricula) "
                "where lu.lotacao not like '%Aposentado%' group by lu.matricula")
    pontos = []
    for row in cur.fetchall():
        pontos.append(
            dict(
                x = row[0],
                y = row[3]
            )
        )
    context["chart"]["docente_ativo"] = ",".join(["{x:%d, y:%.2f }" % (int(p["x"]), p["y"]) for p in pontos])



    cur.execute(
        "select lu.matricula, lu.nome, lu.lotacao,  avg(fu.liquido) sal_medio from htc_lotacao_unicamp as lu left join htc_folha_unicamp as fu on(lu.matricula = fu.matricula) "
        "where lu.lotacao like '%Aposentado%' group by lu.matricula")
    pontos = []
    for row in cur.fetchall():
        pontos.append(
            dict(
                x=row[0],
                y=row[3]
            )
        )
    context["chart"]["docente_aposentado"] = ",".join(["{x:%d, y:%.2f }" % (int(p["x"]), p["y"]) for p in pontos])

    return render(request, "docente/index.html", context)

def docente(request, docente_id):
    db = MySQLdb.connect(host="143.106.73.88",
                         user="htc",
                         passwd="htc_123456",
                         db="hackthecampus")
    context = dict(
        docente = dict(
            folha = []
        )
    )
    cur = db.cursor()

    cur.execute("select bruto,indenizacoes,redutor,descontos_legais,liquido,ano,mes from htc_folha_unicamp where matricula = %d" % int(docente_id))

    for row in cur.fetchall():
        context["docente"]["folha"].append(
            dict(
                bruto = row[0],
                indenizacoes = row[1],
                redutor = row[2],
                descontos_legais = row[3],
                liquido = row[4],
                ano = row[5],
                mes = row[6]
            )
        )

    cur.execute("select lotacao,nome,ramal from htc_lotacao_unicamp where matricula = %d" % int(docente_id))
    # print all the first cell of all the rows
    for row in cur.fetchall():
        context["docente"]["lotacao"] = row[0].replace("\r","")
        context["docente"]["nome"] = row[1]
        context["docente"]["ramal"] = row[2]

    db.close()

    labels = ",".join( ['"%d/%d"' % (x, 2016) for x in xrange(1, 13)] + ['"%d/%d"' % (x, 2017) for x in xrange(1, 6)])

    def get_value(context, ano, mes):
        for x in sorted(context["docente"]["folha"]):
            if x["ano"]==ano and x["mes"]==mes:
                return "%.2f" % x["liquido"]
        return " "

    values = ",".join([get_value(context, 2016, x) for x in xrange(1, 13)] + [get_value(context, 2017, x) for x in xrange(1, 6)])
    print values


    missing = ["'%d/%d'" % (x, 2016) for x in xrange(1, 13) if get_value(context, 2016, x) == " "] + ["'%d/%d'" % (x, 2017) for x in xrange(1, 6) if get_value(context, 2017, x) == " "]

    context["chart"] = dict(
        labels = labels,
        values = values,
        missing = missing
    )

    return render(request, "docente/docente.html", context)