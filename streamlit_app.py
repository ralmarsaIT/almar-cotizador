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


# Configuración de la página
st.set_page_config(layout="wide")

# Creamos un objeto de sesión
session_state = st.session_state

col1,col2=st.columns([1,2.5])
with col1:
    st.image("images/logos2.webp", width=400)
with col2:
    st.title("Listado de articulos")

# Lee el archivo CSV
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet='Productos')
df_clientes = conn.read(worksheet='Clientes')
df_dolar = conn.read(worksheet='DolarBNA_hoy',header=None)
dolar_hoy= df_dolar.iloc[0, 1]
fecha = df_dolar.iloc[0, 0].replace("/", "_")
fecha2 = df_dolar.iloc[0, 0]
# Caja de búsqueda
nombres_clientes = df_clientes['Cliente'].dropna().unique().tolist()

pdfmetrics.registerFont(TTFont('HandelGothic BT', 'fonts/HANDGOTN.TTF'))

# Agrega una nueva columna llamada "categoria_producto"  y guarda las letras del codigo
df['Categoria Producto'] = df.iloc[:, 0].str.extract(r'^([a-zA-Z]*)', expand=False)
# Elimina la columna "categoria_producto" de su posición actual
categoria_producto = df.pop('Categoria Producto')

# Inserta la columna "categoria_producto" en la posición 2
df.insert(1, 'Categoria Producto', categoria_producto)

Vendedor = st.experimental_user ["email"]
st.session_state.reset_filtros = False

col1, col2, col3, col4, col5, col6,col7,col8 = st.columns(8)
cov1,cov2= st.columns(2)
with cov1:
    # Botón para resetear los filtros
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
gd.configure_default_column(editable=False, groupable=True, resizable=True)  # Resizable es importante aquí
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
    selected_rows=filas_seleccionadas,  # Restaurar las filas seleccionadas
    update_mode='MODEL_CHANGED',  # Permite que se actualicen los cambios
    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,  # Ajusta el ancho al contenido
    fit_columns_on_grid_load=False,  # Desactivar ajuste global al contenedor
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
    if not nuevos_articulos.empty:  # Si hay artículos seleccionados
        # Concatenar los artículos seleccionados al carrito almacenado en la sesión
        st.session_state.carrito = pd.concat([st.session_state.carrito, nuevos_articulos]).drop_duplicates("Codigo").reset_index(drop=True)

# Almacena los artículos seleccionados
articulo_seleccionado_df = pd.DataFrame(grid_table['selected_rows'])


# Definir las columnas
col1, col2, col3 = st.columns([1, 1, 1])  # Col1 ocupa 1 parte, Col2 ocupa 2 partes, Col3 ocupa 1 parte

with col1:
    if st.button("Añadir al carrito"):
        # Verificar si se han seleccionado nuevos artículos antes de agregar al carrito
        if not articulo_seleccionado_df.empty:
            agregar_al_carrito(articulo_seleccionado_df)

with col2:
    # Mejorar la escritura en la columna 2
    st.write("**Cotización del Dólar U.S.A (Tipo de venta BNA):**")
    st.write(f"**Fecha:** {fecha2}")
    st.write(f"**Dólar hoy:** ${dolar_hoy:.2f}")

with col3:
    st.write("")  # Puedes dejar esta columna vacía o agregar contenido adicional si lo deseas

# Selector de múltiples opciones
   

