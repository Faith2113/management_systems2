import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from faker import Faker


# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")

    menu = ["Clientes", "Contas a Pagar", "Contas a Receber", "Lançamentos", "Relatórios"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)

    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)

    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)

    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)

    elif choice == "Relatórios":
        st.subheader("Relatórios de Fluxo de Caixa")

        # Adicionando uma opção para visualizar a tabela ou o gráfico de fluxo de caixa
        report_option = st.radio("Selecione o tipo de relatório:",
                                 ("Tabela de Lançamentos",
                                  "Gráfico de Fluxo de Caixa",
                                  "Distribuição das Contas a Pagar por Fornecedor",
                                  "Status das Contas a Pagar e Receber"))

        if report_option == "Tabela de Lançamentos":
            df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
            st.dataframe(df)

        elif report_option == "Gráfico de Fluxo de Caixa":
            # Consulta para obter a receita e a despesa por mês
            query = """
            SELECT 
                strftime('%Y-%m', data) AS mes, 
                tipo, 
                SUM(valor) AS total
            FROM lancamentos
            GROUP BY mes, tipo
            ORDER BY mes
            """
            df = pd.read_sql_query(query, conn)

            # Criando gráfico de barras com Plotly
            fig = px.bar(df, x='mes', y='total', color='tipo', title='Fluxo de Caixa por Mês',
                         labels={'mes': 'Mês', 'total': 'Valor', 'tipo': 'Tipo de Lançamento'})
            st.plotly_chart(fig)

        elif report_option == "Distribuição das Contas a Pagar por Fornecedor":
            # Consulta para obter os fornecedores e valores devidos
            query = """
            SELECT fornecedor, SUM(valor) AS total
            FROM contas_pagar
            GROUP BY fornecedor
            ORDER BY total DESC
            LIMIT 10
            """
            df = pd.read_sql_query(query, conn)

            # Escolha do gráfico: pizza ou barras
            chart_type = st.radio("Escolha o tipo de gráfico:", ("Gráfico de Pizza", "Gráfico de Barras"))

            if chart_type == "Gráfico de Pizza":
                # Criando gráfico de pizza com Plotly
                fig = px.pie(df, names='fornecedor', values='total',
                             title='Distribuição das Contas a Pagar por Fornecedor')
                st.plotly_chart(fig)

            elif chart_type == "Gráfico de Barras":
                # Criando gráfico de barras com Plotly
                fig = px.bar(df, x='fornecedor', y='total', title='Distribuição das Contas a Pagar por Fornecedor',
                             labels={'fornecedor': 'Fornecedor', 'total': 'Valor devido'})
                st.plotly_chart(fig)

        elif report_option == "Status das Contas a Pagar e Receber":
            # Consulta para obter o status das contas a pagar
            query_pagar = """
            SELECT 
                CASE 
                    WHEN status = 'Pendente' THEN 'Pendente' 
                    ELSE 'Pagas'
                END AS status,
                SUM(valor) AS total
            FROM contas_pagar
            GROUP BY status
            """
            df_pagar = pd.read_sql_query(query_pagar, conn)

            # Consulta para obter o status das contas a receber
            query_receber = """
            SELECT 
                CASE 
                    WHEN status = 'Pendente' THEN 'Pendente' 
                    ELSE 'Recebidas'
                END AS status,
                SUM(valor) AS total
            FROM contas_receber
            GROUP BY status
            """
            df_receber = pd.read_sql_query(query_receber, conn)

            # Concatenando os dois dataframes para mostrar no gráfico
            df_combined = pd.concat([df_pagar, df_receber], ignore_index=True)

            # Criando gráfico de barras com Plotly
            fig = px.bar(df_combined, x='status', y='total', color='status',
                         title='Status das Contas a Pagar e Receber',
                         labels={'status': 'Status', 'total': 'Total de Valores'})
            st.plotly_chart(fig)

    conn.close()


if __name__ == "__main__":
    main()
