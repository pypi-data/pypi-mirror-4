r"""Classe base de suporte para operacoes com datas.

1)Objetivo: Esta classe fornece um conjunto de funcoes cujo principal objetivo e
    facilitar o trabalho com datas, voltadas, principalmente, para as financas:
    dias uteis, dias corridos, numero de dias uteis entre duas datas, numero de
    dias corridos entre duas datas.
"""

import csv
import re
import locale
locale.setlocale(locale.LC_ALL, '')
from datetime import date, timedelta
from operator import itemgetter #classe que permite ordenacao de dicionarios
from collections import OrderedDict

__author__ = """\n""".join(['Marcelo G Facioli (mgfacioli@yahoo.com.br)'])


def NormalizaData(Data=None):
    '''
    Transforma o separador de data de diversos formatos no separador padrao "/"

    Parametros
    ----------
        Data - cadeia de caracteres (string) que representa uma data que pode ser de diversos formatos:
             "xx/xx/xxxx"
             "xx:xx:xxxx"
             "xx-xx-xxxx"
             "xx xx xxxx"
    '''
    if Data != None:
##            partes = Data.split('/')
        try:
            DataMask = re.compile(r'^(\d{2})\D*(\d{2})\D*(\d{4})$')
            partes = DataMask.search(Data).groups()
            DataFormatada = ("{}/{}/{}".format(partes[0], partes[1], partes[2]))
            return DataFormatada
        except AttributeError as AttErr:
            print("Separador Indefinido: " + str(AttErr))
            return
    else:
        return None

