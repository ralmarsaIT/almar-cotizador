import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from st_aggrid import AgGrid, GridUpdateMode,ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

# Configuración de la página
st.set_page_config(layout="wide")

# Creamos un objeto de sesión
session_state = st.session_state

col1,col2=st.columns([1,2.5])
with col1:
    st.image("images/logos2.webp", width=400)
with col2:
    st.title("Cotizador de articulos")

# Lee el archivo CSV
conn = st.connection("gsheets", type=GSheetsConnection)
df          = conn.read(worksheet='Productos')
df_clientes = conn.read(worksheet='Clientes')
df_condvta  = conn.read(worksheet='Condiciones')
df_dolar    = conn.read(worksheet='DolarBNA_hoy',header=None)
dolar_hoy   = df_dolar.iloc[0, 1]
fecha       = df_dolar.iloc[0, 0].replace("/", "_")
#fecha2      = df_dolar.iloc[0, 0]
fecha2 = datetime.now().strftime("%d/%m/%Y")

# Caja de búsqueda
nombres_clientes = df_clientes['Cliente'].dropna().unique().tolist()
descrip_condvta  = df_condvta['Descripcion'].dropna().unique().tolist()

pdfmetrics.registerFont(TTFont('HandelGothic BT', 'fonts/HANDGOTN.TTF'))

# Agrega una nueva columna llamada "categoria_producto"  y guarda las letras del codigo
df['Categoria Producto'] = df.iloc[:, 0].str.extract(r'^([a-zA-Z]*)', expand=False)
# Elimina la columna "categoria_producto" de su posición actual
categoria_producto = df.pop('Categoria Producto')

# Inserta la columna "categoria_producto" en la posición 2
df.insert(1, 'Categoria Producto', categoria_producto)

Vendedor = "ventas@almar.com.ar"
#Vendedor = st.experimental_user ["email"]
st.session_state.reset_filtros = False

col1, col2, col3, col4, col5, col6,col7,col8 = st.columns(8)
cov1,cov2= st.columns(2)
with cov1:
            # Botón para resetear los filtros
            st.markdown("""
            <style>
                /* Aplica estilo a todos los botones de Streamlit */
                .stButton>button {
                    font-size: 40px;            /* Tamaño de la fuente */
                    background-color: #FFFFFF;  /* Fondo blanco */
                    color: #333333;             /* Texto gris oscuro */
                    border: 1px solid #DDDDDD;  /* Borde sutil */
                    padding: 15px 32px;         /* Espaciado alrededor del texto */
                    border-radius: 12px;        /* Bordes redondeados */
                }

                .stButton>button:hover {
                    background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                    color: #FFA500;             /* Naranja para el texto en hover */
                    border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                }

                .stButton>button:active,
                .stButton>button:focus {
                    background-color: #FFFFFF;   
                    color: #FFA500;             
                    border: 1px solid #FFA500;  
                }
            </style>
            """, unsafe_allow_html=True)
if st.button('Resetear filtros'):
        # Resetea la sesión de filtros y selecciona todos los valores por defecto
        st.session_state.reset_filtros = True
        st.session_state.codigo_seleccionado = 'Todos'
        st.session_state.categoria_seleccionada = 'Todos'
        st.session_state.tela_madre_seleccionado = 'Todos'
        st.session_state.tela_seleccionada = 'Todos'
        st.session_state.corte_seleccionado = 'Todos'
        st.session_state.ancho_seleccionado = 'Todos'
        st.session_state.peso_seleccionado = 'Todos'
        # Asigna el dataframe original a la variable df_filtrado
        df_filtrado = df
with col1:
    # Crea un selectbox para seleccionar el código
    codigo_seleccionado = st.selectbox('Filtrar por código', ['Todos'] + df['Codigo'].dropna().unique().tolist(), key='codigo_seleccionado')
    # Si se ha reseteado el filtro, selecciona 'Todos'
    if st.session_state.reset_filtros:
        codigo_seleccionado = 'Todos'

# Filtro por código
if codigo_seleccionado == 'Todos':
    # Si se selecciona 'Todos', asigna el dataframe original a df_codigo
    df_codigo = df
else:
    # Si se selecciona un código específico, filtra el dataframe por ese código
    df_codigo = df.loc[df['Codigo'] == codigo_seleccionado]