# Mantener el contenido del carrito incluso cuando se cambian los filtros o se resetean
if not st.session_state.carrito.empty:
    # Selecciona las columnas necesarias para la cotización del producto según el tipo de venta
    if tipo_venta == 'Venta por unidad':
        
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'Precio/USD']])
            carrito_df['Cantidad'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/USD", editable=True)
            carrito_go.configure_columns(['Codigo','Articulo', 'Cantidad', 'Precio/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['Precio/Pesos'] = st.session_state.carrito['Precio/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'Precio/Pesos']])
            carrito_df['Cantidad'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Cantidad", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/Pesos", editable=True)
            carrito_go.configure_columns(['Codigo','Articulo', 'Cantidad', 'Precio/Pesos'], columns_to_display='visible')

    elif tipo_venta == 'Venta por peso':
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'PrecioKg/USD']])
            carrito_df['Kg_vender'] = 1 # Inicializa la columna "Kg_vender" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Kg_vender", editable=True,cellEditor='agNumberCellEditor')
            carrito_go.configure_column("PrecioKg/USD", editable=True)
            carrito_go.configure_columns(['Articulo', 'Kg_vender', 'PrecioKg/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['PrecioKg/Pesos'] = st.session_state.carrito['PrecioKg/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'PrecioKg/Pesos']])
            carrito_df['Kg_vender'] = 1  
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Kg_vender", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("PrecioKg/Pesos", editable=True)
            carrito_go.configure_columns(['Codigo','Articulo', 'Kg_vender', 'PrecioKg/Pesos'], columns_to_display='visible')

    elif tipo_venta == 'Venta por metro':
        if  tipo_moneda=='Dolar':
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'Precio/USD']])
            carrito_df['Metros_vender'] = 1  # Inicializa la columna "Metros_vender" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Metros_vender", editable=True,cellEditor='agNumberCellEditor')
            carrito_go.configure_column("Precio/USD", editable=True)
            carrito_go.configure_columns(['Codigo','Articulo', 'Metros_vender', 'Precio/USD'], columns_to_display='visible')
        else:
            st.session_state.carrito['Precio/Pesos'] = st.session_state.carrito['Precio/USD']*dolar_hoy
            carrito_df = pd.DataFrame(st.session_state.carrito[['Codigo','Articulo', 'Precio/Pesos']])
            carrito_df['Metros_vender'] = 1  # Inicializa la columna "Cantidad" con un valor predeterminado de 1
            carrito_go = GridOptionsBuilder.from_dataframe(carrito_df)
            carrito_go.configure_column("Metros_vender", editable=True,cellEditor='agNumberCellEditor')  # Habilita la edición para la columna "Cantidad"
            carrito_go.configure_column("Precio/Pesos", editable=True)
            carrito_go.configure_columns(['Codigo','Articulo', 'Metros_vender', 'Precio/Pesos'], columns_to_display='visible')

    carrito_go.configure_default_column(editable=False)
    carrito_go.configure_selection(selection_mode='multiple', use_checkbox=True)
    carrito_go.configure_column("Codigo", headerCheckboxSelection = True)
    carrito_go.configure_default_column(
    cellStyle={'color': 'black', 'fontWeight': 'bold', 'border': 'none'},
    headerCellStyle={'background': 'white', 'text-align': 'center', 'border': 'none'},
    autoSizeColumns=True
    )
    carrito_go.configure_grid_options(
    rowStyle={'backgroundColor': 'white'},
    domLayout='autoHeight',  
    suppressHorizontalScroll=True,

    )
    st.title("Cotizador")
    # Configurar las opciones de edición para el AgGrid
    carrito_lindo = AgGrid(
        st.session_state.carrito,
        gridOptions=carrito_go.build(),
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        reload_data=True
    )

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

ValidezCot = ['7 dias', '15 dias', '30 dias']
tiempo_cotizacion = st.selectbox("Seleccione validez de presupuesto de venta", ValidezCot)
        # Cálculo del Total a cotizacion
