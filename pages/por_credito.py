import streamlit as st
import login
import pandas as pd
import datetime as dt
import time
login.generarLogin()
    
if st.button("Volver"):
    st.session_state['credito'] = None
    st.switch_page("pages/clientes.py")
    
# Verificar si 'cliente' está en session_state
if 'credito' not in st.session_state:
    st.switch_page('inicio.py')
else:
    credito = st.session_state['credito']

    # Cargar los datos de préstamos y cobranzas
    prestamos = login.load_data(st.secrets['urls']['prestamos'])
    cobranzas = login.load_data(st.secrets['urls']['cobranzas'])

    # Filtrar préstamos y cobranzas por el cliente seleccionado
    cobranzas_credito = cobranzas[cobranzas['prestamo_id'] == credito['id']]

    cobranzas_credito['vencimiento'] = pd.to_datetime(cobranzas_credito['vencimiento'], format='%d-%m-%Y', errors='coerce')
    credito['fecha']= pd.to_datetime(credito['fecha'], format='%d-%m-%Y', errors='coerce')

    # Obtener la fecha mínima y máxima de vencimiento, manejando NaT
    primer = credito['fecha']
    ultima = cobranzas_credito['vencimiento'].max()


    # Verificar si los valores son NaT antes de aplicar strftime
    primer = primer.strftime('%d-%m-%Y') if pd.notna(primer) else ""
    ultima = ultima.strftime('%d-%m-%Y') if pd.notna(ultima) else ""
    with st.container(border=True):
        col1,col2,col3,col4=st.columns(4)
        with col1: 
            st.markdown(f"### Préstamo ID: {credito['id']}")
            st.write(f"📝 **Concepto:** {credito['asociado']}")
        with col2:
            st.write(f"📅 **Fecha:** {credito['fecha']}")
            st.write(f"💰 **Capital:** {credito['capital']}")
        with col3:
            st.write(f"📌 **Cantidad de cuotas:** {credito['cantidad']}")
            st.write(f"📆 **Vencimiento:** {credito['vence']}")
        with col4:
            st.write(f"📝 **Estado:** {credito['estado']}")
    with st.container(border=True):
        col1,col2,col3,col4=st.columns(4)
        with col1:
            #primer y ultima cobranza
            st.write(f"Fecha de entrega: {primer}")
            st.write(f"Ultimo vencimiento: {ultima}")

        with col2:
            #capital entregado
            entregado=credito['capital']
            st.write(f"capital entregado: {entregado}")


            #total de intereses
            mora=cobranzas_credito[cobranzas_credito['estado']=='en mora']['mora'].sum()
            st.write(f"total de intereses acumulados: {mora}")

        with col3:
            #total de deuda
            monto_mora=cobranzas_credito['monto_recalculado_mora'].sum()-cobranzas_credito['pago'].sum()
            st.write(f"total adeudado: {monto_mora}")

            #total pagado
            pagado=cobranzas_credito['pago'].sum()
            st.write(f"total pagado: {pagado}")


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
    vendedores = st.session_state['usuarios']['usuario'].tolist()


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

        monto = (
            cobranza['monto_recalculado_mora']
            if pago == "Pago total"
            else st.number_input(
                "Monto",
                min_value=0.0,
                max_value=cobranza['monto_recalculado_mora'],
                value=0.0,
                step=1000.0,
                key=f"monto_{cobranza['id']}"
            )
            if pago == 'Otro monto'
            else 0.0
        )

        registro = 'Pago total' if monto == cobranza['monto_recalculado_mora'] else 'Pago parcial'

        medio_pago = st.selectbox(
            'Medio de pago', 
            ['Seleccione una opción', 'Efectivo', 'Transferencia', 'Mixto'], 
            key=f"medio_{cobranza['id']}"
        )

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
    def display_table():
        # Crear una copia del DataFrame original
        df = cobranzas_credito   
        with st.container(border=True): 
            col1,col2,col3,col4,col5=st.columns(5)
            with col1:
                st.write('Filtros adicionales: ')
            with col2:
                check1= st.checkbox('En mora')
            with col3:
                check2=st.checkbox('Pendientes de pago')
            if check1 and check2:
                df=df[df['estado']=='En mora' or df['estado']=='Pendientes de pago' ]
            elif check1:
                df=df[df['estado']=='En mora']
            elif check2:
                df=df[df['estado']=='Pendientes de pago']
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

###----------------------------------------------------###
    display_table()
    with st.expander('ver pagados'):
        st.dataframe(credito[(credito['estado']=='Pago total') or (credito['estado']=='Pago parcial')])