# Filtro por categoría
with col2:
    # Crea un selectbox para seleccionar la categoría
    categoria_seleccionada = st.selectbox('Filtrar por categoría', ['Todos'] + df_codigo['Categoria Producto'].dropna().unique().tolist(), key='categoria_seleccionada')
    # Si se ha reseteado el filtro, selecciona 'Todos'
    if st.session_state.reset_filtros:
        categoria_seleccionada = 'Todos'

# Filtro por categoría
if categoria_seleccionada == 'Todos':
    # Si se selecciona 'Todos', asigna el dataframe df_codigo a df_categoria
    df_categoria = df_codigo
else:
    # Si se selecciona una categoría específica, filtra el dataframe por esa categoría
    df_categoria = df_codigo.loc[df_codigo['Categoria Producto'] == categoria_seleccionada]

# Filtro por tela madre
with col3:
    # Crea un selectbox para seleccionar la tela madre
    tela_madre_seleccionado = st.selectbox('Filtrar por Tela Madre', ['Todos'] + df_categoria['Tela Madre'].dropna().unique().tolist(), key='tela_madre_seleccionado')
    # Si se ha reseteado el filtro, selecciona 'Todos'
    if st.session_state.reset_filtros:
        tela_madre_seleccionado = 'Todos'

# Filtro por tela madre
if 'Tela Madre' in df_categoria.columns:
    if tela_madre_seleccionado == 'Todos':
        df_tela_madre = df_categoria
    else:
        df_tela_madre = df_categoria.loc[(df_categoria['Tela Madre'] == tela_madre_seleccionado) | (df_categoria['Tela Madre'].isna())]
else:
    print("Error: La columna 'Tela Madre' no existe en el DataFrame.")
    # Maneja el error o proporciona un valor predeterminado
    df_tela_madre = df_categoria

# Filtro por tela
with col4:
    tela_seleccionada = st.selectbox('Filtrar por tela', ['Todos'] + df_tela_madre['Tela'].dropna().unique().tolist(), key='tela_seleccionada')
    if st.session_state.reset_filtros:
        tela_seleccionada = 'Todos'

# Filtro por tela
if tela_seleccionada == 'Todos':
    df_tela = df_tela_madre
else:
    df_tela = df_tela_madre.loc[df_tela_madre['Tela'] == tela_seleccionada]

# Filtro por corte
with col5:
    # Crea un selectbox para seleccionar el corte
    corte_seleccionado = st.selectbox('Filtrar por corte', ['Todos'] + df_tela['Corte'].dropna().unique().tolist(), key='corte_seleccionado')
    # Si se ha reseteado el filtro, selecciona 'Todos'
    if st.session_state.reset_filtros:
        corte_seleccionado = 'Todos'

# Filtro por corte
if corte_seleccionado == 'Todos':
    # Si se selecciona 'Todos', asigna el dataframe df_tela_madre a df_corte
    df_corte = df_tela
else:
    # Si se selecciona un corte específico, filtra el dataframe por ese corte
    df_corte = df_tela.loc[df_tela['Corte'] == corte_seleccionado]
# Filtro por ancho
with col6:
     # Crea un selectbox para seleccionar el ancho
    ancho_seleccionado = st.selectbox('Filtrar por ancho', ['Todos'] + df_corte['Ancho'].dropna().unique().tolist(), key='ancho_seleccionado')
    if st.session_state.reset_filtros:
        ancho_seleccionado = 'Todos'
#  Si la variable de sesión "reset_filtros" es True, se resetea el valor seleccionado en el selectbox a "Todos"
    if st.session_state.reset_filtros:
        ancho_seleccionado = 'Todos'

#  Se filtra el dataframe según el valor seleccionado en el selectbox de ancho
if ancho_seleccionado == 'Todos':  
    df_ancho = df_corte  # . Si se seleccionó "Todos", se asigna el dataframe original a df_ancho
else:
    df_ancho = df_corte.loc[df_corte['Ancho'] == ancho_seleccionado]  #  Si se seleccionó un valor específico, se filtra el dataframe por ancho

# Filtro por peso
with col7:
    peso_seleccionado = st.selectbox('Filtrar por peso', ['Todos'] + df_ancho['Peso'].dropna().unique().tolist(), key='peso_seleccionado')
    if st.session_state.reset_filtros:
        peso_seleccionado = 'Todos'

