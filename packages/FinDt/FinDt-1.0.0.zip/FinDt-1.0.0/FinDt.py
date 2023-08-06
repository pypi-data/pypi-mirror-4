#-------------------------------------------------------------------------------
# Name:        FinancialDatas.py
# Purpose:     Criar um roll de funcoes que permitam trabalhar com datas e calen-
#               darios com foco em calculos financeiros (dias uteis entre duas
#               datas, feriados em um dados mes)
#
# Author:      MGFac
#
# Created:     20/11/2012
# Copyright:   (c) MGFac 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

r"""Suporte para operacoes com datas financeiras(FinDt).

1)Objetivo: Este modulo fornece um conjunto de funcoes cujo principal objetivo e
    facilitar o trabalho com datas, voltadas, principalmente, para as financas:
    dias uteis, dias corridos, numero de dias uteis entre duas datas, numero de
    dias corridos entre duas datas

2)Funcoes exportadas pelo modulo:
    StrToDate   Transforma uma Data do formato String para formato Date.

    DateToStr   Transforma uma Data do formato Date para formato String.

    Weekday     Obtem o dia da semana a partir de uma data no formata String.

    DateRange   Cria uma lista de Dias entre uma data inicial e uma data final.

    ListaDiasUteis   Cria uma Lista com os dias da semana entre a Data Inicial e a Data Final,
        sem considerar Sabados, Domingos e Feriados.

    ListaDiasCorridos   Cria uma Lista com os dias da semana entre a Data Inicial e a Data Final,
        sem considerar Sabados e Domingos.

    ListaFeriados   Cria uma Lista com os feriados entre a Data Inicial e a Data Final.

    ListaDiaEspecificoSemana    Cria uma Lista com os dias em que um determinado dia da semana se repete
        entre a Data Inicial e a Data Final

    PrimeiroDiaMes(data): Fornecida uma data qualquer no formato string, retorna o primeiro dia do mes daquela data, tambem
        no formato string.

    UltimoDiaMes(data): Fornecida uma data qualquer no formato string, retorna o ultimo dia do mes daquela data, tambem no formato string.

    Para maiores detalhes de cada funcao, consulte documentacao individual
"""

import csv
from datetime import date, timedelta
from operator import itemgetter #classe que permite ordenacao de dicionarios

def StrToDate(strDate=None):
    '''
    Transforma uma Data do formato String para formato Date

    Argumentos:
        strDate - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
    '''
    if strDate != None:
        partes = strDate.split('/')
        return date(int(partes[2]), int(partes[1]), int(partes[0]))
    else:
        return None

def DateToStr(Date):
    '''
    Transforma uma Data do formato Date para formato String

    Argumentos:
        Date - uma data no formato padrao do sistema (datetime.date)
    '''
    return Date.strftime("%d/%m/%Y")

def Weekday(strDate):
    '''
    Obtem o dia da semana a partir de uma data no formata String

    Argumentos:
        strDate - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
    '''
    return (StrToDate(strDate)).strftime("%A")

def DateRange(start_date, end_date=None, num_dias=1):
    #ver http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
    '''
    Cria uma lista de Dias entre uma data inicial e uma data final.

    Argumentos:
        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).

        num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
            end_date
    '''
    if end_date==None and num_dias==None:
        raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

    if type(start_date) == date:
        start_date = DateToStr(start_date)

    if end_date != None:
        if type(end_date) == date:
            end_date = DateToStr(end_date)
        dateList = [ (StrToDate(start_date) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,(int ((StrToDate(end_date) - StrToDate(start_date)).days) + 1)) ]
    else:
            if num_dias >= 1:
                dateList = [(StrToDate(start_date) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,num_dias)]
            else:
                dateList = [(StrToDate(start_date) - timedelta(days=(abs(x)))).strftime("%d/%m/%Y") for x in range(num_dias,0)]

    return dateList

def ListaDiasUteis(file_path, start_date, end_date=None, num_dias=1):
    '''
    Cria uma Lista com os dias entre a Data Inicial e a Data Final, sem considerar Sabados, Domingos e Feriados.
    Pode-se fornecer uma data final (end_date) ou um numero de dias (num_dias) para se obter a lista.

    Argumentos:
        file_path - (OBRIGATORIO) cadeia de caracteres(string) representando o caminho (path) para o arquivo tipo csv
            contendo os feriados nacionais, no formato (c:\\foo)
        O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data,
        dia_da_semana e descricao do feriado (dar preferencia para o arquivo da 'Anbima' o qual ja vem neste
        formato (site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx'

        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).

        num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
            end_date
    '''
    if end_date==None and num_dias==None:
        raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

    DiasCorridos = DateRange(start_date, end_date, num_dias)

    DUteis = [dia for dia in DiasCorridos if (StrToDate(dia)).isoweekday() != 6 and (StrToDate(dia)).isoweekday() != 7]

    RelatorioFeriados = ListaFeriados(file_path, start_date, end_date)

    DUteisComFeriado = [dia for dia in DUteis if StrToDate(dia) not in RelatorioFeriados]
    return DUteisComFeriado


