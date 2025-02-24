import pandas as pd
import login
import streamlit as st

if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
login.cargar_clientes()
idc=st.secrets['ids']['clientes']
url = st.secrets['urls']['clientes']
def load():
    return login.load_data_vendedores(url)

def save(id,column,data):#modifica un solo dato
    login.save_data(id,column,data,idc)
    
def new(data):#añade una fila entera de datos
    login.append_data(data,idc)
login.generarLogin()
st.session_state['clientes']=load() 

cobranzas=st.session_state['cobranzas']
prestamos=st.session_state['prestamos']


import numpy as np

def delete(index):  
    # 🔹 1. Obtener los datos antes de eliminar
    df_original = st.session_state['clientes'].copy()

    # 🔹 2. Filtrar el DataFrame para eliminar la fila con el índice dado
    df_nuevo = df_original[df_original['id'] != index].copy()

    # 🔹 3. Verificar si después de eliminar quedan datos
    if df_nuevo.empty:
        st.error("Error: No se puede eliminar la última fila, la tabla quedaría vacía.")
        return  # Detener la ejecución

    # 🔹 4. Resetear los índices después de eliminar
    df_nuevo.reset_index(drop=True, inplace=True)
    df_nuevo['id'] = df_nuevo.index  # Asignar nuevos IDs ordenados

    # 🔹 5. Convertir `fecha_nac` a string
    try:
        df_nuevo['fecha_nac'] = df_nuevo['fecha_nac'].dt.strftime("%d-%m-%Y")
    except:
        pass

    # 🔹 6. Reemplazar NaN y valores nulos para evitar errores JSON
    df_nuevo.replace([np.nan, None], '', inplace=True)

    # 🔹 7. Preparar datos para sobrescribir
    df_final = [df_nuevo.columns.tolist()]  # Encabezados
    df_final += df_nuevo.values.tolist()  # Datos

    # 🔹 8. Sobrescribir la hoja solo si hay datos
    login.overwrite_sheet(df_final, idc)

    # 🔹 9. Actualizar la sesión con los nuevos datos
    st.session_state['clientes'] = df_nuevo

    # 🔹 10. Recargar la página
    st.rerun()




if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1


vendedores=st.session_state['usuarios']['usuario'].tolist()
# Función para mostrar la tabla con filtro de búsqueda
from datetime import date
def editar(cliente):
    idx=cliente['id']
    col1,col2,col3,col4=st.columns(4)
    with col1:
        st.subheader("Editar Cliente: ")
    with st.form(f'editar_cliente_{cliente['id']}'):
        st.session_state["dni"] = cliente["dni"]
        st.session_state["nombre"] = cliente["nombre"]
        st.session_state["direccion"] = cliente["direccion"]
        st.session_state["celular"] = cliente["celular"]
        st.session_state["vendedor"] = cliente["vendedor"]
        st.session_state['scoring']= cliente['scoring']
        if cliente['fecha_nac'] is not None:
            st.session_state['fecha_nac']=cliente['fecha_nac']
        else:
            st.session_state['fecha_nac']=date.today().strftime('%d/%m/%Y')
        st.session_state['mail']=cliente['mail']

        col1,col2=st.columns(2)
        with col1:
            dni = st.text_input("DNI", value=st.session_state.get("dni", ""),key=f'dni_{idx}')
            nombre = st.text_input("Nombre", value=st.session_state.get("nombre", ""),key=f'nombre_{idx}')
            if isinstance(st.session_state['fecha_nac'], str):
                try:
                    fecha_nac_value = pd.to_datetime(st.session_state['fecha_nac'], format="%d/%m/%Y")
                except Exception:
                    fecha_nac_value = None
            else:
                fecha_nac_value = st.session_state['fecha_nac']

            fecha_nac = st.date_input("Fecha", value=fecha_nac_value if fecha_nac_value and not pd.isna(fecha_nac_value) else date.today(), key=f'fecha_{idx}')
            vendedor=st.selectbox('vendedor',vendedores,key=f'vendedor_{idx}')
        with col2:
            direccion = st.text_input("Dirección", value=st.session_state.get("direccion", ""),key=f'direccion_{idx}')
            celular = st.text_input("Celular", value=st.session_state.get("celular", ""),key=f'celular_{idx}')
            mail=st.text_input("Mail", value=st.session_state.get("mail", ""),key=f'mail_{idx}')
            scoring= st.text_input("Scoring", value=st.session_state.get("scoring", ""),key=f'scoring_{idx}')
        submit_button=st.form_submit_button('guardar')
    if submit_button:
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['id']==idx],'edicion_viejo')
        datos= [(nombre,'nombre'),
                (vendedor,'vendedor'),
                (scoring,'scoring'),
                (direccion,'direccion'),
                (fecha_nac.strftime("%d-%m-%Y"), 'fecha_nac'),
                (dni,'dni'),
                (celular,'celular'),
                (mail,'mail')]
        #login.historial(st.session_state['clientes'][st.session_state['clientes']['id']==idx],'edicion_nuevo')
        for dato,col in datos:
            save(idx,col,dato)
            login.cargar_clientes()
        st.success("cambios guardados")