# Se filtra el dataframe según el valor seleccionado en el selectbox de peso
if peso_seleccionado == 'Todos':
    df_peso = df_ancho
else:
    df_peso = df_ancho.loc[df_ancho['Peso'] == peso_seleccionado]


# Filtro por color
with col8:
    color_seleccionado = st.selectbox('Filtrar por color', ['Todos'] + df_peso['Color'].dropna().unique().tolist(), key='color_seleccionado')
    if st.session_state.reset_filtros:
        color_seleccionado = 'Todos'

# Filtro por color
if color_seleccionado == 'Todos':
    df_color = df_peso
else:
    df_color = df_peso.loc[df_peso['Color'] == color_seleccionado]

# Asigna el dataframe filtrado final
df_filtrado = df_color
df_filtrado = df_filtrado.loc[:, ['Codigo', 'Articulo', 'Tela Madre', 'Tela', 'Precio/USD', 'PrecioKg/USD', 'Corte', 'Ancho', 'Peso', 'Color']]

# Configura las opciones de la grid
gd = GridOptionsBuilder.from_dataframe(df_filtrado)
gd.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
gd.configure_default_column(editable=False, groupable=True, resizable=True, autoSizeColumns=True)  # Resizable es importante aquí
gd.configure_selection(selection_mode='multiple', use_checkbox=True)
gd.configure_column("Codigo", headerCheckboxSelection = True)
gridoptions = gd.build()
gd.configure_default_column(
    cellStyle={'color': 'black', 'fontWeight': 'bold', 'border': 'none'},
    headerCellStyle={'background': 'white', 'text-align': 'center', 'border': 'none'}
)
gd.configure_grid_options(
    rowStyle={'backgroundColor': 'white'},   
    domLayout='autoHeight',  
    suppressHorizontalScroll=True  
)

filas_seleccionadas = []  # Inicializa la lista vacía
# Almacenar las filas seleccionadas en la variable de sesión    
if 'filas_seleccionadas' not in st.session_state:
    st.session_state.filas_seleccionadas = []

# Cuando los filtros cambian, restaurar las filas seleccionadas
if st.session_state.reset_filtros:
    filas_seleccionadas = st.session_state.filas_seleccionadas
else:
    filas_seleccionadas = []

grid_table = AgGrid(
    df_filtrado,
    gridOptions=gridoptions,
    selected_rows=filas_seleccionadas,                        # Restaurar las filas seleccionadas
    update_mode='MODEL_CHANGED',                              # Permite que se actualicen los cambios
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,  # Ajusta el ancho al contenido
    fit_columns_on_grid_load=False,                           # Desactivar ajuste global al contenedor
  
)

# Cuando el usuario selecciona filas, actualizar la variable de sesión
if grid_table['selected_rows'] is not None:
    selected_rows = grid_table['selected_rows']
    filas_seleccionadas = [fila[0] for fila in selected_rows]
    st.session_state.filas_seleccionadas = filas_seleccionadas

col1,col2,col3= st.columns(3)

with col1:
    tipo_venta = st.selectbox('Tipo de venta', ['Venta por unidad', 'Venta por peso', 'Venta por metro'])
with col2:
    tipo_moneda = st.selectbox('Tipo de moneda', ['Dolar','Peso'])
with col3:
# Selector de múltiples opciones
   nombres_seleccionados = st.selectbox("Seleccione un cliente:", nombres_clientes)

# Filtrar el DataFrame según la selección
if nombres_seleccionados:
    poolresultado = df_clientes[df_clientes['Cliente'] == nombres_seleccionados]
    if poolresultado.empty:
        st.write("No se encontraron clientes con el nombre seleccionado.")
else:
    st.write("Por favor, seleccione un cliente.")

# Almacenar los artículos seleccionados en la variable de sesión
articulo_seleccionado_df = grid_table['selected_rows']
articulo_seleccionado_df = pd.DataFrame(articulo_seleccionado_df)

# Verifica si la lista 'carrito' ya existe en la sesión, si no, inicialízala
if 'carrito' not in st.session_state:
    st.session_state.carrito = pd.DataFrame()  # El carrito inicialmente es un DataFrame vacío

