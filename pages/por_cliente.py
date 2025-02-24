import streamlit as st
import login
import pandas as pd
import datetime as dt
import time
login.generarLogin()
if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
    
if st.button("Volver"):
    st.session_state['cliente'] = None
    st.switch_page("pages/clientes.py")
# Verificar si 'cliente' está en session_state
if 'cliente' not in st.session_state :
    st.error("No se ha seleccionado ningún cliente.")
else:
    cliente = st.session_state['cliente']
    vendedores = st.session_state['usuarios']['usuario'].tolist()

    # Cargar los datos de préstamos y cobranzas
    prestamos = st.session_state['prestamos']
    cobranzas = st.session_state['cobranzas']

    # Filtrar préstamos y cobranzas por el cliente seleccionado
    prestamos_cliente = prestamos[prestamos['nombre'] == cliente['nombre']]
    cobranzas_cliente = cobranzas[cobranzas['nombre'] == cliente['nombre']]

    cobranzas_cliente['vencimiento'] = pd.to_datetime(cobranzas_cliente['vencimiento'], format='%d-%m-%Y', errors='coerce')
    prestamos_cliente['fecha'] = pd.to_datetime(prestamos_cliente['fecha'], format='%d-%m-%Y', errors='coerce')


    # Obtener la fecha mínima y máxima de vencimiento, manejando NaT
    primer_cobranza = cobranzas_cliente['vencimiento'].min()
    ultima_cobranza = cobranzas_cliente['vencimiento'].max()

    primer_prestamo = prestamos_cliente['fecha'].min()
    ultimo_prestamo = prestamos_cliente['fecha'].max()

    # Verificar si los valores son NaT antes de aplicar strftime
    primer_cobranza = primer_cobranza.strftime('%d-%m-%Y') if pd.notna(primer_cobranza) else ""
    ultima_cobranza = ultima_cobranza.strftime('%d-%m-%Y') if pd.notna(ultima_cobranza) else ""

    primer_prestamo = primer_prestamo.strftime('%d-%m-%Y') if pd.notna(primer_prestamo) else ""
    ultimo_prestamo = ultimo_prestamo.strftime('%d-%m-%Y') if pd.notna(ultimo_prestamo) else ""

    col1,col2,col3,col4=st.columns(4)
    with col1:
        #primer y ultima cobranza
        st.write(f"primer vencimiento: {primer_cobranza}")
        st.write(f"ultimo vencimiento: {ultima_cobranza}")
        #primer y ultimo prestamo
        st.write(f"primer prestamo: {primer_prestamo}")
        st.write(f"ultimo prestamo: {ultimo_prestamo}")
        
    with col2:
        #capital entregado
        entregado=prestamos_cliente['capital'].sum()
        st.write(f"capital entregado: {entregado}")


        #total de intereses
        mora=cobranzas_cliente[cobranzas_cliente['estado']=='en mora']['mora'].sum()
        st.write(f"total de intereses acumulados: {mora}")

    with col3:
        #total de deuda
        monto_mora=cobranzas_cliente['monto_recalculado_mora'].sum()-cobranzas_cliente['pago'].sum()
        st.write(f"total adeudado: {monto_mora}")

        #total pagado
        pagado=cobranzas_cliente['pago'].sum()
        st.write(f"total pagado: {pagado}")

    # Función para mostrar el nivel de morosidad
    def nivel_de_morosidad():
        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader('Pagados')
                pagados = cobranzas_cliente[cobranzas_cliente['estado'] == 'Pago total']
                if pagados.empty:
                    st.write("No hay pagos registrados.")
                else:
                    st.dataframe(pagados, use_container_width=True)

            with col2:
                st.subheader('Atrasados')
                atrasados = cobranzas_cliente[cobranzas_cliente['estado'] == 'En mora']
                if atrasados.empty:
                    st.write("No hay pagos atrasados.")
                else:
                    st.dataframe(atrasados, use_container_width=True)

            with col3:
                st.subheader('Pendientes')
                pendientes = cobranzas_cliente[cobranzas_cliente['estado'] == 'Pendiente de pago']
                if pendientes.empty:
                    st.write("No hay pagos pendientes.")
                else:
                    st.dataframe(pendientes, use_container_width=True)


    if 'prestamos' not in st.session_state:
        st.session_state["prestamos"] = login.load_data_vendedores(st.secrets['urls']['prestamos'])
    if 'cobranzas' not in st.session_state:
        st.session_state['cobranzas'] = login.load_data_vendedores(st.secrets['urls']['cobranzas'])

    if "mov" not in st.session_state:
        st.session_state["mov"] = login.load_data(st.secrets['urls']['flujo_caja'])



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
    idc = st.secrets['ids']['cobranzas']
    url = st.secrets['urls']['cobranzas']

    def load():
        return login.load_data_vendedores(url)

    def save(id,column,data):#modifica un solo dato
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
            campos = [
                ('cobrador', cobrador),
                ('pago', monto),
                ('estado', registro),
                ('medio de pago', medio_pago),
                ('fecha_cobro', fecha_cobro),
                ('obs', obs)]
            
            for campo, valor in campos:
                save(cobranza['id'], campo, valor)
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
            save(cobranza['id'],'estado','En mora')
            st.session_state['cobranzas']=load()
            cobranza.fillna('')
            login.historial(st.session_state['cobranzas'].columns.tolist(), cobranza.values.tolist())
    if 'pagina_actual' not in st.session_state:
        st.session_state['pagina_actual'] = 1
    st.session_state['cobranzas']['id'] = pd.to_numeric(st.session_state['cobranzas']['id'], errors='coerce').astype('Int64')


    clientes=st.session_state['clientes']['nombre'].values.tolist()
    estados=['Pendiente de pago','En mora','Pago total','Pago parcial']
    # Función para mostrar préstamos y cobranzas relacionadas
    def display_table(cobranzas_credito):
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
    def cartones():
        if prestamos_cliente.empty:
            st.warning("Este cliente no tiene préstamos registrados.")
            return
        col1,col2,col3,col4=st.columns(4)
        with col4:
            if st.button('Recargar datos'):
                login.cargar_clientes()
        for _, row in prestamos_cliente.iterrows():
            with st.container(border=True):
                col1,col2,col3,col4=st.columns(4)
                with col1: 
                    st.markdown(f"### Préstamo ID: {row['id']}")
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
                cobranzas_prestamo = cobranzas_cliente[cobranzas_cliente['prestamo_id'] == row['id']]
                display_table(cobranzas_prestamo)
    # Mostrar información
    nivel_de_morosidad()
    cartones()
