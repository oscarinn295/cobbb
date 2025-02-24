
import pandas as pd
import streamlit as st
import login
import datetime as dt
import meta_ediciones
import numpy as np
import time
if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')

login.generarLogin()
login.cargar_clientes()

# Cargar datos
idc = st.secrets['ids']['cobranzas']
url = st.secrets['urls']['cobranzas']

def load():
    return login.load_data_vendedores(url)

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    login.delete_data(index,st.secrets['ids']['cobranzas'])

def upload_to_drive(image_path, folder_id):
    pass

def convert_drive_url(url):
    pass


prestamos=st.session_state["prestamos"]
cobranzas = st.session_state['cobranzas']
vendedores = st.session_state['usuarios']['usuario'].tolist()
clientes=st.session_state['clientes']['nombre'].values.tolist()


#hoy_date = dt.date.today()
#if st.button('calcular recargos por mora'):
#    # Recargar datos (en caso de que hayan cambiado)
#    cobb = login.load_data(st.secrets['urls']['cobranzas'])
    
    # Asegurar que el campo de ID se trate como cadena y convertir la fecha de vencimiento
#    cobb['prestamo_id'] = cobb['prestamo_id'].astype(str)
#    cobb['vencimiento'] = pd.to_datetime(cobb['vencimiento'], format='%d-%m-%Y', errors='coerce')
    
    # Actualizar el estado de las cobranzas:
    # • Si el vencimiento es en el futuro, dejar "Pendiente de pago"
    # • Si ya pasó y aún está en "Pendiente de pago", cambiar a "En mora"
#    cobb.loc[cobb['vencimiento'].dt.date > hoy_date, 'estado'] = 'Pendiente de pago'
#    cobb.loc[(cobb['vencimiento'].dt.date <= hoy_date) & (cobb['estado'] == 'Pendiente de pago'), 'estado'] = 'En mora'
    
    # Aplicar la función de recálculo solo a aquellas cobranzas que estén en "En mora"
#    cobb[['dias_mora', 'mora', 'monto_recalculado_mora']] = cobb.apply(meta_ediciones.calcular_recargo, axis=1)
    
    # Ordenar las columnas según tu formato requerido
#    column_order = ['id', 'prestamo_id', 'entregado', 'tnm', 'cantidad de cuotas',
#                    "vendedor", "nombre", "n_cuota", "monto", "vencimiento", 
#                    "dias_mora", "mora", 'capital', 'cuota pura', 'intereses',
#                    'amortizacion', 'iva', 'monto_recalculado_mora', 'pago', 'estado', 
#                    'medio de pago', 'cobrador', 'fecha_cobro']
#    cobb = cobb[column_order]
    
    # Reemplazar NaN y valores nulos
#    cobb = cobb.replace({np.nan: "", pd.NaT: ""})
#    cobb['vencimiento'] = pd.to_datetime(cobb['vencimiento'], errors='coerce').dt.strftime('%d-%m-%Y')
    
#    cobb['fecha_cobro'] = pd.to_datetime(cobb['fecha_cobro'], errors='coerce')
#    cobb['fecha_cobro'] = cobb['fecha_cobro'].dt.strftime('%d-%m-%Y').fillna("")
#    cobb['fecha_cobro'] = cobb['fecha_cobro'].replace("NaT", "")
    
#    data_to_upload = [cobb.columns.tolist()] + cobb.astype(str).values.tolist()
#    sheet_id = st.secrets['ids']['cobranzas']
#    login.overwrite_sheet(data_to_upload, sheet_id)

def ingreso(cobranza,descripcion):
    st.session_state["mov"]=login.load_data(st.secrets['urls']['flujo_caja'])
    caja=st.session_state["mov"]
    caja['saldo'] = pd.to_numeric(caja['saldo'], errors='coerce')
    saldo_total = caja['saldo'].sum() if not caja['saldo'].isnull().all() else 0
    mov = [
        dt.date.today().strftime("%d-%m-%Y"),
        f"COBRANZA CUOTA NRO: {cobranza['n_cuota']}, {descripcion}",
        cobranza['pago'],
        0,
        cobranza['pago'],
        saldo_total + cobranza['pago']
    ]
    login.append_data(mov,st.secrets['ids']['flujo_caja'])