# Función para agregar productos seleccionados al carrito
def agregar_al_carrito(nuevos_articulos):
    if not nuevos_articulos.empty:    # Si hay artículos seleccionados
        # Concatenar los artículos seleccionados al carrito almacenado en la sesión
        st.session_state.carrito = pd.concat([st.session_state.carrito, nuevos_articulos]).drop_duplicates("Codigo").reset_index(drop=True)

# Almacena los artículos seleccionados
articulo_seleccionado_df = pd.DataFrame(grid_table['selected_rows'])


# Definir las columnas
col1, col2, col3 = st.columns([1, 1, 1])  # Col1 ocupa 1 parte, Col2 ocupa 2 partes, Col3 ocupa 1 parte
            
with col1:
            st.markdown("""
            <style>
                /* Aplica estilo a todos los botones de Streamlit */
                .stButton>button {
                    font-size: 40px;            /* Tamaño de la fuente */
                    background-color: #FFFFFF;  /* Fondo blanco */
                    color: #333333;             /* Texto gris oscuro */
                    border: 1px solid #DDDDDD;  /* Borde sutil */
                    padding: 15px 32px;         /* Espaciado alrededor del texto */
                    border-radius: 12px;        /* Bordes redondeados */
                }

                .stButton>button:hover {
                    background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                    color: #FFA500;             /* Naranja para el texto en hover */
                    border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                }

                .stButton>button:active,
                .stButton>button:focus {
                    background-color: #FFFFFF;   
                    color: #FFA500;             
                    border: 1px solid #FFA500;  
                }
            </style>
            """, unsafe_allow_html=True)
if st.button("Añadir al carrito"):
        # Verificar si se han seleccionado nuevos artículos antes de agregar al carrito
    if not articulo_seleccionado_df.empty:
       agregar_al_carrito(articulo_seleccionado_df)

with col2:
    # Mejorar la escritura en la columna 2
    st.write("**Cotización Billete Dólar U.S.A (Tipo Venta BNA):**")
    st.write(f"**Fecha:** {fecha2}")
    st.write(f"**Valor:** ${dolar_hoy:.2f}")

with col3:
    st.write("")  # columna vacía o agregar contenido adicional si lo deseas

# Mantener el contenido del carrito incluso cuando se cambian los filtros o se resetean
if not st.session_state.carrito.empty:
    # Selecciona las columnas necesarias para la cotización del producto según el tipo de venta
    if tipo_venta == 'Venta por unidad':
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','Precio/USD']])
            carrito_df['Cantidad'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/USD", editable=True, type=["numericColumn"],valueFormatter="value.toFixed(3)")  # Formato con 3 decimales
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad','Precio/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['Precio/Pesos'] = st.session_state.carrito['Precio/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','Precio/Pesos']])
            carrito_df['Cantidad'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/Pesos", editable=True, type=["numericColumn"],valueFormatter="value.toFixed(2)")
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad','Precio/Pesos'], columns_to_display='visible')

    elif tipo_venta == 'Venta por peso':
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','PrecioKg/USD']])
            carrito_df['Cantidad Kgs'] = 1 # Inicializa la columna "Kg_vender" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad Kgs", editable=True,cellEditor='agNumberCellEditor')
            carrito_go.configure_column("PrecioKg/USD", editable=True, type=["numericColumn"],valueFormatter="value.toFixed(3)")  # Formato con 3 decimales
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad Kgs','PrecioKg/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['PrecioKg/Pesos'] = st.session_state.carrito['PrecioKg/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','PrecioKg/Pesos']])
            carrito_df['Cantidad Kgs'] = 1  
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad Kgs", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("PrecioKg/Pesos", editable=True, type=["numericColumn"],valueFormatter="value.toFixed(2)")
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad/Kgs','PrecioKg/Pesos'], columns_to_display='visible')

    elif tipo_venta == 'Venta por metro':
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','Precio/USD']])
            carrito_df['Cantidad Mts'] = 1  # Inicializa la columna "Metros_vender" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad Mts", editable=True,cellEditor='agNumberCellEditor')
            carrito_go.configure_column("Precio/USD", editable=True,type=["numericColumn"],valueFormatter="value.toFixed(3)")
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad Mts','Precio/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['Precio/Pesos'] = st.session_state.carrito['Precio/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo','Precio/Pesos']])
            carrito_df['Cantidad Mts'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad Mts", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/Pesos", editable=True,type=["numericColumn"],valueFormatter="value.toFixed(2)")
            carrito_go.configure_columns(['Codigo','Articulo','Cantidad Mts','Precio/Pesos'], columns_to_display='visible')

    carrito_go.configure_default_column(editable=False)
    carrito_go.configure_selection(selection_mode='multiple', use_checkbox=True)
    carrito_go.configure_column("Codigo", headerCheckboxSelection = True)
    carrito_go.configure_column("index", hide=True)
    carrito_go.configure_default_column(
    cellStyle={'color': 'black', 'fontWeight': 'bold', 'border': 'none'},
    headerCellStyle={'background': 'white', 'text-align': 'center', 'border': 'none'},
    autoSizeColumns=True 
    )
    carrito_go.configure_grid_options(
    rowStyle={'backgroundColor': 'white'},
    width='100%', 
    rowHeight=35,        # Aumenta la altura de cada fila
    domLayout='normal',  # Tamaño fijo
    #domLayout='autoHeight',  
    suppressHorizontalScroll=False,
    )
    st.write(f"---------------------------------------------------------------------------------------------------")
    st.title("Cotizador")
    st.write(f"Ingrese la cantidad a cotizar. Puede modificar el precio si lo desea.")
    # Configurar las opciones de edición para el AgGrid
    carrito_lindo = AgGrid(
        st.session_state.carrito,
        gridOptions=carrito_go.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        reload_data=True
    )

    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 40px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 15px 32px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)
            