def ListaDiasCorridos(start_date, end_date=None, num_dias=1):
    '''
    Cria uma Lista com os dias da semana entre a Data Inicial e a Data Final sem considerar Sabados e Domingos.
    Pode-se fornecer uma data final (end_date) ou um numero de dias (num_dias) para se obter a lista.

    Argumentos:
        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).

        num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
            end_date
    '''

    if end_date==None and num_dias==None:
        raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

    DiasCorridos = DateRange(start_date, end_date, num_dias)

    return DiasCorridos


def ListaFeriados(file_path, start_date, end_date=None):
    '''
    Cria um Dicionario com os feriados entre a Data Inicial e a Data Final.

    Argumentos:
        file_path - (OBRIGATORIO) cadeia de caracteres(string) representando o caminho (path) para o arquivo tipo csv
            contendo os feriados nacionais, no formato (c:\\foo)
        O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data,
        dia_da_semana e descricao do feriado (dar preferencia para o arquivo da 'Anbima' o qual ja vem neste
        formato (site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx'

        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).
    '''
    with open(file_path, 'rU') as csvfile:
        feriados = csv.reader(csvfile, dialect='excel', delimiter=';')
        dicSelic = {row[0]:row[2] for row in feriados}

    ListDt = DateRange(start_date, end_date)

    DicFeriados = {StrToDate(dt):dicSelic[dt] for dt in ListDt if dt in dicSelic}

    return DicFeriados


def ListaDiaEspecificoSemana(start_date, end_date=None, num_dias=1, dia_da_semana=1):
    '''
    Cria uma Lista com os dias em que um determinado dia da semana se repete entre a Data Inicial e a Data Final.

    Argumentos:
        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).

        num_dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
            end_date

        dia_da_semana - (OPICIONAL) numero inteiro que representa o dia da semana desejado, conforme tabela:
            Segunda-Feira = 1
            Terca-Feira = 2
            Quarta-Feira = 3
            Quinta-Feira = 4
            Sexta-Feira = 5
            Sabado = 6
            Domingo = 7
    '''
    DiasCorridos = DateRange(start_date, end_date, num_dias)

    for dia in DiasCorridos:
        DUteis = [dia for dia in DiasCorridos if (StrToDate(dia)).isoweekday() == dia_da_semana ]

    return DUteis

def PrimeiroDiaMes(data):
    '''
    Fornecida uma data qualquer no formato string, retorna o primeiro dia do mes daquela data, tambem
        no formato string.

    Argumentos:
        data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
    '''
    data_base = StrToDate(data)
    return data_base.strftime("01/%m/%Y")

def UltimoDiaMes(data):
    '''
    Fornecida uma data qualquer no formato string, retorna o ultimo dia do mes daquela data, tambem
        no formato string.

    Argumentos:
        data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
    '''
    data_base = StrToDate(data)
    data_seguinte = data_base

    while data_seguinte.month == data_base.month:
        data_seguinte = date.fromordinal(data_seguinte.toordinal()+1)

    ultimo_dia_mes = DateToStr(date.fromordinal(data_seguinte.toordinal()-1))

    return ultimo_dia_mes

def DiasUteisPorMes(file_path, start_date, end_date):
    '''
    Cria um dicionario contendo o numero de dias uteis (sem sabados, domingos e feriados) mensais entre uma
    data inicial e uma data final.

    Argumentos:
        file_path - (OBRIGATORIO) cadeia de caracteres(string) representando o caminho (path) para o arquivo tipo csv
            contendo os feriados nacionais, no formato (c:\\foo)
        O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data,
        dia_da_semana e descricao do feriado (dar preferencia para o arquivo da 'Anbima' o qual ja vem neste
        formato (site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx'

        start_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        end_date - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).
    '''
    if start_date==None or end_date==None:
        raise ValueError('A data inicial e final tem que ser fornecidas!')


    DiasCorridos = DateRange(start_date, end_date)
    ListaMesDiasUteis = []
    DicDiasUteisPorMes = {}

    for dia in DiasCorridos:
        if dia == UltimoDiaMes(dia):
            DiasCorridos2 = DateRange(PrimeiroDiaMes(dia), UltimoDiaMes(dia))
            DUteis = [dia for dia in DiasCorridos2 if (StrToDate(dia)).isoweekday() != 6 and (StrToDate(dia)).isoweekday() != 7]
            RelatorioFeriados = ListaFeriados(file_path, PrimeiroDiaMes(dia), UltimoDiaMes(dia))
            DUteisComFeriado = [dia for dia in DUteis if StrToDate(dia) not in RelatorioFeriados]
            MesAno = "{0}/{1}".format(StrToDate(UltimoDiaMes(dia)).strftime("%B")[:3],StrToDate(UltimoDiaMes(dia)).strftime("%Y"))
            DicTupple = (MesAno, len(DUteisComFeriado))
            ListaMesDiasUteis.append(DicTupple)

    DicDiasUteisPorMes = {per[0]:'' for per in ListaMesDiasUteis}

    for per in ListaMesDiasUteis:
        DicDiasUteisPorMes[per[0]] = (per[1])

    return DicDiasUteisPorMes
           #Correcao a ser feita: a funcao nao conta o ultimo dia util do mes(ver funcao range)


def main():
    pass

if __name__ == '__main__':
    main()