def crear():
    st.title('Crear Cliente: ')
    with st.form("form_crear_cliente"):
        col1, col2 = st.columns(2)
        
        with col1:
            dni = st.text_input("DNI")
            nombre = st.text_input("Apellido y Nombre")
            fecha_nac = st.date_input("Fecha",format="DD/MM/YYYY")
            vendedor = st.selectbox('Vendedor', vendedores, key='vendedores')
        
        with col2:
            direccion = st.text_input("Dirección")
            celular = st.text_input("Celular")
            mail = st.text_input("Mail")
            scoring = st.text_input("Scoring")

        # Botón de guardar dentro del formulario
        submit_button = st.form_submit_button("Guardar")
        
        if submit_button:
            nuevo_cliente = [
                max(st.session_state['clientes']['id'])+1,
                nombre,
                vendedor,
                scoring,
                direccion,
                fecha_nac.strftime("%d-%m-%Y"),
                dni,
                celular,
                mail
            ]
            new(nuevo_cliente)
            login.cargar_clientes()
            st.success('Cliente guardado correctamente')
            login.historial(['id','nombre','vendedor', 'scoring', 'direccion', 'fecha_nac', 'dni', 'celular', 'mail'],nuevo_cliente)

def display_table(search_query=""):
    st.subheader("Lista de Clientes")
    df=st.session_state['clientes']
    
    if search_query:
        df =df[df['nombre'].str.contains(search_query, case=False, na=False)]
    # Configuración de paginación
    ITEMS_POR_PAGINA = 10
    # Paginación
    total_paginas = (len(df) // ITEMS_POR_PAGINA) + (1 if len(df) % ITEMS_POR_PAGINA > 0 else 0)
    inicio = (st.session_state['pagina_actual'] - 1) * ITEMS_POR_PAGINA
    fin = inicio + ITEMS_POR_PAGINA
    df_paginado = df.iloc[inicio:fin]
    # Crear tabla con botones
    if not df.empty:
        if st.session_state['user_data']['permisos'].iloc[0]=='admin':
                for idx, row in df_paginado.iterrows():
                    with st.container(border=True):
                            col1, col2, col3 = st.columns(3)  # Distribuir columnas
                            with col1:
                                st.write(f"**Nombre**: {row['nombre']} - **Vendedor**: {row['vendedor']}")
                                st.write(f"**Dirección**: {row['direccion']} - **DNI**: {row['dni']} - **Celular**: {row['celular']}")
                            with col2:
                                with st.popover(f'✏️ Editar'):
                                            editar(row)
                            with col3:
                                if st.button("🗑️Eliminar", key=f"delete_{row['id']}"):
                                    delete(row['id'])
                                    st.rerun()
                                if st.button("ver detalles",key=f'cliente_{idx}'):
                                    st.session_state['cliente']=row
                                    st.switch_page("pages/por_cliente.py")
        else:
            for idx, row in df_paginado.iterrows():
                col1, col2, col3,col4 = st.columns(4)  # Distribuir columnas
                with col1:
                    st.write(f"**Nombre**: {row['nombre']}")
                with col2:
                    st.write(f"**Dirección**: {row['direccion']}- **DNI**: {row['dni']}")
                with col3:
                    st.write(f"**Celular**: {row['celular']}  **Mail**: {row['mail']}")
                with col4:
                    if st.button("ver detalles",key=f'cliente_{idx}'):
                        st.session_state['cliente']=row
                        st.switch_page("pages/por_cliente.py")

    else:
        st.warning("No se encontraron resultados.")
    # Controles de paginación
    with st.container(border=True):
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
    # Contador de registros y selector de cantidad por página
    with st.container(border=True):
        st.write(f"Se muestran de {inicio + 1} a {min(fin, len(df))} de {len(df)} resultados")
        items_seleccionados = st.selectbox("Por página", [10, 25, 50, 100], index=[10, 25, 50, 100].index(ITEMS_POR_PAGINA),key='seleccionados')
        if items_seleccionados != ITEMS_POR_PAGINA:
            ITEMS_POR_PAGINA = items_seleccionados
            st.session_state['pagina_actual'] = 1
            st.rerun()



# Página de lista de clientes
st.title("Clientes")
col1,col2,col3,col4=st.columns(4)
with col4:
    if st.session_state['user_data']['permisos'].iloc[0]=='admin':
        # Botón para crear un nuevo cliente
        with st.popover("Crear cliente"):
            crear()
with col1:
    # Botón para reiniciar datos
    if st.button("Reiniciar datos"):
        login.cargar_clientes()
with st.container(border=True):
    col1,col2=st.columns(2)
    with col2:
        search_query = st.text_input("Buscar cliente", key="search_query")
    display_table(search_query)
    with st.expander('Ver todos los datos'):
        st.dataframe(st.session_state["clientes"])

import datetime as dt
st.title("morosos")
moras=cobranzas[cobranzas['estado']=='En mora']
cartones_morosos=prestamos[prestamos['id'].isin(moras['prestamo_id'].unique())]
morosos=st.session_state['clientes'][st.session_state['clientes']['nombre'].isin(cartones_morosos['nombre'].unique())]

def save_data(id_value, column_name, new_value, sheet_id):
        worksheet = login.get_worksheet(sheet_id)
        col_labels = worksheet.row_values(1)

        if column_name not in col_labels:
            return
        
        col_index = col_labels.index(column_name) + 1
        id_column_values = worksheet.col_values(1)  # Se asume que la columna "ID" siempre es la primera
        
        if str(id_value) in id_column_values:
            row_index = id_column_values.index(str(id_value)) + 1
            worksheet.update_cell(row_index, col_index, new_value)

# Cargar datos
idc2 = st.secrets['ids']['cobranzas']
url2 = st.secrets['urls']['cobranzas']

def save2(id,column,data):#modifica un solo dato
    save_data(id,column,data,idc)



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

def registrar(cobranza,idd):
    fecha_cobro = st.selectbox(
        'Fecha de cobro',
        ['Seleccionar fecha', 'Hoy', 'Otra fecha'],
        index=0,
        key=f"{idd}"
    )

    fecha_cobro = (
        dt.date.today().strftime("%d-%m-%Y")
        if fecha_cobro == 'Hoy'
        else st.date_input('Fecha del cobro', key=f"cobro{idd}").strftime("%d-%m-%Y")
        if fecha_cobro == 'Otra fecha'
        else None
    )

    cobranza['monto_recalculado_mora'] = float(cobranza['monto_recalculado_mora'])
    cobranza['monto'] = float(cobranza['monto'])

    pago = st.selectbox(
        'Monto',
        ['Pago', "Pago total", 'Otro monto'],
        index=0,
        key=f"pago{idd}"
    )
    if f"init{idd}" not in st.session_state:
        monto=0
        st.session_state[f"init{idd}"]=0
    col1,col2=st.columns(2)
    def show1():
        st.session_state[f"init{idd}"]=1
    with col1:
        monto = (
            cobranza['monto_recalculado_mora']
            if pago == "Pago total"
            else st.number_input(
                "Monto",
                min_value=0.0,
                value=0.0,
                step=1000.0,
                key=f"monto_{idd}"
                , format="%.2f",on_change=show1
            )
            if pago == 'Otro monto'
            else 0.0
        )
    with col2:
        if st.session_state[f"init{idd}"]==1:
            st.write(f"${monto:,.2f}")
        medio_pago = st.selectbox(
            'Medio de pago', 
            ['Seleccione una opción', 'Efectivo', 'Transferencia', 'Mixto'], 
            key=f"medio_{idd}"
        )
    if pago=="Pago total":
        st.write(f'Monto a cobrar: {cobranza['monto_recalculado_mora']:,.2f}')

    registro = 'Pago total' if monto >= cobranza['monto_recalculado_mora'] else 'Pago parcial'


    with st.form(f"registrar_pago{idd}"):
        cobrador = st.selectbox('Cobrador', vendedores, key=f"cobradores_{idd}")
        obs = st.text_input('Observación', key=f'observacion_{idd}')
        submit_button = st.form_submit_button("Registrar")

    if submit_button:
        cobranza['vencimiento'] = str(cobranza['vencimiento'])
        campos = [
            ('cobrador', cobrador),
            ('pago', monto),
            ('estado', registro),
            ('medio de pago', medio_pago),
            ('fecha_cobro', fecha_cobro),
            ('obs', obs)]
        
        for campo, valor in campos:
            save2(cobranza['id'], campo, valor)
        login.cargar_clientes()  
        st.rerun()



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
        save2(cobranza['id'],'estado','En mora')
        st.session_state['cobranzas']=login.load_data_vendedores(url)
        cobranza.fillna('')
        login.historial(st.session_state['cobranzas'].columns.tolist(), cobranza.values.tolist())
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 1
st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')


clientes=st.session_state['clientes']['nombre'].values.tolist()
estados=['Pendiente de pago','En mora','Pago total','Pago parcial']
# Función para mostrar préstamos y cobranzas relacionadas
def display_table_morosos(cobranzas_credito):
    # Crear una copia del DataFrame original
    df = cobranzas_credito    

    if not df.empty:
        for idx, row in df.iterrows():
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
                    if row['estado']!='Pendiente de pago':
                        st.write(f"**Dias de mora**: {row['dias_mora']}")
                        st.write(f"**Monto a pagar**: ${row['mora']:,.2f}")
                with col5:
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
                            registrar(row,idx)
                        with st.popover('No abonó'):
                            no_abono(row)
    else:
        st.warning("No se encontraron resultados.")
def cartones_morosos(prestamo_monton):
    for _, row in prestamo_monton.iterrows():
        with st.container(border=True):
            col1,col2,col3,col4=st.columns(4)
            with col1: 
                st.markdown(f"### {row['nombre']}: {row['id']}")
                st.write(f"📝 **Concepto:** {row['asociado']}")
            with col2:
                st.write(f"📅 **Fecha:** {row['fecha']}")
                st.write(f"💰 **Capital:** {row['capital']}")
            with col3:
                st.write(f"📌 **Cantidad de cuotas:** {row['cantidad']}")
                st.write(f"📆 **Vencimiento:** {row['vence']}")
            with col4:
                st.write(f"📝 **Estado:** {row['estado']}")
                if st.button('ver detalles',key=f'detalles_{row['id']}'):
                    st.session_state['credito']=row
                    st.switch_page('pages/por_credito.py')
            # Filtrar cobranzas relacionadas con este préstamo
            cobranzas_prestamo = cobranzas[cobranzas['prestamo_id'] == row['id']]
            cobranzas_prestamo=cobranzas_prestamo[cobranzas_prestamo['estado']=='En mora']
            display_table_morosos(cobranzas_prestamo)
for _,moroso in morosos.iterrows():
    prestamos_moroso=prestamos[prestamos['nombre']==moroso['nombre']]
    cartones_morosos(prestamos_moroso)