if not session_state.carrito.empty:
    if st.button("Eliminar"):
            if carrito_lindo['selected_rows'] is not None and not carrito_lindo['selected_rows'].empty:
                # Convertir los artículos seleccionados a un DataFrame
                articulos_seleccionados = pd.DataFrame(carrito_lindo['selected_rows'])
            
                # Filtrar el carrito para eliminar los artículos seleccionados
                st.session_state.carrito = st.session_state.carrito[~st.session_state.carrito['Articulo'].isin(articulos_seleccionados['Articulo'])]
                st.rerun()
            else:
                st.warning("Por favor, selecciona al menos un artículo para eliminar.")
    st.write(f"Marque las filas y presione eliminar si desea quitar articulo/s.")

st.write(f"------------------------------------------------------------------------------------------------------")

# Definir las columnas
col1, col2, col3 = st.columns([1, 1, 1]) 

# Selector de múltiples opciones
with col1:
    condicion_seleccionada = st.selectbox("Seleccione una condicion de pago:", descrip_condvta)
    if condicion_seleccionada:
        poolresultadocond = df_condvta[df_condvta['Descripcion'] == condicion_seleccionada]    
        if poolresultadocond.empty:
             st.write("No se encontraron resultados con la condicion seleccionada.")
    else:
         st.write("Por favor, seleccione una condicion de pago.")

with col2:
    ValidezCot = ['7 dias', '15 dias', '30 dias']
    tiempo_cotizacion = st.selectbox("Seleccione dias de validez de la cotización", ValidezCot)
with col3:
    #radio button para seleccionar si se entrega mercadería en destino
    entrega_destino = st.radio("¿Mercadería se entrega en destino?", ["Sí", "No"])
    if entrega_destino == "Sí":
        st.write("La mercaderia se entregará en el destino.")
    else:
        st.write("La mercaderia se retira de planta.")


# Cálculo del Total a cotizacion
if tipo_venta == 'Venta por unidad' and tipo_moneda == 'Dolar':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)   
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False
        
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "Precio/USD", "Cantidad"]].copy()
                cotiza_df["Precio/USD"] = cotiza_df["Precio/USD"].apply(lambda x: f"{x:.3f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/USD"]) * float(row["Cantidad"]), 3), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'Precio/USD', 'Cantidad', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["Precio/USD"], 
                                             row["Cantidad"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
                    
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )    

            st.session_state.cotizacion_generada = True
        
        if st.session_state.cotizacion_generada:    
            def resetall_filtros():
                # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df


         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación
         
