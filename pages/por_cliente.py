import streamlit as st
import login
import pandas as pd
import datetime as dt
import time
login.generarLogin()
st.title(f"{st.session_state['cliente']['nombre']}")
col1,col2,col3,col4,col5=st.columns(5)
with col1:
    if st.button("Volver"):
        st.session_state['cliente'] = None
        st.switch_page("pages/clientes.py")
with col5:
    if st.button("Reiniciar datos"):
            login.cargar_clientes(forzado=True)
if 'usuario' not in st.session_state:
    st.switch_page('inicio.py')
    

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
    def cartones():
        if prestamos_cliente.empty:
            st.warning("Este cliente no tiene préstamos registrados.")
            return
        col1,col2,col3,col4=st.columns(4)
        with col4:
            if st.button('Recargar datos'):
                login.cargar_clientes(forzado=True)
        for idx, row in prestamos_cliente.iterrows():
            with st.container(border=True):
                col1,col2,col3,col4,col5=st.columns(5)
                with col1: 
                    st.markdown(f"### Préstamo ID: {row['id']}")
                    st.write(f"📝 **Concepto:** {row['asociado']}")
                    st.write(f"📆 **Vencimiento:** {row['vence']}")
                with col2:
                    st.write(f"📅 **Fecha:** {row['fecha']}")
                    st.write(f"💰 **Capital:** {row['capital']}")
                with col3:
                    st.write(f"📌 **Cantidad de cuotas:** {row['cantidad']}")
                    st.write(f"💰 **Monto por cuota:** ${row['monto']:,.2f}")
                with col4:
                    st.write(f"📝 **Estado:** {row['estado']}")
                    estado=st.selectbox('Modificar estado',
                                ["Seleccione una opción", "pendiente", "aceptado", "liquidado", 
                                "al dia", "En mora", "en juicio", "cancelado", "finalizado"],key=f'estado{idx}')
                    if st.button('Guardar'):
                        login.save_data(st.session_state['credito']['id'],'estado',estado)

                with col5:
                    if st.button('ver detalles',key=f'detalles_{row['id']}'):
                        st.session_state['credito']=row
                        st.switch_page('pages/por_credito.py')
                    
                # Filtrar cobranzas relacionadas con este préstamo
                cobranzas_prestamo = cobranzas_cliente[cobranzas_cliente['prestamo_id'] == row['id']]
                df=cobranzas_prestamo
                col1,col2,col3,col4,col5=st.columns(5)
                with col1:
                    st.write('Filtros adicionales: ')
                with col2:
                    check1= st.checkbox('En mora',key=f"check1{idx}")
                with col3:
                    check2=st.checkbox('Pendientes de pago',key=f"check2{idx}")
                if check1 and check2:
                    df=df[df['estado']=='En mora' or df['estado']=='Pendientes de pago' ]
                elif check1:
                    df=df[df['estado']=='En mora']
                elif check2:
                    df=df[df['estado']=='Pendientes de pago']
                login.display_cobranzas(df)
    # Mostrar información
    nivel_de_morosidad()
    cartones()