if tipo_venta == 'Venta por unidad' and  tipo_moneda == 'Dolar' :
    
        if not st.session_state.carrito.empty:
            if st.button("Cotizar"):    
                calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
                if 'Cantidad' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad'].isna().any():
                    st.warning('Llene los campos de cantidad.')
                else:
                    cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "Precio/USD", "Cantidad"]])
                    cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/USD"]) * float(row["Cantidad"]), 3), axis=1)
                    st.write(cotiza_df)
                    total = (cotiza_df['SubTotal']).sum()
                    st.write(f"SubTotal a pagar: ${total:.2f}")



                    #pdf
                    pagesize = letter
                    leftMargin = 18  # 1 pulgada   
                    rightMargin = 18  # 1 pulgada
                    topMargin = 180 # 1 pulgada
                    bottomMargin = 0  # 1 pulgada           
                    
                data = [
                        ['Codigo', 'Articulo', 'Precio/USD', 'Cantidad', 'SubTotal']
                    ]

        
                for index, row in cotiza_df.iterrows():
            # Asegúrate de que estás accediendo a los valores correctamente
                    data.append([row["Codigo"], row["Articulo"], row["Precio/USD"], row["Cantidad"],  row["SubTotal"]])
                data.append(["", "", "", "Total", round(total, 2)])

                    



                colWidths = [60, 160, 65, 60, 120]
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
                



                cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
                cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
                # Luego, utiliza cliente_data para crear la tabla
            

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
        # Crea un párrafo de texto

        # Función para dibujar en el PDF
                def draw(c, doc):

                    
                
                    width, height = letter

            # Dibujar un borde
                    
                    c.drawString(72, 650, Vendedor)
                    BuenCliente = ("Cliente: " + cliente_data)
                    c.drawString(72, 635, BuenCliente)
                    c.drawString(420, 650, "Fecha : " + fecha2)
                    
                    
                    # Agregar "Administración" en negrita
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(72, 600, "ADMINISTRACIÓN")

                    # Dirección: "Francisco Roca 574"
                    c.setFont("Helvetica", 10)
                    c.drawString(72, 585, "Francisco Roca 574")

                    # Ciudad: "(2705) Rojas - Buenos Aires"
                    c.setFont("Helvetica", 10)
                    c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                    # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                    c.setFont("Helvetica", 10)
                    c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                    
                    c.drawString(72, 540, "##########################")
                    
                    
                    x_pos=410
                    # Agregar "PLANTA INDUSTRIAL" en negrita
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                    # Dirección: "Ruta Prov. 45 y Carrasco"
                    c.setFont("Helvetica", 10)
                    c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                    # Ciudad: "(2705) Rojas - Buenos Aires"
                    c.setFont("Helvetica", 10)
                    c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                    # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                    c.setFont("Helvetica", 10)
                    c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                    # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                    c.setFont("Helvetica", 10)
                    c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                    
                    
                    
                    c.setStrokeColor(colors.black)
                    c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                        
                    c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
            

            # Logo de la empresa
                    c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                    
            # Título y pretexto
                    c.setFont("Helvetica-Bold", 11)
                    c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                    c.setFont("HandelGothic BT", 22)
                    c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                    
                    
                    
                    tablo.wrapOn(c, width, height)
                    tablo.drawOn(c, 1 * inch, height - 6   * inch)



                elementos=[parrafo_personalizado]
                doc.build(elementos, onFirstPage=draw)
                




                pdf_buffer.seek(0)
                
                st.download_button(
                    label="Descargar Cotizacion",
                    data=pdf_buffer,
                    file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                    mime="application/pdf"
                )

           
elif tipo_venta == 'Venta por unidad' and  tipo_moneda == 'Peso':
    if not st.session_state.carrito.empty:   
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Cantidad' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Cantidad'].isna().any():
                st.warning('Llene los campos de cantidad.')
            else:
                cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "Precio/Pesos", "Cantidad"]])
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/Pesos"]) * float(row["Cantidad"]), 3), axis=1)
                st.write(cotiza_df)
                total = (cotiza_df['SubTotal']).sum()
                st.write(f"SubTotal a pagar: ${total:.2f}")



                #pdf
                pagesize = letter
                leftMargin = 18  # 1 pulgada   
                rightMargin = 18  # 1 pulgada
                topMargin = 180 # 1 pulgada
                bottomMargin = 0  # 1 pulgada           
                
            data = [
                    ['Codigo', 'Articulo', 'Precio/Pesos', 'Cantidad', 'SubTotal']
                ]

    
            for index, row in cotiza_df.iterrows():
        # Asegúrate de que estás accediendo a los valores correctamente
                data.append([row["Codigo"], row["Articulo"], row["Precio/Pesos"], row["Cantidad"],  row["SubTotal"]])
            data.append(["", "", "", "Total", round(total, 2)])

                



            colWidths = [60, 160, 65, 60, 120]
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
            



            cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            # Luego, utiliza cliente_data para crear la tabla
        

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
    # Crea un párrafo de texto

    # Función para dibujar en el PDF
            def draw(c, doc):

                
            
                width, height = letter

        # Dibujar un borde
                
                c.drawString(72, 650, Vendedor)
                BuenCliente = ("Cliente: " + cliente_data)
                c.drawString(72, 635, BuenCliente)
                c.drawString(420, 650, "Fecha : " + fecha2)
                
                
                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, 600, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 585, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                
                c.drawString(72, 540, "##########################")
                
                
                x_pos=410
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                
                
                
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                    
                c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
        

        # Logo de la empresa
                c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
        # Título y pretexto
                c.setFont("Helvetica-Bold", 11)
                c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                c.setFont("HandelGothic BT", 22)
                c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                
                
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)



            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
            




            pdf_buffer.seek(0)
            
            st.download_button(
                label="Descargar Cotizacion",
                data=pdf_buffer,
                file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                mime="application/pdf"
            )