#Fin Unidades/Dolar
elif tipo_venta == 'Venta por unidad' and tipo_moneda == 'Peso':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)                
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "Precio/Pesos", "Cantidad"]].copy()
                cotiza_df["Precio/Pesos"] = cotiza_df["Precio/Pesos"].apply(lambda x: f"{x:.2f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row:round(float(row["Precio/Pesos"]) * float(row["Cantidad"]), 2), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'Precio/Pesos', 'Cantidad', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["Precio/Pesos"], 
                                             row["Cantidad"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
                    
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )

            st.session_state.cotizacion_generada = True #activo la flag que se cotizo
        
        if st.session_state.cotizacion_generada:    
            def resetall_filtros():
                # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df


         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación  
#Fin Unidades/Peso
elif tipo_venta == 'Venta por peso' and tipo_moneda == 'Dolar':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)                
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False

        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad Kgs' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad Kgs'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "PrecioKg/USD", "Cantidad Kgs"]].copy()
                cotiza_df["PrecioKg/USD"] = cotiza_df["PrecioKg/USD"].apply(lambda x: f"{x:.3f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["PrecioKg/USD"]) * float(row["Cantidad Kgs"]), 3), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'PrecioKg/USD', 'Cantidad Kgs', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["PrecioKg/USD"], 
                                             row["Cantidad Kgs"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
                    
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )
            st.session_state.cotizacion_generada = True #activo la flag que se cotizo

        if st.session_state.cotizacion_generada: 
            def resetall_filtros():
                    # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df

         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación
         
#Fin Peso/Dolar
elif tipo_venta == 'Venta por peso' and tipo_moneda == 'Peso':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)                
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False

        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad Kgs' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad Kgs'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "PrecioKg/Pesos", "Cantidad Kgs"]].copy()
                cotiza_df["PrecioKg/Pesos"] = cotiza_df["PrecioKg/Pesos"].apply(lambda x: f"{x:.2f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row:round(float(row["PrecioKg/Pesos"]) * float(row["Cantidad Kgs"]), 2), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'PrecioKg/Pesos', 'Cantidad Kgs', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["PrecioKg/Pesos"], 
                                             row["Cantidad Kgs"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
            
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )
            st.session_state.cotizacion_generada = True #activo la flag que se cotizo
        if st.session_state.cotizacion_generada:    
            def resetall_filtros():
                # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df


         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación  
        
#Fin Peso/Peso
elif tipo_venta == 'Venta por metro' and tipo_moneda == 'Dolar':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)                
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad Mts' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad Mts'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "Precio/USD", "Cantidad Mts"]].copy()
                cotiza_df["Precio/USD"] = cotiza_df["Precio/USD"].apply(lambda x: f"{x:.3f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/USD"]) * float(row["Cantidad Mts"]), 3), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'Precio/USD', 'Cantidad Mts', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["Precio/USD"], 
                                             row["Cantidad Mts"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
                    
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )
            st.session_state.cotizacion_generada = True #activo la flag que se cotizo
        if st.session_state.cotizacion_generada:    
            def resetall_filtros():
                # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df


         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación
