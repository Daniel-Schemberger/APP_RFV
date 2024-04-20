# Bibliotecas:

import streamlit    as st
import pandas       as pd
import numpy        as np

from datetime       import datetime
from PIL            import Image
from io             import BytesIO

# Config Seaborn:
custom_params = {'axes.spine.right': False, 'axes.spine.top': False}

# Funções:

    # Carregar dataset

@st.cache_data
def load_data(file_data):
    try:
        return pd.read_csv(file_data, parse_dates=['DiaCompra'])
    except:
        return pd.read_excel(file_data)

    # Converter df para csv

@st.cache_data
def converter_csv(df):
    return df.to_csv(index=False).encode('utf-8')

    # Converter df para excel

@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()

    return processed_data

    # Criando os segmentos

def rec_class(x, r, q_dict):
    """Classifica como melhor o menor quartil
    x = valor da linha,
    r = recencia
    q_dict = dicionario do quartil"""

    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.5]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'
    
def freq_val_class(x, fv, q_dict):
    """Classifica como melhor o menor quartil
    x = valor da linha,
    fv = frequencia ou valor
    q_dict = dicionario do quartil"""

    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.5]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A' 
    

# "E:\backup\Python\2024\Python\Estudo\EBAC\Mod_6\app_RFV.py"

# Função principal da aplicação:

def main():

    # Configuração inicial da página
    st.set_page_config(page_title='RFV',
                       layout='wide',
                       initial_sidebar_state='expanded'
                       )
    
    # Título
    st.write('# Análise de Segmentação RFV')

    # Botão para carregar arquivo na aplicação
    st.sidebar.write('## Suba o arquivo')
    data = st.sidebar.file_uploader('Bank Marketing Data', type=['csv', 'xlsx'])

    # Verifica se há conteúdo carregado
    if (data is not None):
        #df = load_data('./input/data.csv')
        df = pd.read_csv(data, parse_dates=['DiaCompra'])

        dia_atual = df['DiaCompra'].max()
        st.write(f'Data máxima dos dados carregados: {dia_atual}')
        
        st.write('## Recência (R)')

        st.write('Quantos dias faz que o cliente comprou pela última vez?')

        df_rec = df.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
        df_rec.columns = ['ID_cliente', 'DiaUltimaCompra']
        df_rec['Recencia'] = df_rec['DiaUltimaCompra'].apply(
                                                            lambda x: (dia_atual - x).days
                                                            )
        st.write(df_rec.head())

        st.write('## Frequência (F)')

        st.write('Quantas vezes o cliente comprou?')

        df_freq = df.groupby('ID_cliente')['CodigoCompra'].count().reset_index()
        df_freq.columns = ['ID_cliente', 'Frequencia']
        st.write(df_freq.head())

        st.write('## Valor (V)')

        st.write('Quanto o cliente gastou?')

        df_val = df.groupby('ID_cliente')['ValorTotal'].sum().reset_index()
        df_val.columns = ['ID_cliente', 'Valor']
        st.write(df_val.head())

        st.write('## Tabela RFV:')

        df_rfv = df_rec.merge(df_freq, on='ID_cliente')
        df_rfv = df_rfv.merge(df_val, on ='ID_cliente')
        df_rfv.set_index('ID_cliente', inplace=True)
        st.write(df_rfv.head())

        st.write('## Segmentação dos dados com RFV')

        st.write('Quartis dos dados:')
        quartis = df_rfv.quantile(q=[0.25, 0.5, 0.75])
        st.write(quartis)

        st.write('Tabela com grupos:')

        df_rfv['R_quartil'] = df_rfv['Recencia'].apply(rec_class, args=('Recencia', quartis))
        df_rfv['F_quartil'] = df_rfv['Frequencia'].apply(freq_val_class, args=('Frequencia', quartis))
        df_rfv['V_quartil'] = df_rfv['Valor'].apply(freq_val_class, args=('Valor', quartis))
        
        df_rfv['Score'] = (df_rfv['R_quartil'] + df_rfv['F_quartil'] + df_rfv['V_quartil'])
        st.write(df_rfv.head())

        st.write('Quantidade de clientes por grupo')
        st.write(df_rfv['Score'].value_counts())

        st.write('### Ação de marketing/CRM')

        dict_acoes = {
        'AAA':
        'Enviar cupons de desconto, Pedir para indicar nosso produto pra algum amigo, Ao lançar um novo produto enviar amostras grátis pra esses.',
        'DDD':
        'Churn! clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
        'DAA':
        'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
        'CAA':
        'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar'
        }

        df_rfv['acoes de marketing/crm'] = df_rfv['Score'].map(dict_acoes)
        st.write(df_rfv.head())

        # Excel:

        df_xlsx = to_excel(df_rfv)
        st.download_button(label='Download xlsx',
                           data=df_xlsx,
                           file_name='RFV.xlsx')
        
        # CSV:

        df_csv = converter_csv(df_rfv)
        st.download_button(label='Download csv',
                           data=df_csv,
                           file_name='RFV.csv')
        
        st.write('Quantidade de clientes por tipo de ação:')
        st.write(df_rfv['acoes de marketing/crm'].value_counts(dropna=False))

if __name__=='__main__':
    main()

