#aca es donde quiero hacer un poco de magia
#quiero que al buscar al cliente, se cree un objeto tomando todos sus datos del excel y que de ahi se hagan todos los calculos necesarios
import streamlit as st
import pandas as pd

def load_data_vendedores(url):
    df=pd.read_excel(url,engine='openpyxl')
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]
    return df


if "clientes" not in st.session_state:
    st.session_state["clientes"] = load_data_vendedores(st.secrets['urls']['clientes'])
if "cobranzas" not in st.session_state:
    st.session_state["cobranzas"] = load_data_vendedores(st.secrets['urls']['cobranzas'])
if "prestamos" not in st.session_state:
    st.session_state["prestamos"] = load_data_vendedores(st.secrets['urls']['prestamos'])


clientes= st.session_state['clientes']
cobranzas= st.session_state["cobranzas"]
prestamos= st.session_state["prestamos"]

class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre
        self.cliente = self.datos_cliente(st.session_state['urls']['clientes'])
        self.prestamos = self.datos_prestamos(st.session_state['urls']['prestamos'])
        self.cobranzas = self.datos_cobranzas(st.session_state['urls']['cobranzas'])

    def datos_cliente(self):

        return clientes[clientes['nombre']==self.nombre]
    
    def datos_prestamos(self, ruta):
        
        return prestamos[prestamos['nombre']==self.nombre]

    def datos_cobranzas(self, ruta):
        
        return cobranzas[cobranzas['prestamo_id'].isin(prestamos['id'].unique)]


# Verificar si el cliente ya está en session_state
if "cliente" not in st.session_state:
    st.session_state["cliente"] = Cliente(
        id_cliente=123,  # Podrías recibir este ID del usuario
        ruta_clientes="clientes.xlsx",
        ruta_prestamos="prestamos.xlsx",
        ruta_cobranzas="cobranzas.xlsx"
    )

cliente = st.session_state["cliente"]

st.write("Datos del cliente:", cliente.datos_cliente)
st.write("Préstamos:", cliente.prestamos)
st.write("Cobranzas:", cliente.cobranzas)