#Fin Metro/Dolar
elif tipo_venta == 'Venta por metro' and tipo_moneda == 'Peso':
    st.markdown("""
                <style>
                    /* Aplica estilo a todos los botones de Streamlit */
                    .stButton>button {
                        font-size: 60px;            /* Tamaño de la fuente */
                        background-color: #FFFFFF;  /* Fondo blanco */
                        color: #333333;             /* Texto gris oscuro */
                        border: 1px solid #DDDDDD;  /* Borde sutil */
                        padding: 18px 36px;         /* Espaciado alrededor del texto */
                        border-radius: 12px;        /* Bordes redondeados */
                    }
                    .stButton>button:hover {
                        background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                        color: #FFA500;             /* Naranja para el texto en hover */
                        border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                    }
                    .stButton>button:active,
                    .stButton>button:focus {
                        background-color: #FFFFFF;   
                        color: #FFA500;             
                        border: 1px solid #FFA500;  
                    }
                </style>
                """, unsafe_allow_html=True)                
    if not st.session_state.carrito.empty:

        # Variable para rastrear si se ha generado una cotización
        if 'cotizacion_generada' not in st.session_state:
           st.session_state.cotizacion_generada = False

        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad Mts' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad Mts'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                # Cálculo de cotización
                cotiza_df = carrito_lindo.data[["Codigo", "Articulo", "Precio/Pesos", "Cantidad Mts"]].copy()
                cotiza_df["Precio/Pesos"] = cotiza_df["Precio/Pesos"].apply(lambda x: f"{x:.2f}")
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row:round(float(row["Precio/Pesos"]) * float(row["Cantidad Mts"]), 2), axis=1)
                subtotal = cotiza_df['SubTotal'].sum()
                iva = round(subtotal * 0.21, 2)
                total = round(subtotal + iva, 2)

                # Mostrar resumen en la app
                # Usar st.dataframe para mostrar el DataFrame sin la columna de índice
                st.dataframe(cotiza_df, hide_index=True,use_container_width=True)

                # Alinear el texto a la derecha utilizando HTML dentro de Markdown
                st.markdown(f"<div style='text-align: right;'>SUBTOTAL: ${subtotal:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>I.V.A: ${iva:,.2f}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: right;'>TOTAL COTIZACION: ${total:,.2f}</div>", unsafe_allow_html=True)              
             
                # Config para el pdf
                pagesize     = letter
                leftMargin   = 18  # 1 pulgada   
                rightMargin  = 18  # 1 pulgada
                topMargin    = 180 # 1 pulgada
                bottomMargin = 0   # 1 pulgada           
                  
             # if 'Cantidad' in cotiza_df.columns and not cotiza_df['Cantidad'].isna().any():
             #     if cotiza_df['Cantidad'].apply(lambda x: str(x).replace('.', '', 1).isdigit()).all():           
            data = [
                    ['Codigo', 'Articulo', 'Precio/Pesos', 'Cantidad Mts', 'SubTotal']
                ]
            for index, row in cotiza_df.iterrows():
                                # Asegúrate de que estás accediendo a los valores correctamente
                                data.append([row["Codigo"], 
                                             row["Articulo"], 
                                             row["Precio/Pesos"], 
                                             row["Cantidad Mts"],  
                                             f"$ {row['SubTotal']:,.2f}"])              
                    
            data.append(["", "", "", "SUBTOTAL ", f"$ {subtotal:,.2f}"])
            data.append(["", "", "", "IVA (21%)", f"$ {     iva:,.2f}"])
            data.append(["", "", "", "    TOTAL", f"$ {   total:,.2f}"])                                           
            
            colWidths = [50, 170, 70, 70, 120]
            tablo = Table(data, colWidths=colWidths)

            # Estilo de la tabla
            style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.black),  # Fila de encabezado
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
            tablo.setStyle(style)
            
            cliente_data   = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            condicion_data = str(poolresultadocond.iloc[0,1])
                
            pdf_buffer = BytesIO()

            doc = SimpleDocTemplate(pdf_buffer, pagesize=pagesize, leftMargin=leftMargin, rightMargin=rightMargin,
                                    topMargin=topMargin, bottomMargin=bottomMargin)

            # Crea un estilo de texto
            mi_estilo = ParagraphStyle(
            name='MiEstilo',
            fontSize=8,
            textColor='transparent'
            )
            
            # Crear un párrafo utilizando el estilo personalizado
            parrafo_personalizado = Paragraph("Te", mi_estilo)
            # Función para dibujar en el PDF
            def draw(c, doc):
                width, height = letter
                c.setTitle("Cotización Ricardo Almar e Hijos S.A.")  # Establecer el título

                # Datos Cliente/Cotizacion
                BuenCliente = ("Cliente: " + cliente_codigo + "-" + cliente_data)
                c.drawString(72, 560, BuenCliente)
                if tipo_moneda == "Dolar":
                    MonCotiza = "Dolares"
                else:
                    MonCotiza = f"Pesos considerándose un tipo de cambio de USD 1 = {dolar_hoy}"
                Moneda = ("Cotizacion expresada en: " + MonCotiza)
                c.drawString(72, 540, Moneda)
                                              
                c.drawString(72, 520, "Condición de Pago: " + condicion_data)
                
                VendedorCot = ("Vendedor: " + Vendedor)
                c.drawString(72, 500, VendedorCot) 
                
                if entrega_destino == "Sí":
                    entrega = "entrega en domicilio del cliente"
                else:
                    entrega = "retiro en planta/deposito"
                texto_nota = f"Nota: la presente cotización tiene una validez de {tiempo_cotizacion} y con modalidad {entrega}."
                c.setFont("Helvetica-Bold", 9)
                c.drawString(72, 55, texto_nota)
                
                #c.drawString(72, 500, "Cotización válida por: " + tiempo_cotizacion)
                
                line_y = 575  # Coordenada Y donde quieres que esté la línea
                c.setStrokeColorRGB(0, 0, 0)  # Color negro para la línea
                c.setLineWidth(1)  # Grosor de la línea
                c.line(72, line_y, width - 72, line_y)  # Dibujar línea desde el margen izquierdo (72) hasta el derecho (width - 72)

                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(72, 645, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 630, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 600, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                c.drawString(72, 585, "www.almar.com.ar")
                
                x_pos=400
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 11)
                c.drawString(x_pos, 645, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 630, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 615, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 600, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Envases: (02475) 46-3381 L.Rot.")
                               
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                # Logo de la empresa
                c.drawImage("images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
                ## Título y pretexto
                c.setFont("HandelGothic BT", 16)
                c.drawString(320, 730, "Cotización")

                # Fecha junto a "Cotización"
                c.setFont("Helvetica", 12)
                c.drawString(415, 730, f"Fecha : {fecha2}")

                # Deja un espacio vertical ajustando la coordenada y
                separacion_entre_textos = 10  # Ajusta este valor según el espacio que desees
                c.setFont("HandelGothic BT", 22)
                c.drawString(150, 670, "RICARDO ALMAR e HIJOS S.A.")              
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)

            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
           

            pdf_buffer.seek(0)

            st.markdown("""
                    <style>
                        /* Aplica estilo a todos los botones de descarga de Streamlit */
                        .stDownloadButton>button {
                              font-size: 40px;               /* Tamaño de la fuente */
                              background-color: #FFFFFF;     /* Fondo blanco */
                              color: #333333;                /* Texto gris oscuro */
                              border: 1px solid #DDDDDD;     /* Borde sutil */
                              padding: 18px 36px;            /* Espaciado alrededor del texto */
                              border-radius: 12px;           /* Bordes redondeados */
                        }

                        .stDownloadButton>button:hover {
                            background-color: #FFFFFF;  /* Mantener fondo blanco en hover */
                            color: #FFA500;             /* Naranja para el texto en hover */
                            border: 1px solid #FFA500;  /* Naranja para el borde en hover */
                        }

                         .stDownloadButton>button:active,
                         .stDownloadButton>button:focus {
                            background-color: #FFFFFF;   
                            color: #FFA500              
                            border: 1px solid #FFA500;  
                        }
                    </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                        label="Descargar Cotizacion",
                        data=pdf_buffer,
                        file_name="Cotizacion_Cliente"+ "_" + cliente_codigo + "_" + fecha + ".pdf",
                        mime="application/pdf",
                        key="download_button",
            )
            st.session_state.cotizacion_generada = True #activo la flag que se cotizo
        if st.session_state.cotizacion_generada:    
            def resetall_filtros():
                # Resetea los filtros a sus valores por defecto
                st.session_state.reset_filtros = True
                st.session_state.codigo_seleccionado = 'Todos'
                st.session_state.categoria_seleccionada = 'Todos'
                st.session_state.tela_madre_seleccionado = 'Todos'
                st.session_state.tela_seleccionada = 'Todos'
                st.session_state.corte_seleccionado = 'Todos'
                st.session_state.ancho_seleccionado = 'Todos'
                st.session_state.peso_seleccionado = 'Todos'
                # Asigna el dataframe original al df_filtrado
                df_filtrado = df


         # Botón para limpiar/reiniciar la aplicación
        if st.button("Nueva Cotizacion"):
                   # Limpiar el estado de la sesión y recargar la aplicación
            st.session_state.clear()  # Limpia todo el estado guardado
            resetall_filtros()
            st.rerun()  # Recarga la aplicación 
#Fin Metros/Peso
else:
    st.write("No hay artículos en el carrito.")
# Agrega CSS personalizado para el marcador en la parte inferior
st.markdown(
    """
    <style>
    .footer {
        position: static; 
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 5px;
        text-align: left;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Agrega el marcador
st.markdown("---")
st.markdown('<div class="footer">Desarrollado por Equipo EEST N1: Jonas Fernandez, Ian Favre, Martin Mansilla, Thiago Leonelli y Oficina Almar IT. Rojas,(BA).Argentina.</div>', unsafe_allow_html=True)