def registrar(cobranza):
    fecha_cobro = st.selectbox(
        'Fecha de cobro',
        ['Seleccionar fecha', 'Hoy', 'Otra fecha'],
        index=0,
        key=f"vencimiento{cobranza['id']}"
    )

    fecha_cobro = (
        dt.date.today().strftime("%d-%m-%Y")
        if fecha_cobro == 'Hoy'
        else st.date_input('Fecha del cobro', key=f"cobro{cobranza['id']}")
        if fecha_cobro == 'Otra fecha'
        else None
    )

    cobranza['monto_recalculado_mora'] = float(cobranza['monto_recalculado_mora'])
    cobranza['monto'] = float(cobranza['monto'])

    pago = st.selectbox(
        'Monto',
        ['Pago', "Pago total", 'Otro monto'],
        index=0,
        key=f"pago{cobranza['id']}"
    )
    if f"init{cobranza['id']}" not in st.session_state:
        monto=0
        st.session_state[f"init{cobranza['id']}"]=0
    col1,col2=st.columns(2)
    def show1():
        st.session_state[f"init{cobranza['id']}"]=1
    with col1:
        monto = (
            cobranza['monto_recalculado_mora']
            if pago == "Pago total"
            else st.number_input(
                "Monto",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key=f"monto_{cobranza['id']}"
                , format="%.2f",on_change=show1
            )
            if pago == 'Otro monto'
            else 0.0
        )
    with col2:
        if st.session_state[f"init{cobranza['id']}"]==1:
            st.write(f"${monto:,.2f}")
        medio_pago = st.selectbox(
            'Medio de pago', 
            ['Seleccione una opción', 'Efectivo', 'Transferencia', 'Mixto'], 
            key=f"medio_{cobranza['id']}"
        )
    if pago=="Pago total":
        st.write(f'Monto a cobrar: {cobranza['monto_recalculado_mora']:,.2f}')

    registro = 'Pago total' if monto >= cobranza['monto_recalculado_mora'] else 'Pago parcial'


    with st.form(f"registrar_pago{cobranza['id']}"):
        cobrador = st.selectbox('Cobrador', vendedores, key=f"cobradores_{cobranza['id']}")
        obs = st.text_input('Observación', key=f'observacion_{cobranza["id"]}')
        submit_button = st.form_submit_button("Registrar")

    if submit_button:
        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        campos = {
            'cobrador': cobrador,
            'pago': monto,
            'estado': registro,
            'medio de pago': medio_pago,
            'fecha_cobro': fecha_cobro.strftime('%d-%m-%Y'),
            'obs': obs
        }
        
        for campo, valor in campos.items():
            save(int(cobranza['id']), campo, valor)
            time.sleep(1)

        st.session_state['cobranzas'] = load()  


def registrar_moroso(cobranza):
    morosos=login.load_data(st.secrets['urls']['repo_morosos'])
    int(st.session_state['cobranzas']['id'].max())
    moroso=[
            int(morosos['id'].max()),
            cobranza['nombre'],
            st.session_state['clientes'][st.session_state['clientes']['nombre']==cobranza['nombre']]['dni'],
            cobranza['n_cuota'],
            cobranza['monto'],
            cobranza['monto_recalculado_mora'],
            cobranza['dias_mora'],
            cobranza['mora']
        ]
    login.append_data(moroso,st.secrets['ids']['repo_morosos'])

def no_abono(cobranza):
    import numpy as np
    with st.form(f'no abono{cobranza['id']}'):
        st.text_input('obs',key=f"no abono_{cobranza['id']}")
        submit_button=st.form_submit_button('registrar')
    if submit_button:
        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        cobranza = cobranza.replace({np.nan: ""}) 
        save(cobranza['id'],'estado','En mora')
        st.session_state['cobranzas']=load()
        cobranza.fillna('')
        login.historial(st.session_state['cobranzas'].columns.tolist(), cobranza.values.tolist())
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1

