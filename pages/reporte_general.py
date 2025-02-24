import streamlit as st
import login
import datetime as dt
if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
# Llamar al módulo de login
login.generarLogin()
#plata en la calle
#plata por cobrar este mes
#numero de clientes por vendedor
#numero de cobranzas pendientes por mes, por vendedor y estado de las cobranzas
#todos los morosos

st.title('Reporte general')


prestamos=st.session_state['prestamos']
prestamos=prestamos[prestamos['estado']=='liquidado']
prestamos_vigentes=prestamos.shape[0]


clientes=st.session_state["clientes"]
cobranzas=st.session_state["cobranzas"]

moras=cobranzas[cobranzas['estado']=='En mora']
cartones_morosos=prestamos[prestamos['id'].isin(moras['prestamo_id'].unique())]
morosos=clientes[clientes['nombre'].isin(cartones_morosos['nombre'].unique())]


import pandas as pd
cobranzas['vencimiento'] = pd.to_datetime(cobranzas['vencimiento'], format='%d-%m-%Y')
cobranzas_2025=cobranzas[cobranzas['vencimiento'].dt.year>2025]
prestamos['fecha'] = pd.to_datetime(prestamos['fecha'], format='%d-%m-%Y')
prestamos_2025=prestamos[prestamos['fecha'].dt.year>2025]
cobranzas_2025['amortizacion']=cobranzas_2025['amortizacion'].astype(float)
generado=cobranzas_2025['pago'].sum()-cobranzas_2025['amortizacion'].sum()


vendedores=st.session_state['usuarios']['usuario'].tolist()


col1,col2=st.columns(2)
with col1:
    st.write(f"Prestamos vigentes: {prestamos_vigentes}\n",unsafe_allow_html=True)
    st.write(f"Cantidad de clientes atrasados: {morosos.shape[0]}")
with col2:
    st.write(f"Balance en 2025:{generado} \n",unsafe_allow_html=True)
    st.write('calculo: pagos-amortizaciones')



cant_clientes=[clientes[clientes['vendedor']==vendedor].shape[0] for vendedor in vendedores]

df_clientes_vendedor=pd.DataFrame({
    'vendedor':vendedores,
    'cantidad de clientes':cant_clientes
})


cant_prestamos=[prestamos[prestamos['vendedor']==vendedor].shape[0] for vendedor in vendedores]

df_prestamos_vendedor=pd.DataFrame({
    'vendedor':vendedores,
    'cantidad de prestamos':cant_prestamos
})


moras=cobranzas[cobranzas['estado']=='En mora']
cartones_morosos=prestamos[prestamos['id'].isin(moras['prestamo_id'].unique())]
morosos=clientes[clientes['nombre'].isin(cartones_morosos['nombre'].unique())]
cant_morosos=[morosos[morosos['vendedor']==vendedor].shape[0] for vendedor in vendedores]

df_morosos_vendedor=pd.DataFrame({
    'vendedor':vendedores,
    'cantidad de morosos':cant_morosos
})

with st.container(border=True):
    st.subheader('Datos por vendedor')
    col1,col2,col3=st.columns(3)

    with col1:
        st.dataframe(df_clientes_vendedor)
    with col2:
        st.dataframe(df_prestamos_vendedor)
    with col3:
        st.dataframe(df_morosos_vendedor)

#amortizacion por dia
pagados_hoy=cobranzas[cobranzas['fecha_cobro'].strftime('%d-%m-%Y')==dt.date.today().strftime('%d-%m-%Y')]
st.dataframe(pagados_hoy)



# Obtener la fecha actual
fecha_actual = dt.datetime.now()

# Extraer mes y año
mes = fecha_actual.month
año = fecha_actual.year
with st.container(border=True):
    st.subheader(f'Resultados esperados periodo: {mes} - {año}')
    col1,col2,col3=st.columns(3)
    with col1:
        st.subheader('Cobranzas semanales')
        st.write('en desarrollo')
    with col2:
        st.subheader('Cobranzas quincenales')
        st.write('en desarrollo')
    with col3:
        st.subheader('Cobranzas durante el mes')
        st.write('en desarrollo')
with st.container(border=True):
    st.subheader('Plata en la calle')
    st.write('en desarrollo')

with st.expander('Ver movimientos de caja'):
    st.subheader('Movimientos de caja')
    st.dataframe(st.session_state["mov"])

with st.expander('Ver reporte de ventas'):
    st.subheader('Reporte de ventas')
    st.dataframe(st.session_state['repo_ventas'])


idc=st.secrets['ids']['repo_mensual']
url=st.secrets['urls']['repo_mensual']
def load():
    return login.load_data(url)

def new(data):#añade una columna entera de datos
    login.append_data(data,st.secrets['ids']['clientes'])

if 'repo_mensual' not in st.session_state:
    st.session_state['repo_mensual']=load()
repo_mensual=st.session_state['repo_mensual']
with st.expander('Ver reporte Mensual'):
    st.subheader("Reporte Mensual")
    st.dataframe(repo_mensual)
