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
    with st.expander('ver morosos'):
        st.subheader("morosos")
        moras=cobranzas[cobranzas['estado']=='En mora']
        cartones_morosos=prestamos[prestamos['id'].isin(moras['prestamo_id'].unique())]
        morosos=df[df['nombre'].isin(cartones_morosos['nombre'].unique())]
        st.dataframe(morosos)



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


