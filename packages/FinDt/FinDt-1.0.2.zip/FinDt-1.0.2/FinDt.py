r"""Suporte para operacoes com datas financeiras(FinDt).

1)Objetivo: Este modulo fornece um conjunto de funcoes cujo principal objetivo e
    facilitar o trabalho com datas, voltadas, principalmente, para as financas:
    dias uteis, dias corridos, numero de dias uteis entre duas datas, numero de
    dias corridos entre duas datas
"""

import csv
import locale
locale.setlocale(locale.LC_ALL, '')
from datetime import date, timedelta
from operator import itemgetter #classe que permite ordenacao de dicionarios
from collections import OrderedDict

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

def DiaSemana(strDate):
    '''
    Obtem o dia da semana a partir de uma data no formato String

    Argumentos:
        strDate - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
    '''
    return (StrToDate(strDate)).strftime("%A")

def Dias(Data_Inicio, Data_Fim=None, Num_Dias=1, Opt=1, Path_Arquivo=''):
    '''
    Cria uma lista de Dias entre uma data inicial e uma data final.

    Argumentos:
        Data_Inicio - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
            periodo desejado (inclusive).

        Data_Fim - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
            periodo desejado (exclusive).

        Num_Dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
            Data_Fim

        Opt - (OPICIONAL) Permite selecionar entre 3 opcoes para gerar a lista de dias:
            Opcao 1: gera uma lista de dias corridos (incluindo sabados, domingos e feriados).
            Opcao 2: gera uma lista de dias excluindo sabados e domingos.
            Opcao 3: gera uma lista de dias excluindo sabados e domingos e feriados.

        Path_Arquivo - (OPCIONAL/OBRIGATORIO) - seu uso e opcional para as opcoes 1 e 2 e obrigatorio para a opcao 3 (nesta opcao, o arquivo contendo os feriados sera necessario para a correta execucao da funcao.
        Portanto, quando Path_Arquivo for obrigatorio, sera a cadeia de caracteres(string) representando o caminho (path) para o arquivo tipo csv contendo os feriados nacionais, no formato (c:\\foo)
        O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data, dia_da_semana e descricao do feriado - dar preferencia para o arquivo da 'Anbima'(site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx') o qual vem no formato xls (Excel) e que pode ser facilmente convertido para o formato csv, a partir do menu "Salvar como" e escolhendo-se como Tipo "CSV - separado por virgula" a partir do Excel.
        Apos a conversao, excluir o cabecalho (primeira linha) e informacoes adicionais (ultimas quatro ou cinco linhas) para o arquivo manter somente os dados que nos interessam - data, dia da semana e nomemclatura do feriado.
    '''
    if Data_Inicio == None:
        raise ValueError('A Data Inicial e imprescindivel!!!')
        return
    else:
        if type(Data_Inicio) == date:
            Data_Inicio = DateToStr(Data_Inicio)

    if Data_Fim == None and Num_Dias == None:
        raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')
        return
    elif Data_Fim != None:
        if type(Data_Fim) == date:
            Data_Fim = DateToStr(Data_Fim)
        ListaDatas = [(StrToDate(Data_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,(int((StrToDate(Data_Fim) - StrToDate(Data_Inicio)).days) + 1))]
    else:
        if Num_Dias >= 1:
            ListaDatas = [(StrToDate(Data_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,Num_Dias)]
        else:
            ListaDatas = [(StrToDate(Data_Inicio) - timedelta(days=(abs(x)))).strftime("%d/%m/%Y") for x in range(Num_Dias,0)]

    if Opt == 1:
        return ListaDatas
    elif Opt == 2:
        return [dia for dia in ListaDatas if (StrToDate(dia).isoweekday() != 6 and StrToDate(dia).isoweekday() != 7)]
    elif Opt == 3:
        if Path_Arquivo == None:
            raise ValueError('E necessario um path/arquivo!')
            return
        else:
            if Data_Fim == None and Num_Dias >= 1:
                Data_Fim = ListaDatas[-1]
            RelatorioFeriados = ListaFeriados(Path_Arquivo, Data_Inicio, Data_Fim)
            return [dia for dia in Dias(Data_Inicio, Data_Fim, Num_Dias, Opt=2) if StrToDate(dia) not in RelatorioFeriados]


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

    RelatorioFeriados = ListaFeriados(file_path, start_date, end_date)

    DUteisComFeriado = [dia for dia in ListaDiasCorridos(start_date, end_date, num_dias) if StrToDate(dia) not in RelatorioFeriados]
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

    DiasCorridos = [dia for dia in DateRange(start_date, end_date, num_dias) \
        if (StrToDate(dia)).isoweekday() != 6 and (StrToDate(dia)).isoweekday() != 7]

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
    try:
        with open(file_path, 'rU') as csvfile:
            feriados = csv.reader(csvfile, dialect='excel', delimiter=';')
            dicSelic = {StrToDate(row[0]):row[2] for row in feriados}

        DicFeriados = {StrToDate(dt):dicSelic[StrToDate(dt)] for dt in DateRange(start_date, end_date) if StrToDate(dt) in dicSelic}

        return DicFeriados

    except IOError as IOerr:
        print("Erro de leitura do arquivo:" + str(IOerr))
    except KeyError as Kerr:
        print("Erro na chave do Dicionario" + str(Kerr))


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

    ListaMesDiasUteis = []
    DicDiasUteisPorMes = {}

    for dia in DateRange(start_date, end_date):
        if dia == UltimoDiaMes(dia):
            DUteis = ListaDiasUteis(file_path, PrimeiroDiaMes(dia), UltimoDiaMes(dia))
            MesAno = "{0}".format(StrToDate(UltimoDiaMes(dia)).strftime("%m/%Y"))
            DicTupple = (MesAno, len(DUteis))
            ListaMesDiasUteis.append(DicTupple)

    DicDiasUteisPorMes = {per[0]:per[1] for per in ListaMesDiasUteis}

    return OrderedDict(sorted(DicDiasUteisPorMes.items(), key=lambda t:t[0]))

def main():
    pass

if __name__ == '__main__':
    main()