elif tipo_venta == 'Venta por peso' and tipo_moneda == 'Dolar':
    if not st.session_state.carrito.empty:
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Kg_vender' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Kg_vender'].isna().any():
                st.warning('Llene los campos de Kg_vender.')
            else:
                cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "PrecioKg/USD", "Kg_vender"]])
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["PrecioKg/USD"]) * float(row["Kg_vender"]), 3), axis=1)
                st.write(cotiza_df)
                total = (cotiza_df['SubTotal']).sum()
                st.write(f"SubTotal a pagar: ${total:.2f}")



                #pdf
                pagesize = letter
                leftMargin = 18  # 1 pulgada   
                rightMargin = 18  # 1 pulgada
                topMargin = 180 # 1 pulgada
                bottomMargin = 0  # 1 pulgada           
                
            data = [
                    ['Codigo', 'Articulo', 'PrecioKg/USD', 'Kg_vender', 'SubTotal']
                ]

    
            for index, row in cotiza_df.iterrows():
        # Asegúrate de que estás accediendo a los valores correctamente
                data.append([row["Codigo"], row["Articulo"], row["PrecioKg/USD"], row["Kg_vender"],  row["SubTotal"]])
            data.append(["", "", "", "Total", round(total, 2)])

                



            colWidths = [60, 160, 65, 60, 120]
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
            



            cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            # Luego, utiliza cliente_data para crear la tabla
        

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
    # Crea un párrafo de texto

    # Función para dibujar en el PDF
            def draw(c, doc):

                
            
                width, height = letter

        # Dibujar un borde
                
                c.drawString(72, 650, Vendedor)
                BuenCliente = ("Cliente: " + cliente_data)
                c.drawString(72, 635, BuenCliente)
                c.drawString(420, 650, "Fecha : " + fecha2)
                
                
                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, 600, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 585, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                
                c.drawString(72, 540, "##########################")
                
                
                x_pos=410
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                
                
                
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                    
                c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
        

        # Logo de la empresa
                c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
        # Título y pretexto
                c.setFont("Helvetica-Bold", 11)
                c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                c.setFont("HandelGothic BT", 22)
                c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                
                
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)



            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
            




            pdf_buffer.seek(0)
            
            st.download_button(
                label="Descargar Cotizacion",
                data=pdf_buffer,
                file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                mime="application/pdf"
            )


                
elif tipo_venta == 'Venta por peso' and tipo_moneda == 'Peso':
    if not st.session_state.carrito.empty:
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Kg_vender' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Kg_vender'].isna().any():
                st.warning('Llene los campos de Kg_vender.')
            else:
                cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "PrecioKg/Pesos", "Kg_vender"]])
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["PrecioKg/Pesos"]) * float(row["Kg_vender"]), 3), axis=1)
                st.write(cotiza_df)
                total = (cotiza_df['SubTotal']).sum()
                st.write(f"SubTotal a pagar: ${total:.2f}")



                #pdf
                pagesize = letter
                leftMargin = 18  # 1 pulgada   
                rightMargin = 18  # 1 pulgada
                topMargin = 180 # 1 pulgada
                bottomMargin = 0  # 1 pulgada           
                
            data = [
                    ['Codigo', 'Articulo', 'PrecioKg/Pesos', 'Kg_vender', 'SubTotal']
                ]

    
            for index, row in cotiza_df.iterrows():
        # Asegúrate de que estás accediendo a los valores correctamente
                data.append([row["Codigo"], row["Articulo"], row["PrecioKg/Pesos"], row["Kg_vender"],  row["SubTotal"]])
            data.append(["", "", "", "Total", round(total, 2)])

                



            colWidths = [60, 160, 65, 60, 120]
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
            



            cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            # Luego, utiliza cliente_data para crear la tabla
        

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
    # Crea un párrafo de texto

    # Función para dibujar en el PDF
            def draw(c, doc):

                
            
                width, height = letter

        # Dibujar un borde
                
                c.drawString(72, 650, Vendedor)
                BuenCliente = ("Cliente: " + cliente_data)
                c.drawString(72, 635, BuenCliente)
                c.drawString(420, 650, "Fecha : " + fecha2)
                
                
                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, 600, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 585, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                
                c.drawString(72, 540, "##########################")
                
                
                x_pos=410
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                
                
                
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                    
                c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
        

        # Logo de la empresa
                c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
        # Título y pretexto
                c.setFont("Helvetica-Bold", 11)
                c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                c.setFont("HandelGothic BT", 22)
                c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                
                
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)



            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
            




            pdf_buffer.seek(0)
            
            st.download_button(
                label="Descargar Cotizacion",
                data=pdf_buffer,
                file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                mime="application/pdf"
            )
