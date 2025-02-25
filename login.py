import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
import pandas as pd
import time
# Ocultar el botón de Deploy con CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

def authenticate():
    """Autentica con Google Sheets y guarda el cliente en la sesión."""
    if "gspread_client" not in st.session_state:
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        st.session_state["gspread_client"] = gspread.authorize(creds)

def get_worksheet(sheet_id):
    """Obtiene la hoja de cálculo reutilizando la autenticación."""
    authenticate()  # Asegura que `st.session_state["gspread_client"]` está disponible
    client = st.session_state["gspread_client"]
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.worksheet("Sheet1")

def overwrite_sheet(new_data, sheet_id):
    """
    Sobrescribe toda la hoja de cálculo con los nuevos datos.
    
    :param new_data: Lista de listas, donde cada sublista representa una fila.
    :param sheet_id: ID de la hoja de cálculo en Google Sheets.
    """
    worksheet = get_worksheet(sheet_id)
    worksheet.clear()  # Borra todo el contenido de la hoja
    worksheet.update("A1", new_data)  # Escribe los nuevos datos desde A1


def delete_data(id_value, sheet_id, column_index=1):
    """Elimina todas las filas donde id_value esté presente en la columna especificada."""
    worksheet = get_worksheet(sheet_id)
    
    try:
        cells = worksheet.findall(str(id_value), in_column=column_index)  # Busca en una columna específica
        if not cells:
            return f"ID {id_value} no encontrado en la columna {column_index}."
        
        row_indices = sorted(set(cell.row for cell in cells), reverse=True)
        for row in row_indices:
            worksheet.delete_rows(row)
        
        return f"Se eliminaron {len(row_indices)} fila(s) con ID {id_value}."
    
    except Exception as e:
        return f"Error al eliminar datos: {e}"




def save_data(id_value, column_name, new_value, sheet_id):
    worksheet = get_worksheet(sheet_id)

    # Obtener nombres de las columnas
    col_labels = worksheet.row_values(1)
    if column_name not in col_labels:
        st.error(f"La columna '{column_name}' no existe en la hoja.")
        return

    # Índice de las columnas
    try:
        id_col_index = col_labels.index("ID_Personalizado") + 1  # Cambia el nombre si es diferente
        col_index = col_labels.index(column_name) + 1
    except ValueError:
        st.error("No se encontró la columna de ID o la columna objetivo.")
        return

    # Obtener todas las filas de la columna de ID
    id_column = worksheet.col_values(id_col_index)

    # Buscar la fila correspondiente al ID
    try:
        row_index = id_column.index(str(id_value)) + 1  # +1 porque Google Sheets usa base 1
    except ValueError:
        st.error(f"ID {id_value} no encontrado en la columna 'ID_Personalizado'.")
        return

    # Actualizar la celda
    worksheet.update_cell(row_index, col_index, new_value)
    st.success(f"Valor '{new_value}' guardado en fila {row_index}, columna '{column_name}'.")

def append_data(new_values, sheet_id):
    worksheet = get_worksheet(sheet_id)
    worksheet.append_row(new_values)

def load_data(url):
    return pd.read_excel(url,engine='openpyxl')

def load_data_vendedores(url):
    df=pd.read_excel(url,engine='openpyxl')
    if st.session_state['user_data']['permisos'].iloc[0]!='admin':
        df=df[df['vendedor']==st.session_state['usuario']]
    return df
def load_data1(url):
    return pd.read_csv(url)

def delete(index):#borra una fila completa y acomoda el resto de la hoja para que no quede el espacio en blanco
    delete_data(index,st.secrets['ids']['clientes'])
def save(id,column,data):#modifica un solo dato
    save_data(id,column,data,st.secrets['ids']['clientes'])
def new(data):#añade una columna entera de datos
    append_data(data,st.secrets['ids']['clientes'])




st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])



# Validación simple de usuario y clave con un archivo CSV
def validarUsuario(usuario, clave):
    st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])
    """
    Permite la validación de usuario y clave.
    :param usuario: Usuario ingresado
    :param clave: Clave ingresada
    :return: True si el usuario y clave son válidos, False en caso contrario
    """
    try:
        dfusuarios = st.session_state['usuarios']  # Carga el archivo CSV
        # Verifica si existe un usuario y clave que coincidan
        if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
            return True
    except FileNotFoundError:
        st.error("El archivo 'usuarios.csv' no se encontró.")
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def generarMenu(usuario,permiso):
    st.session_state['usuarios']=load_data1(st.secrets['urls']['usuarios'])
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            dfusuarios = st.session_state['usuarios']
            dfUsuario = dfusuarios[dfusuarios['usuario'] == usuario]
            nombre = dfUsuario['nombre'].iloc[0]

            # Bienvenida al usuario
            st.write(f"### Bienvenido/a, **{nombre}**")
            st.divider()
            st.page_link("pages/clientes.py", label="Clientes", icon=":material/sell:")
            st.page_link("pages/prestamos.py", label="Préstamos", icon=":material/sell:")

            # Administración
            if permiso=='admin':
                st.page_link('pages/reporte_general.py', label="Reporte General", icon=":material/group:")
            st.subheader("Otros")
            st.page_link('pages/preliminar.py', label="Actualizaciones preliminares", icon=":material/group:")

            # Botón de cierre de sesión
            if st.button("Salir"):
                del st.session_state['usuario']
                st.switch_page('inicio.py')
                

        except FileNotFoundError:
            st.error("El archivo 'usuarios.csv' no se encontró.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")