class DatasFinanceiras:
    '''
        Classe base de suporte para operacoes com datas.

        Parametros
        ----------
            Data_Inicio - (OBRIGATORIO) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data inicial do
                periodo desejado (inclusive).

            Data_Fim - (OPICIONAL) cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"; a data final do
                periodo desejado (exclusive).

            Num_Dias - (OPICIONAL) numero inteiro que representa o numero de dias desejados, em substituicao ao argumento
                Data_Fim

            Path_Arquivo - (OPCIONAL/OBRIGATORIO) - seu uso e opcional para as opcoes 1 e 2 e obrigatorio para a opcao 3 (nesta opcao, o arquivo contendo os feriados sera necessario para a correta execucao da funcao.
            Portanto, quando cPath_Arquivo for obrigatorio, sera a cadeia de caracteres(string) representando o caminho (path) para o arquivo tipo csv contendo os feriados nacionais, no formato (c:\\foo)
            O arquivo deve estar no formato csv, com as colunas um, dois e tres contendo, respectivamente, data, dia_da_semana e descricao do feriado - dar preferencia para o arquivo da 'Anbima'(site 'http://portal.anbima.com.br/informacoes-tecnicas/precos/feriados-bancarios/Pages/default.aspx') o qual vem no formato xls (Excel) e que pode ser facilmente convertido para o formato csv, a partir do menu "Salvar como" e escolhendo-se como Tipo "CSV - separado por virgula" a partir do Excel.
            Apos a conversao, excluir o cabecalho (primeira linha) e informacoes adicionais (ultimas quatro ou cinco linhas) para o arquivo manter somente os dados que nos interessam - data, dia da semana e nomemclatura do feriado.

        Exemplos
        --------
            1)
                Criando variaveis auxiliares:

                    >>> varPath= "C:\\Apostilas\\Python\\BCB\\feriados.csv"
                    >>> dtIni = "01/01/2013"
                    >>> dtFin = "28/02/2013"

                Criando um instancia da classe DatasFinanceiras:

                    >>> a = DatasFinanceiras(dtIni, dtFin, Path_Arquivo=varPath)

                Gerando uma lista de dias da data inicial ate final:

                    >>> a.Dias()

                Gerando uma lista de dias sem sabados e domingos da data inicial ate final:

                    >>> a.Dias(Opt=2)

                Gerando uma lista de dias sem sabados, domingos e feriados da data inicial ate final:

                    >>> a.Dias(Opt=3)

                                Obtendo um dicionario ordenado 'Mes/Ano':(Dias Uteis por Mes)

                                        >>> a.DiasUteisPorMes()

                                Criando uma lista de todas terca-feiras entre dtIni e dtFim:

                                        >>> a.ListaDiaEspecificoSemana(3)

                                Obtendo o dia da semana em que determinada data ira cair (mesmo com tal data nao estando entre dtIni e dtFim):

                                        >>> a.DiaSemana('03/04/2013')

                                        Resultado: 'quarta-feira'

    '''
    def __init__(self, Data_Inicio=None, Data_Fim=None, Num_Dias=1, Opt=1, Path_Arquivo=''):
        self.cData_Inicio= NormalizaData(Data_Inicio)
        self.cData_Fim= NormalizaData(Data_Fim)
        self.cNum_Dias= Num_Dias
        self.cPath_Arquivo= Path_Arquivo


    def StrToData(self, Data=None):
        '''
        Transforma uma Data do formato String para formato Date

        Parametros
        ----------
        Data - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
        '''
        if Data != None:
            partes = Data.split('/')
            return date(int(partes[2]), int(partes[1]), int(partes[0]))
        else:
            return None

    def DateToStr(self, Data):
        '''
        Transforma uma Data do formato Date para formato String

        Parametros
        ----------
            Data - uma data no formato padrao do sistema (datetime.date)
        '''
        return Data.strftime("%d/%m/%Y")

    def DiaSemana(self, Data):
        '''
        Obtem o dia da semana a partir de uma data no formato String

        Parametros
            Data - cadeia de caracteres (string) que representa uma data no formato "xx/xx/xxxx"
        '''
        return (self.StrToData(Data)).strftime("%A")

    def Dias(self, Opt=1):
        '''
        Cria uma lista de Dias entre uma data inicial e uma data final.

        Parametros
        ----------
            Opt - (OPICIONAL) Permite selecionar entre 3 opcoes para gerar a lista de dias:
                Opcao 1: gera uma lista de dias corridos (incluindo sabados, domingos e feriados).
                Opcao 2: gera uma lista de dias excluindo sabados e domingos.
                Opcao 3: gera uma lista de dias excluindo sabados e domingos e feriados.
        '''
        if self.cData_Inicio == None:
            raise ValueError('A Data Inicial e imprescindivel!!!')
            return
        else:
            if type(self.cData_Inicio) == date:
                self.cData_Inicio = DateToStr(self.cData_Inicio)

        if self.cData_Fim == None and self.cNum_Dias == None:
            raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')
            return
        elif self.cData_Fim != None:
            if type(self.cData_Fim) == date:
                self.cData_Fim = DateToStr(self.cData_Fim)
            ListaDatas = [(self.StrToData(self.cData_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,(int((self.StrToData(self.cData_Fim) - self.StrToData(self.cData_Inicio)).days) + 1))]
        else:
            if self.cNum_Dias >= 1:
                ListaDatas = [(self.StrToData(self.cData_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,self.cNum_Dias)]
            else:
                ListaDatas = [(self.StrToData(self.cData_Inicio) - timedelta(days=(abs(x)))).strftime("%d/%m/%Y") for x in range(self.cNum_Dias,0)]

        if Opt == 1:
            return ListaDatas
        elif Opt == 2:
            return [dia for dia in ListaDatas if (self.StrToData(dia).isoweekday() != 6 and self.StrToData(dia).isoweekday() != 7)]
        elif Opt == 3:
            if self.cPath_Arquivo == None:
                raise ValueError('E necessario um path/arquivo!')
                return
            else:
                if self.cData_Fim == None and self.cNum_Dias >= 1:
                    self.cData_Fim = ListaDatas[-1]
                RelatorioFeriados = self.ListaFeriados()
                return [dia for dia in self.Dias(Opt=2) if self.StrToData(dia) not in RelatorioFeriados]


    def DateRange(self):
        #ver http://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
        '''
        Cria uma lista de Dias entre uma data inicial e uma data final.
        '''

        if self.cData_Fim==None and self.cNum_Dias==None:
            raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

        if type(self.cData_Inicio) == date:
            self.cData_Inicio = DateToStr(self.cData_Inicio)

        if self.cData_Fim != None:
            if type(self.cData_Fim) == date:
                self.cData_Fim = DateToStr(self.cData_Fim)
            dateList = [ (self.StrToData(self.cData_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0,(int ((self.StrToData(self.cData_Fim) - self.StrToData(self.cData_Inicio)).days) + 1)) ]
        else:
                if cNum_Dias >= 1:
                    dateList = [(self.StrToData(self.cData_Inicio) + timedelta(days=x)).strftime("%d/%m/%Y") for x in range(0, self.cNum_Dias)]
                else:
                    dateList = [(self.StrToData(self.cData_Inicio) - timedelta(days=(abs(x)))).strftime("%d/%m/%Y") for x in range(self.cNum_Dias,0)]

        return dateList

    def ListaDiasUteis(self):
        '''
        Cria uma Lista com os dias entre a Data Inicial e a Data Final, sem considerar Sabados, Domingos e Feriados.
        '''

        if self.cData_Fim==None and self.cNum_Dias==None:
            raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

        RelatorioFeriados = self.ListaFeriados()

        DUteisComFeriado = [dia for dia in self.ListaDiasCorridos() if self.StrToData(dia) not in RelatorioFeriados]
        return DUteisComFeriado


    def ListaDiasCorridos(self):
        '''
        Cria uma Lista com os dias da semana entre a Data Inicial e a Data Final sem considerar Sabados e Domingos.
        '''

        if self.cData_Fim==None and self.cNum_Dias==None:
            raise ValueError('Uma data final ou numero de dias tem que ser fornecido!')

        DiasCorridos = [dia for dia in self.DateRange() \
            if (self.StrToData(dia)).isoweekday() != 6 and (self.StrToData(dia)).isoweekday() != 7]

        return DiasCorridos


    def ListaFeriados(self):
        '''
        Cria um Dicionario com os feriados entre a Data Inicial e a Data Final.

        '''
        try:
            with open(self.cPath_Arquivo, 'rU') as csvfile:
                feriados = csv.reader(csvfile, dialect='excel', delimiter=';')
                dicSelic = {self.StrToData(row[0]):row[2] for row in feriados}

            DicFeriados = {self.StrToData(dt):dicSelic[self.StrToData(dt)] for dt in self.DateRange() if self.StrToData(dt) in dicSelic}

            return DicFeriados

        except IOError as IOerr:
            print("Erro de leitura do arquivo:" + str(IOerr))
        except KeyError as Kerr:
            print("Erro na chave do Dicionario" + str(Kerr))


    def ListaDiaEspecificoSemana(self, dia_da_semana=1):
        '''
        Cria uma Lista com os dias em que um determinado dia da semana se repete entre a Data Inicial e a Data Final.

        Parametros
        ----------
            dia_da_semana - (OPICIONAL) numero inteiro que representa o dia da semana desejado, conforme tabela:
                Segunda-Feira = 1
                Terca-Feira = 2
                Quarta-Feira = 3
                Quinta-Feira = 4
                Sexta-Feira = 5
                Sabado = 6
                Domingo = 7
        '''
        DiasCorridos = self.DateRange()

        for dia in DiasCorridos:
            DUteis = [dia for dia in DiasCorridos if (self.StrToData(dia)).isoweekday() == dia_da_semana ]

        return DUteis

    def PrimeiroDiaMes(self, Data):
        '''
        Fornecida uma data qualquer no formato string, retorna o primeiro dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            Data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
        '''
        data_base = self.StrToData(Data)
        return data_base.strftime("01/%m/%Y")

    def UltimoDiaMes(self, Data):
        '''
        Fornecida uma data qualquer no formato string, retorna o ultimo dia do mes daquela data, tambem
            no formato string.

        Parametros
        ----------
            Data - a data para a qual se deseja obeter o ultimo dia do mes (formato string).
        '''
        data_base = self.StrToData(Data)
        data_seguinte = data_base

        while data_seguinte.month == data_base.month:
            data_seguinte = date.fromordinal(data_seguinte.toordinal()+1)

        ultimo_dia_mes = self.DateToStr(date.fromordinal(data_seguinte.toordinal()-1))

        return ultimo_dia_mes

    def DiasUteisPorMes(self):
        '''
        Cria um dicionario contendo o numero de dias uteis (sem sabados, domingos e feriados) mensais entre uma
        data inicial e uma data final.

        '''
        if self.cData_Inicio==None or self.cData_Fim==None:
            raise ValueError('A data inicial e final tem que ser fornecidas!')

        ListaMesDiasUteis = []
        DicDiasUteisPorMes = {}

        for dia in self.DateRange():
            if dia == self.UltimoDiaMes(dia):
##                DUteis = self.ListaDiasUteis(self.PrimeiroDiaMes(dia), self.UltimoDiaMes(dia))
                DUteis = DatasFinanceiras(self.PrimeiroDiaMes(dia), self.UltimoDiaMes(dia), Path_Arquivo = self.cPath_Arquivo)
                MesAno = "{0}".format(self.StrToData(DUteis.UltimoDiaMes(dia)).strftime("%m/%Y"))
                DicTupple = (MesAno, len(DUteis.ListaDiasUteis()))
                ListaMesDiasUteis.append(DicTupple)

        DicDiasUteisPorMes = {per[0]:per[1] for per in ListaMesDiasUteis}

        return OrderedDict(sorted(DicDiasUteisPorMes.items(), key=lambda t:t[0]))

def main():
    pass

if __name__ == '__main__':
    main()