elif tipo_venta == 'Venta por metro' and tipo_moneda == 'Dolar':
    if not st.session_state.carrito.empty:
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Metros_vender' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Metros_vender'].isna().any():
                st.warning('Llene los campos de Metros_vender.')
            else:
                cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "Precio/USD", "Metros_vender"]])
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/USD"]) * float(row["Metros_vender"]), 3), axis=1)
                st.write(cotiza_df)
                total = (cotiza_df['SubTotal']).sum()
                st.write(f"SubTotal a pagar: ${total:.2f}")



                #pdf
                pagesize = letter
                leftMargin = 18  # 1 pulgada   
                rightMargin = 18  # 1 pulgada
                topMargin = 180 # 1 pulgada
                bottomMargin = 0  # 1 pulgada           
                
            data = [
                    ['Codigo', 'Articulo', 'Precio/USD', 'Metros_vender', 'SubTotal']
                ]

    
            for index, row in cotiza_df.iterrows():
        # Asegúrate de que estás accediendo a los valores correctamente
                data.append([row["Codigo"], row["Articulo"], row["Precio/USD"], row["Metros_vender"],  row["SubTotal"]])
            data.append(["", "", "", "Total", round(total, 2)])

                



            colWidths = [60, 160, 65, 60, 120]
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
            



            cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            # Luego, utiliza cliente_data para crear la tabla
        

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
    # Crea un párrafo de texto

    # Función para dibujar en el PDF
            def draw(c, doc):

                
            
                width, height = letter

        # Dibujar un borde
                
                c.drawString(72, 650, Vendedor)
                BuenCliente = ("Cliente: " + cliente_data)
                c.drawString(72, 635, BuenCliente)
                c.drawString(420, 650, "Fecha : " + fecha2)
                
                
                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, 600, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 585, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                
                c.drawString(72, 540, "##########################")
                
                
                x_pos=410
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                
                
                
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                    
                c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
        

        # Logo de la empresa
                c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
        # Título y pretexto
                c.setFont("Helvetica-Bold", 11)
                c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                c.setFont("HandelGothic BT", 22)
                c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                
                
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)



            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
            




            pdf_buffer.seek(0)
            
            st.download_button(
                label="Descargar Cotizacion",
                data=pdf_buffer,
                file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                mime="application/pdf"
            )


                