def guardar_log():
    """
    Registra el inicio de sesión en una hoja de Google Sheets.
    Guarda la fecha y hora en la primera columna y el usuario en la segunda.
    """
    worksheet = get_worksheet(st.secrets['ids']['historial'])  # Asegúrate de usar la hoja correcta

    # Obtener la fecha y hora actual
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Obtener el usuario actual
    usuario = st.session_state.get("usuario", "Desconocido")

    # Agregar la fila con la estructura: [Fecha, Usuario]
    worksheet.append_row([timestamp, usuario])


def generarLogin():
    # Ocultar el menú y el pie de página de Streamlit
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.session_state['usuarios'] = load_data1(st.secrets['urls']['usuarios'])
    usuarios = st.session_state['usuarios']

    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'], st.session_state['user_data']['permisos'].iloc[0])
    else:
        try:
            with st.form('frmLogin'):
                parUsuario = st.text_input('Usuario')
                parPassword = st.text_input('Password', type='password')
                if st.form_submit_button('Ingresar'):
                    if validarUsuario(parUsuario, parPassword):
                        st.session_state['usuario'] = parUsuario
                        usuario = usuarios[usuarios['usuario'] == st.session_state['usuario']]
                        st.session_state['user_data'] = usuario
                        guardar_log()  # Registrar el inicio de sesión en logs
                        st.rerun()  # Recargar la aplicación inmediatamente después del login exitoso
                    else:
                        st.error("Usuario o clave inválidos")
        except:
            st.switch_page('inicio.py')


from datetime import datetime

def historial(old_values, new_values):
    """
    Registra en una hoja de Google Sheets un cambio en los datos.

    :param old_values: Lista con los valores anteriores.
    :param new_values: Lista con los valores nuevos.
    """
    worksheet = get_worksheet(st.secrets['ids']['historial'])

    # Obtener la cantidad de filas actuales para generar el índice numérico
    existing_data = worksheet.get_all_values()
    index = len(existing_data)  # Nueva fila será una más que las actuales

    # Obtener la fecha y hora actual
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Obtener el usuario actual
    usuario = st.session_state.get("usuario", "Desconocido")

    # Crear las filas con la estructura: [Fecha, Usuario, Índice, Valores...]
    row_old = [timestamp, usuario, index] + old_values
    row_new = [timestamp, usuario, index + 1] + new_values

    # Agregar ambas filas a la hoja
    worksheet.append_row(row_old)
    worksheet.append_row(row_new)
import meta_ediciones
def cargar_clientes(forzado=False):
    try:
        if forzado==True:
            st.session_state["clientes"] = load_data_vendedores(st.secrets['urls']['clientes'])
            st.session_state["cobranzas"] = load_data_vendedores(st.secrets['urls']['cobranzas'])
            st.session_state["prestamos"] = load_data_vendedores(st.secrets['urls']['prestamos'])
        else:
            if "clientes" not in st.session_state:
                st.session_state["clientes"] = load_data_vendedores(st.secrets['urls']['clientes'])
            if "cobranzas" not in st.session_state:
                st.session_state["cobranzas"] = load_data_vendedores(st.secrets['urls']['cobranzas'])
            if "prestamos" not in st.session_state:
                st.session_state["prestamos"] = load_data_vendedores(st.secrets['urls']['prestamos'])
    except:
        pass
    #meta_ediciones.calcular_recargo()


def cargar_reportes(forzado=False):
    try:
        if forzado==True:
            st.session_state["mov"] = load_data(st.secrets['urls']['flujo_caja'])
            st.session_state['repo_cobranzas']=load_data(st.secrets['urls']['repo_cobranzas'])
            st.session_state['comisiones']=load_data(st.secrets['urls']['repo_comision'])
            st.session_state["repo_mensual"] = load_data(st.secrets['urls']['repo_mensual'])
            st.session_state["morosos"] = load_data(st.secrets['urls']['repo_morosos'])
            st.session_state['repo_ventas']=load_data(st.secrets['urls']['repo_ventas'])       
        else:
            if "mov" not in st.session_state:
                st.session_state["mov"] = load_data(st.secrets['urls']['flujo_caja'])
            if 'repo_cobranzas' not in st.session_state:
                st.session_state['repo_cobranzas']=load_data(st.secrets['urls']['repo_cobranzas'])
            if 'comisiones' not in st.session_state:
                st.session_state['comisiones']=load_data(st.secrets['urls']['repo_comision'])
            if "repo_mensual" not in st.session_state:
                st.session_state["repo_mensual"] = load_data(st.secrets['urls']['repo_mensual'])
            if "morosos" not in st.session_state:
                st.session_state["morosos"] = load_data(st.secrets['urls']['repo_morosos'])
            if 'repo_ventas' not in st.session_state:
                st.session_state['repo_ventas']=load_data(st.secrets['urls']['repo_ventas'])
    except:
        pass