estados=['Pendiente de pago','En mora','Pago total','Pago parcial']
def display_table():
    # Crear una copia del DataFrame original
    df = st.session_state["cobranzas"]
    df['vencimiento_dt'] = pd.to_datetime(df['vencimiento'], errors='coerce')
    
    col1, col2, col3, col4 = st.columns(4)

    with col4:
        with st.popover("Filtros"):
            reset = st.button("Resetear filtros")

            aplicar_fecha = st.checkbox("Filtrar por fecha", value=False)
            if aplicar_fecha:
                desde = st.date_input("Desde", value=dt.date.today())
                hasta = st.date_input("Hasta", value=dt.date.today())
            else:
                desde, hasta = None, None
            
            cliente = st.selectbox("Cliente", ["Todos"] + clientes, key='filtro1')
            vendedor = st.selectbox("Vendedor", ["Todos"] + vendedores, key='filtro2')
            estado = st.selectbox("Estado", ["Todos"] + estados, key='filtro3')

    if not reset:

        if aplicar_fecha and desde and hasta:
            df = df[(df['vencimiento_dt'] >= pd.Timestamp(desde)) & 
                    (df['vencimiento_dt'] <= pd.Timestamp(hasta))]
            
        if cliente != "Todos":
            df = df[df['nombre'] == cliente]

        if estado != "Todos":
            df = df[df['estado'] == estado]

        if vendedor != "Todos":
            df = df[df['vendedor'] == vendedor]
    else:
        df = st.session_state["cobranzas"]

    ITEMS_POR_PAGINA = 10
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]

    if not df_paginado.empty:
        for idx, row in df_paginado.iterrows():
            with st.container(border=True):
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

                with col1:
                    st.write(f"**Vencimiento**:")
                    st.write(f"{row['vencimiento']}")
                
                with col2:
                    st.write(f"**Vendedor**: {row['vendedor']}")
                    st.write(f"**Cliente**: \n",unsafe_allow_html=True)
                    st.write(f"{row['nombre']}")

                with col3:
                    st.write(f"**Cuota**: {row['n_cuota']}")
                    st.write(f"**Monto**: ${float(row['monto']):,.2f}")

                with col4:
                    st.write(f"**Amortización**: ${float(row['amortizacion']):,.2f}")
                    st.write(f"**Intereses**: ${float(row['intereses']):,.2f}")
                    st.write(f"**IVA**: ${float(row['iva']):,.2f}")

                with col5:
                    if row['estado']!='Pendiente de pago':
                        st.write(f"**Dias de mora**: {row['dias_mora']}")
                        st.write(f"**Monto a pagar**: ${row['mora']:,.2f}")
                    st.write(f"**Monto a pagar**: ${row['monto_recalculado_mora']:,.2f}")

                with col6:
                    if not pd.isna(row['pago']):
                        st.write(f"**Monto Pago**: ${float(row['pago']):,.2f}")
                with col7:
                    st.write(f"**Estado**: \n", unsafe_allow_html=True)
                    st.write(f"{row['estado']}")

                with col8:
                    with st.expander('Actualizar: '):
                        with st.popover('Registrar pago'):
                            registrar(row)
                        with st.popover('No abonó'):
                            no_abono(row)
    else:
        st.warning("No se encontraron resultados.")


    # --- Controles de paginación ---
    with st.container():
        col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
        with col_pag1:
            if st.session_state['pagina_actual'] > 1:
                if st.button("⬅ Anterior"):
                    st.session_state['pagina_actual'] -= 1
                    st.rerun()
        with col_pag3:
            if st.session_state['pagina_actual'] < total_paginas:
                if st.button("Siguiente ➡"):
                    st.session_state['pagina_actual'] += 1
                    st.rerun()
    
    st.write(f"Se muestran de {inicio + 1} a {min(fin, len(df))} de {len(df)} resultados")

    items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA),key='paginado')

    if items_seleccionados != ITEMS_POR_PAGINA:
        ITEMS_POR_PAGINA = items_seleccionados
        st.session_state['pagina_actual'] = 1
        st.rerun()

    if not reset:
        with st.expander('datos filtrados'):
            st.subheader("Pendientes de pago")
            st.dataframe(df[df['estado'] == 'Pendiente de pago'])

            st.subheader("En mora")
            st.dataframe(df[df['estado'] == 'En mora'])

            st.subheader("Pagados")
            st.dataframe(df[df['estado'] == 'Pago total'])

            st.subheader("Pagos parciales")
            st.dataframe(df[df['estado'] == 'Pago parcial'])

            st.subheader('Pendientes de actualizacion: ')
            # Convertir la columna 'vencimiento' a tipo datetime
            df['vencimiento'] = pd.to_datetime(df['vencimiento'], format='%d-%m-%Y')
            # Filtrar los registros vencidos con estado 'Pendiente de pago'
            df_vencidos = df[(df['vencimiento'] < pd.Timestamp.today()) & (df['estado'] == 'Pendiente de pago')]
            st.dataframe(df_vencidos)
st.title("Cobranzas")
display_table()
with st.expander('Ver todos los datos'):
    st.dataframe(load())