elif tipo_venta == 'Venta por metro' and tipo_moneda == 'Peso':
    if not st.session_state.carrito.empty:    
        if st.button("Cotizar"):
            calculo_carrito_lindo = pd.DataFrame(carrito_lindo['data'])
            if 'Metros_vender' not in calculo_carrito_lindo.columns or calculo_carrito_lindo['Metros_vender'].isna().any():
                st.warning('Llene los campos de Metros_vender.')
            else:
                cotiza_df = (carrito_lindo.data[["Codigo", "Articulo", "Precio/Pesos", "Metros_vender"]])
                cotiza_df["SubTotal"] = cotiza_df.apply(lambda row: round(float(row["Precio/Pesos"]) * float(row["Metros_vender"]), 3), axis=1)
                st.write(cotiza_df)
                total = (cotiza_df['SubTotal']).sum()
                st.write(f"SubTotal a pagar: ${total:.2f}")



                #pdf
                pagesize = letter
                leftMargin = 18  # 1 pulgada   
                rightMargin = 18  # 1 pulgada
                topMargin = 180 # 1 pulgada
                bottomMargin = 0  # 1 pulgada           
                
            data = [
                    ['Codigo', 'Articulo', 'Precio/Pesos', 'Metros_vender', 'SubTotal']
                ]

    
            for index, row in cotiza_df.iterrows():
        # Asegúrate de que estás accediendo a los valores correctamente
                data.append([row["Codigo"], row["Articulo"], row["Precio/Pesos"], row["Metros_vender"],  row["SubTotal"]])
            data.append(["", "", "", "Total", round(total, 2)])

                



            colWidths = [60, 160, 65, 60, 120]
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
            



            cliente_data = str([poolresultado.iloc[0,1]]).replace('["', "").replace('"]', "").replace("['", "").replace("']", "")  # Agrega cada cliente como una lista
            cliente_codigo = str([poolresultado.iloc[0,0]]).replace("[np.float64(", "").replace(".0)]", "")
            # Luego, utiliza cliente_data para crear la tabla
        

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
    # Crea un párrafo de texto

    # Función para dibujar en el PDF
            def draw(c, doc):

                
            
                width, height = letter

        # Dibujar un borde
                
                c.drawString(72, 650, Vendedor)
                BuenCliente = ("Cliente: " + cliente_data)
                c.drawString(72, 635, BuenCliente)
                c.drawString(420, 650, "Fecha : " + fecha2)
                
                
                # Agregar "Administración" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(72, 600, "ADMINISTRACIÓN")

                # Dirección: "Francisco Roca 574"
                c.setFont("Helvetica", 10)
                c.drawString(72, 585, "Francisco Roca 574")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(72, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono y Fax: "Tel/Fax: (02475) 46-5585 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(72, 555, "Tel/Fax: (02475) 46-5585 L.Rot.") 
                
                c.drawString(72, 540, "##########################")
                
                
                x_pos=410
                # Agregar "PLANTA INDUSTRIAL" en negrita
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x_pos, 600, "PLANTA INDUSTRIAL")

                # Dirección: "Ruta Prov. 45 y Carrasco"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 585, "Ruta Prov. 45 y Carrasco")

                # Ciudad: "(2705) Rojas - Buenos Aires"
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 570, "(2705) Rojas - Buenos Aires")

                # Teléfono Textil: "Textil: (02475) 46-5586 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 555, "Textil: (02475) 46-5586 L.Rot.")

                # Teléfono Envases: "Envases: (02475) 46-3381 L.Rot."
                c.setFont("Helvetica", 10)
                c.drawString(x_pos, 540, "Envases: (02475) 46-3381 L.Rot.")
                
                
                
                c.setStrokeColor(colors.black)
                c.rect(0.5 * inch, 0.5 * inch, width - 1 * inch, height - 1 * inch)

                    
                c.drawString(72, 620, "Cotizacion valida por: " + tiempo_cotizacion)
        

        # Logo de la empresa
                c.drawImage(".images/Logo.png", 1 * inch, height - 1.7 * inch, width=1 * inch, height=0.9 * inch)
                
        # Título y pretexto
                c.setFont("Helvetica-Bold", 11)
                c.drawString(2.1 * inch, height - 1.54 * inch, "Cotizacion")
                c.setFont("HandelGothic BT", 22)
                c.drawString(2.1 * inch, height - 1.37 * inch, "RICARDO ALMAR E HIJOS S.A")
                
                
                
                tablo.wrapOn(c, width, height)
                tablo.drawOn(c, 1 * inch, height - 6   * inch)



            elementos=[parrafo_personalizado]
            doc.build(elementos, onFirstPage=draw)
            




            pdf_buffer.seek(0)
            
            st.download_button(
                label="Descargar Cotizacion",
                data=pdf_buffer,
                file_name="Cotizacion " + cliente_codigo + " " + fecha + ".pdf",
                mime="application/pdf"
            )

                

else:
    st.write("No hay artículos en el carrito.")


# Footer en Markdown
st.markdown("---")
st.markdown("### Contacto")

st.markdown("- **Emails:** jonasjonifernandez2@gmail.com")
st.markdown("- **Emails:** iansistemas990@gmail.com")
st.markdown("- **Emails:** martinmansilla615@gmail.com")
st.markdown("- **Emails:** thiagodanilocontacto@gmail.com")
st.markdown("---")