#esto estoy usando por ahora para guardar las cobranzas hasta que estudie bien el modulo de gspread
def save_cobb(id_value, column_name, new_value, sheet_id):
        try:
            worksheet = get_worksheet(sheet_id)
            col_labels = worksheet.row_values(1)

            if column_name not in col_labels:
                return
            
            col_index = col_labels.index(column_name) + 1
            id_column_values = worksheet.col_values(1)  # Se asume que la columna "ID" siempre es la primera
            
            if str(id_value) in id_column_values:
                row_index = id_column_values.index(str(id_value)) + 1
                worksheet.update_cell(row_index, col_index, new_value)
        except:
            st.warning('los datos no se guardaron correctamente')
import datetime as dt
# Cargar datos
idcc = st.secrets['ids']['cobranzas']
urlc = st.secrets['urls']['cobranzas']
vendedores =['']
for vendedor in st.session_state['usuarios']['usuario'].tolist():
    vendedores.append(vendedor)
def display_cobranzas(cobranzas_df):

    def save(id,column,data):#modifica un solo dato
        save_cobb(id,column,data,idcc)

    def ingreso(cobranza,descripcion):
        st.session_state["mov"]=load_data(st.secrets['urls']['flujo_caja'])
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
        append_data(mov,st.secrets['ids']['flujo_caja'])


    def registrar(cobranza):
        fecha_cobro = st.selectbox(
            'Fecha de cobro',
            ['Seleccionar fecha', 'Hoy', 'Otra fecha'],
            index=0,
            key=f"vencimientoo{cobranza['id']}"
        )

        fecha_cobro = (
            dt.date.today().strftime("%d-%m-%Y")
            if fecha_cobro == 'Hoy'
            else st.date_input('Fecha del cobro', key=f"cobro{cobranza['id']}").strftime("%d-%m-%Y")
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
        if "init" not in st.session_state:
            monto=0
            st.session_state["init"]=0
        def show1():
            st.session_state["init"]=1
        col1,col2=st.columns(2)
        with col1:
            monto = (
                cobranza['monto_recalculado_mora']
                if pago == "Pago total"
                else st.number_input(
                    "Monto",
                    min_value=0,
                    value=0,
                    step=1000,
                    key=f"monto_{cobranza['id']}"
                ,on_change=show1)
                if pago == 'Otro monto'
                else 0
            )
        with col2:
            if st.session_state['init']==1:
                st.write(f"${monto:,.2f}")

            medio_pago = st.selectbox(
            'Medio de pago', 
            ['Seleccione una opción', 'Efectivo', 'Transferencia', 'Mixto'], 
            key=f"medio_{cobranza['id']}"
            )
            
        registro = 'Pago total' if monto >= cobranza['monto_recalculado_mora'] else 'Pago parcial'


        with st.form(f"registrar_pago{cobranza['id']}"):
            cobrador = st.selectbox('Cobrador', vendedores,placeholder='', key=f"cobradores_{cobranza['id']}")
            obs = st.text_input('Observación', key=f'observacion_{cobranza["id"]}')
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
                save(cobranza['id'], campo, valor)
            cargar_clientes(forzado=True) 
            st.rerun()



    def registrar_moroso(cobranza):
        morosos=load_data(st.secrets['urls']['repo_morosos'])
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
        append_data(moroso,st.secrets['ids']['repo_morosos'])

    def no_abono(cobranza):
        import numpy as np
        with st.form(f'no abono{cobranza['id']}'):
            st.text_input('obs',key=f"no abono_{cobranza['id']}")
            submit_button=st.form_submit_button('registrar')
        if submit_button:
            cobranza['vencimiento'] = str(cobranza['vencimiento'])
            cobranza = cobranza.replace({np.nan: ""}) 
            save(cobranza['id'],'estado','En mora')
            st.session_state['cobranzas']=load_data(urlc)
            cobranza.fillna('')
            historial(st.session_state['cobranzas'].columns.tolist(), cobranza.values.tolist())

    st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')

    cobranzas_df['vencimiento']=cobranzas_df['vencimiento'].dt.strftime('%d-%m-%Y')
    def display_table():
        df=cobranzas_df
        # Crear una copia del DataFrame original  
        with st.container(border=True): 
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
                            st.write(f"**Amortización**: ${float(row['amortizacion']):,.2f}")
                            st.write(f"**Intereses**: ${float(row['intereses']):,.2f}")
                            st.write(f"**IVA**: ${float(row['iva']):,.2f}")

                        with col5:
                            if row['estado']!='Pendiente de pago':
                                st.write(f"**Dias de mora**: {row['dias_mora']}")
                                st.write(f"**Monto a pagar**: ${row['monto_recalculado_mora']:,.2f}")

                        with col6:
                            if not(row['estado'] in ['Pendiente de Pago','En mora']):
                                st.write(f"**Monto Pago**: ${float(row['pago']):,.2f}")
                                st.write(f"**Fecha del pago**: {row['fecha_cobro']}")
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
    display_table()